import os
import shutil
import json
import pandas as pd
from pdf2image import convert_from_path
import dashscope
from dashscope import MultiModalConversation

# ================= 配置区 =================
# 1. 设置阿里云 API Key
dashscope.api_key = "sk-06f89b86d978492686de2224814ee1ba"

# 2. 设置文件夹路径
INPUT_PDF_DIR = r"C:\Users\Arno\Desktop\External_database_organization\databaseAfterSplit"  # 存放原始 PDF 的文件夹
OUTPUT_CSV_DIR = "./output_csv"  # CSV 输出文件夹
OUTPUT_PDF_DIR = "./output_pdf"  # 处理后 PDF 输出文件夹
POPPLER_PATH = r"C:\Users\Arno\Desktop\External_database_organization\supportRely\poppler-25.12.0\Library\bin"

# 如果文件夹不存在则创建
os.makedirs(OUTPUT_CSV_DIR, exist_ok=True)
os.makedirs(OUTPUT_PDF_DIR, exist_ok=True)
# ==========================================

def pdf_to_first_page_half_images(pdf_path):
    """将 PDF 第一页按中线分成左/右两张图片用于视觉识别"""
    try:
        images = convert_from_path(
            pdf_path,
            first_page=1,
            last_page=1,
            poppler_path=POPPLER_PATH,
        )
        page_image = images[0]
        width, height = page_image.size
        mid_x = width // 2

        # 从页面中心垂直切分：左半页和右半页
        left_image = page_image.crop((0, 0, mid_x, height))
        right_image = page_image.crop((mid_x, 0, width, height))

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        safe_base_name = "".join([c if c.isalnum() else "_" for c in base_name])
        left_image_path = f"temp_vlm_left_{safe_base_name}.jpg"
        right_image_path = f"temp_vlm_right_{safe_base_name}.jpg"

        left_image.save(left_image_path, "JPEG")
        right_image.save(right_image_path, "JPEG")
        return left_image_path, right_image_path
    except Exception as e:
        print(f"PDF 转换失败: {pdf_path}, 错误: {e}")
        return None, None

def _call_qwen_json(image_path, prompt):
    """调用 Qwen2-VL 并尝试解析为 JSON"""

    messages = [
        {
            "role": "user",
            "content": [
                {"image": f"file://{os.path.abspath(image_path)}"},
                {"text": prompt}
            ]
        }
    ]

    response = MultiModalConversation.call(model='qwen-vl-max', messages=messages)

    if response.status_code == 200:
        content = response.output.choices[0].message.content
        # content 可能是字符串或列表，统一为字符串后再处理
        if isinstance(content, list):
            content = "\n".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        # 尝试清理可能出现的 Markdown 标记
        clean_content = str(content).replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean_content)
        except json.JSONDecodeError:
            print(f"JSON 解析失败: {content}")
            return None
    else:
        print(f"API 调用错误: {response.code} - {response.message}")
        return None

def extract_main_name_from_left(left_image_path):
    """仅从左侧顶部蓝色标题条提取一个完整件名（主标题+处理信息）"""
    try:
        from PIL import Image
        image = Image.open(left_image_path)
        width, height = image.size
        # 标题条通常在页面顶部，扩大截取高度以覆盖第二行处理信息
        title_region = image.crop((0, 0, width, max(1, int(height * 0.30))))
        # 放大标题区，提升小字号处理信息行识别稳定性
        title_region = title_region.resize(
            (title_region.width * 2, title_region.height * 2),
            Image.Resampling.LANCZOS,
        )
        temp_title_path = left_image_path.replace('.jpg', '_title.jpg')
        title_region.save(temp_title_path, 'JPEG')
    except Exception as e:
        print(f"标题区域裁剪失败: {e}")
        return None

    prompt = (
        "你是工业目录标题提取助手。请从顶部蓝色标题条提取完整件名。\n"
        "规则：\n"
        "1. 只输出一个件名。\n"
        "2. 件名必须由两部分组成并拼接：\n"
        "   A. 第一行最大黑色主标题（例如：定位销孔顶料型凸模）\n"
        "   B. 紧挨主标题下方的处理信息行（例如：固定块配合加工已完成・RW涂覆处理・RX涂覆处理）\n"
        "3. 输出格式必须是：A－B（中间用全角短横线‘－’连接，只出现一次）。\n"
        "4. B 必须尽量完整保留‘固定块配合加工已完成’及涂覆处理词（如 DICOAT、TiCN、WPC、HW、HX、RW、RX 等）。\n"
        "5. 忽略‘产品数据’、图标、页码、编号、无关说明文字。\n"
        "6. 去掉首尾多余的横线或空格；只允许中文与常见处理代号。\n"
        "7. 如果无法识别 A 或 B，返回空字符串。\n"
        "请严格输出 JSON，不要 Markdown：\n"
        '{"name": "件名"}'
    )

    try:
        result = _call_qwen_json(temp_title_path, prompt)
    finally:
        if os.path.exists(temp_title_path):
            os.remove(temp_title_path)

    if not isinstance(result, dict):
        return None
    name = (result.get("name") or "").strip()
    # 统一清理首尾噪声横线，避免文件名出现重复连接符
    name = name.strip("-－—_ ")
    name = name.replace(" -- ", "－").replace("-", "－")
    if not name:
        return None
    return name

