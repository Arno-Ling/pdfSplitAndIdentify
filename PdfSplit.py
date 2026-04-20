from PyPDF2 import PdfReader, PdfWriter
import os

def split_pdf_by_range(input_pdf_path, output_pdf_path, start_page, end_page):
    """
    按页码范围拆分PDF
    :param input_pdf_path: 原PDF路径
    :param output_pdf_path: 输出PDF路径
    :param start_page: 起始页码（从1开始）
    :param end_page: 结束页码（包含）
    """ 
    try:
        # 读取原PDF
        reader = PdfReader(input_pdf_path)
        # 获取总页数
        total_pages = len(reader.pages)
        
        # 校验页码合法性
        if start_page < 1 or end_page > total_pages or start_page > end_page:
            print(f"错误：页码无效！PDF共{total_pages}页")
            return
        
        writer = PdfWriter()
        
        # 循环添加指定页码的页面
        for page_num in range(start_page - 1, end_page):
            writer.add_page(reader.pages[page_num])
        
        # 保存拆分后的PDF
        with open(output_pdf_path, "wb") as f:
            writer.write(f)
        
        print(f"✅ 拆分成功！保存至：{output_pdf_path}")
    
    except FileNotFoundError:
        print("❌ 错误：未找到原PDF文件，请检查路径")
    except Exception as e:
        print(f"❌ 拆分失败：{str(e)}")
def split_pdf_single_pages(input_pdf_path, output_folder="pdf_split_pages"):
    """
    将PDF按单页拆分，每页生成一个独立PDF
    :param input_pdf_path: 原PDF路径
    :param output_folder: 输出文件夹
    """
    try:
        # 创建输出文件夹
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        reader = PdfReader(input_pdf_path)
        total_pages = len(reader.pages)
        
        # 逐页拆分
        for i in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            
            output_path = os.path.join(output_folder, f"第{i+1}页.pdf")
            with open(output_path, "wb") as f:
                writer.write(f)
        
        print(f"✅ 单页拆分完成！共{total_pages}页，保存在：{output_folder}")
    
    except FileNotFoundError:
        print("❌ 错误：未找到原PDF文件，请检查路径")
    except Exception as e:
        print(f"❌ 拆分失败：{str(e)}")
def split_pdf_every_n_pages(input_pdf_path, output_folder="pdf_split_10", chunk_size=10):
    """
    每 chunk_size 页拆分为一个PDF
    """
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        reader = PdfReader(input_pdf_path)
        total_pages = len(reader.pages)

        for start in range(0, total_pages, chunk_size):
            writer = PdfWriter()
            end = min(start + chunk_size, total_pages)

            for i in range(start, end):
                writer.add_page(reader.pages[i])

            output_path = os.path.join(output_folder, f"第{start+1}-{end}页.pdf")
            with open(output_path, "wb") as f:
                writer.write(f)

        print(f"✅ 拆分完成！共{total_pages}页，按{chunk_size}页/份，保存在：{output_folder}")

    except FileNotFoundError:
        print("❌ 错误：未找到原PDF文件，请检查路径")
    except Exception as e:
        print(f"❌ 拆分失败：{str(e)}")

# ====================== 你只需要修改这里 ======================
if __name__ == "__main__":
    INPUT_PDF = "氮气弹簧.pdf"

    # split_pdf_by_range(
    #     input_pdf_path=INPUT_PDF,
    #     output_pdf_path="检查夹具用零件.pdf",
    #     start_page=809,
    #     end_page=816
    # )
    split_pdf_single_pages(INPUT_PDF, output_folder="databaseAfterSplit")
    # split_pdf_every_n_pages(INPUT_PDF, output_folder="pdf_split_10", chunk_size=10)
# ============================================================