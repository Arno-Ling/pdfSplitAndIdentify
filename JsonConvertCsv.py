# -*- coding: utf-8 -*-
"""
JSON 转 CSV 转换工具
将 Qwen_T.py 生成的 JSON 文件转换为 CSV 格式
"""

import os
import json
import pandas as pd
from pathlib import Path

# ================= 配置区 =================
INPUT_JSON_DIR = "./output_json"    # JSON 文件输入目录
OUTPUT_CSV_DIR = "./output_csv"     # CSV 文件输出目录

# 如果输出目录不存在则创建
os.makedirs(OUTPUT_CSV_DIR, exist_ok=True)
# ==========================================

def load_json_file(json_path):
    """加载 JSON 文件"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取 JSON 文件失败: {json_path}, 错误: {e}")
        return None

def convert_json_to_csv_matrix(json_data):
    """将 JSON 数据转换为二维矩阵 CSV 格式（空白单元格）"""
    if not json_data:
        return None
    
    catalog_types = json_data.get("catalog_types", [])
    additional_codes = json_data.get("additional_codes", [])
    
    if not catalog_types and not additional_codes:
        return None
    
    # 创建二维矩阵数据
    # 第一列是 Catalog No.，后续列是各个追加工代码
    # 单元格留空表示该型号支持该追加工
    matrix_data = []
    
    # 如果有 catalog_types，每个类型作为一行
    if catalog_types:
        for catalog_type in catalog_types:
            row = {"Catalog No.": catalog_type}
            # 为每个追加工代码创建一列，值为空白
            for code in additional_codes:
                row[code] = ""
            matrix_data.append(row)
    else:
        # 如果没有 catalog_types，创建一个空行
        row = {"Catalog No.": ""}
        for code in additional_codes:
            row[code] = ""
        matrix_data.append(row)
    
    return matrix_data

def convert_single_json_to_csv(json_path):
    """转换单个 JSON 文件为 CSV（二维矩阵格式）"""
    # 加载 JSON 数据
    json_data = load_json_file(json_path)
    if not json_data:
        return False
    
    # 转换为二维矩阵格式
    matrix_data = convert_json_to_csv_matrix(json_data)
    if not matrix_data:
        print(f"跳过空数据文件: {json_path}")
        return False
    
    # 生成 CSV 文件名
    json_filename = Path(json_path).stem
    csv_path = os.path.join(OUTPUT_CSV_DIR, f"{json_filename}.csv")
    
    # 创建 DataFrame 并保存为 CSV
    try:
        df = pd.DataFrame(matrix_data)
        # 确保 Catalog No. 列在第一列
        cols = ["Catalog No."] + [col for col in df.columns if col != "Catalog No."]
        df = df[cols]
        df.to_csv(csv_path, index=False, encoding="utf_8_sig")
        print(f"转换成功: {json_filename}.json → {json_filename}.csv")
        return True
    except Exception as e:
        print(f"CSV 保存失败: {csv_path}, 错误: {e}")
        return False

def convert_all_json_to_csv():
    """批量转换所有 JSON 文件为 CSV"""
    if not os.path.exists(INPUT_JSON_DIR):
        print(f"错误: JSON 输入目录不存在: {INPUT_JSON_DIR}")
        return 0
    
    # 获取所有 JSON 文件
    json_files = [f for f in os.listdir(INPUT_JSON_DIR) if f.lower().endswith('.json')]
    
    if not json_files:
        print(f"未在目录中找到 JSON 文件: {INPUT_JSON_DIR}")
        return 0
    
    print(f"找到 {len(json_files)} 个 JSON 文件，开始转换...")
    print("=" * 50)
    
    success_count = 0
    
    for json_filename in json_files:
        json_path = os.path.join(INPUT_JSON_DIR, json_filename)
        if convert_single_json_to_csv(json_path):
            success_count += 1
    
    print("=" * 50)
    print(f"转换完成！成功转换 {success_count}/{len(json_files)} 个文件")
    print(f"CSV 文件保存在: {OUTPUT_CSV_DIR}")
    return success_count

def create_summary_csv():
    """创建汇总 CSV 文件（二维矩阵格式，包含所有件名）"""
    if not os.path.exists(INPUT_JSON_DIR):
        return
    
    all_data = []
    json_files = sorted([f for f in os.listdir(INPUT_JSON_DIR) if f.lower().endswith('.json')])
    
    # 收集所有的追加工代码（用于统一列）
    all_codes = set()
    items_data = []
    
    for json_filename in json_files:
        json_path = os.path.join(INPUT_JSON_DIR, json_filename)
        json_data = load_json_file(json_path)
        
        if json_data:
            items_data.append(json_data)
            codes = json_data.get("additional_codes", [])
            all_codes.update(codes)
    
    # 排序追加工代码列
    sorted_codes = sorted(all_codes)
    
    # 为每个件名创建数据行
    for json_data in items_data:
        item_name = json_data.get("item_name", "未知")
        catalog_types = json_data.get("catalog_types", [])
        additional_codes = json_data.get("additional_codes", [])
        
        if catalog_types:
            for catalog_type in catalog_types:
                row = {
                    "件名": item_name,
                    "Catalog No.": catalog_type
                }
                # 为每个追加工代码创建列，如果该件名有此代码则留空，否则为空
                for code in sorted_codes:
                    row[code] = "" if code in additional_codes else ""
                all_data.append(row)
        else:
            # 没有 catalog_types 的情况
            row = {
                "件名": item_name,
                "Catalog No.": ""
            }
            for code in sorted_codes:
                row[code] = "" if code in additional_codes else ""
            all_data.append(row)
    
    if all_data:
        df = pd.DataFrame(all_data)
        # 确保列顺序：件名、Catalog No.、然后是所有追加工代码
        column_order = ["件名", "Catalog No."] + sorted_codes
        df = df[column_order]
        
        summary_path = os.path.join(OUTPUT_CSV_DIR, "汇总报告.csv")
        df.to_csv(summary_path, index=False, encoding="utf_8_sig")
        print(f"汇总报告已生成: {summary_path}")
        print(f"  - 包含 {len(items_data)} 个件名")
        print(f"  - 包含 {len(all_data)} 行数据")
        print(f"  - 包含 {len(sorted_codes)} 个追加工代码列")

def main():
    """主函数"""
    print("=" * 60)
    print("JSON 转 CSV 转换工具")
    print("=" * 60)
    print(f"输入目录: {INPUT_JSON_DIR}")
    print(f"输出目录: {OUTPUT_CSV_DIR}")
    print()
    
    # 批量转换
    convert_all_json_to_csv()
    
    print()
    
    # 创建汇总报告
    print("正在生成汇总报告...")
    create_summary_csv()
    
    print("\n所有转换任务完成！")

if __name__ == "__main__":
    main()