def extract_side_data(image_path, side):
    """从单侧页面提取 Catalog Type 与追加工 Code，不提取件名"""
    side_desc = "左半边" if side == "left" else "右半边"
    prompt = (
        "你是工业目录数据提取助手。请观察这张图片并提取数据：\n"
        f"0. 这是一页文档的{side_desc}，仅提取这张图中的数据。\n"
        "1. 提取 Catalog No. 区块中 Type 列所有值。如果没有Type，就只提取Catalog No.下的所有值。\n"
            "a. 注意不要提取页眉页脚上的Catalog No。\n"
            "b. 提取时注意'-'的提取，不要缺失。\n"
            "c. 读取时可能会有重复的，进行去重，删除时删除后出现的值，但是保留空位。\n"
        "2. 提取追加工区块中 Code 列所有值（蓝色加粗字）。\n"
            "a. 追加工的内容整体单独拿出一行来储存，不要在每个值后面都添加一遍。\n"
            "b. 追加工的内容每个值单独成列"
        "3. 不要提取件名，不要输出说明文字。\n"
        "4. 若某项不存在，返回空数组。\n"
        "5. 输出案例如下：\n"
        ",追加工,RLC, ","PC, ","BC,"," YC, ","PKC, ","PKV, ","SC, ","LC, ","WKD, ","UK,", "RTC \n"
        "Catalog No.,"
        "B-WKSTAS,"
        "B-WKSTAL,"
        "B-WKTPAS,"
        "B-WKTPAL,"
        "请严格输出 JSON，不要 Markdown：\n"
        '{"catalog_types": ["A", "B"], "additional_codes": ["LKC", "LJ2"]}'
    )
    result = _call_qwen_json(image_path, prompt)
    if not isinstance(result, dict):
        return {"catalog_types": [], "additional_codes": []}
    return {
        "catalog_types": result.get("catalog_types", []) or [],
        "additional_codes": result.get("additional_codes", []) or [],
    }

def unique_keep_order(values):
    seen = set()
    out = []
    for value in values:
        v = str(value).strip()
        if not v or v in seen:
            continue
        seen.add(v)
        out.append(v)
    return out

def main():
    results_by_item = {}

    # 遍历文件夹下的 PDF
    files = [f for f in os.listdir(INPUT_PDF_DIR) if f.lower().endswith('.pdf')]
    
    if not files:
        print("未在目录中找到 PDF 文件。")
        return

    for filename in files:
        pdf_path = os.path.join(INPUT_PDF_DIR, filename)
        print(f"\n--- 正在处理: {filename} ---")

        # 1. PDF 转图片并按中线切分左右两侧
        left_image, right_image = pdf_to_first_page_half_images(pdf_path)
        if not left_image or not right_image:
            continue

        main_name = None
        left_data = {"catalog_types": [], "additional_codes": []}
        right_data = {"catalog_types": [], "additional_codes": []}
        try:
            # 2. 只从左侧标题条提取一个件名；再分别提取左右两侧数据
            main_name = extract_main_name_from_left(left_image)
            left_data = extract_side_data(left_image, side="left")
            right_data = extract_side_data(right_image, side="right")
        finally:
            # 删除临时图片
            for temp_image in [left_image, right_image]:
                if temp_image and os.path.exists(temp_image):
                    os.remove(temp_image)

        if not main_name:
            print(f"跳过：未识别到 {filename} 的主件名。")
            continue

        all_catalog_types = unique_keep_order(
            left_data.get("catalog_types", []) + right_data.get("catalog_types", [])
        )
        all_additional_codes = unique_keep_order(
            left_data.get("additional_codes", []) + right_data.get("additional_codes", [])
        )

        codes_str = ", ".join(all_additional_codes)
        if main_name not in results_by_item:
            results_by_item[main_name] = []

        if all_catalog_types:
            for catalog_type in all_catalog_types:
                results_by_item[main_name].append({
                    "Catalog No.": catalog_type,
                    "追加工": codes_str,
                })
        else:
            results_by_item[main_name].append({
                "Catalog No.": "",
                "追加工": codes_str,
            })

        copy_pdf_for_item(pdf_path, main_name)
        print(f"成功：从 {filename} 提取 1 个件名。")

    # 6. 导出 CSV 报告（按件名单独输出）
    if results_by_item:
        for name, rows in results_by_item.items():
            safe_name = "".join([c for c in name if c not in r'\/:*?"<>|'])
            csv_path = os.path.join(OUTPUT_CSV_DIR, f"{safe_name}.csv")
            df = pd.DataFrame(rows)
            df.to_csv(csv_path, index=False, encoding="utf_8_sig")
        print("\n任务完成！CSV 已按件名输出。")

def copy_pdf_for_item(pdf_path, item_name):
    safe_name = "".join([c for c in item_name if c not in r'\/:*?"<>|'])
    target_path = os.path.join(OUTPUT_PDF_DIR, f"{safe_name}.pdf")
    counter = 1
    while os.path.exists(target_path):
        target_path = os.path.join(OUTPUT_PDF_DIR, f"{safe_name}_{counter}.pdf")
        counter += 1
    shutil.copy2(pdf_path, target_path)

if __name__ == "__main__":
    main()