# PDF 处理工具集

本项目包含两个 Python 工具，用于 PDF 文件的拆分和智能识别处理。

---

## 📋 目录

- [工具1：拆分pdf.py - PDF拆分工具](#工具1拆分pdfpy---pdf拆分工具)
- [工具2：Qwen_T.py - AI智能识别工具](#工具2qwen_tpy---ai智能识别工具)
- [环境配置](#环境配置)
- [常见问题](#常见问题)

---

## 工具1：拆分pdf.py - PDF拆分工具

### 功能介绍

一个轻量级的 PDF 拆分工具，支持三种拆分模式：

1. **按页码范围拆分**：提取指定页码范围生成新PDF
2. **单页拆分**：将PDF的每一页拆分为独立的PDF文件
3. **批量分组拆分**：按固定页数（如每10页）拆分为多个PDF

### 使用说明

#### 1. 安装依赖

```bash
pip install PyPDF2
```

#### 2. 修改配置

打开 `拆分pdf.py`，找到文件末尾的配置区：

```python
if __name__ == "__main__":
    # 修改为你的PDF文件路径
    INPUT_PDF = "导正销.pdf"
    
    # 选择一种拆分方式（取消注释对应行）
    
    # 方式1：按页码范围拆分（例如：提取第295-303页）
    # split_pdf_by_range(
    #     input_pdf_path=INPUT_PDF,
    #     output_pdf_path="all_user.pdf",
    #     start_page=295,
    #     end_page=303
    # )
    
    # 方式2：单页拆分（每页生成一个PDF）
    split_pdf_single_pages(INPUT_PDF, output_folder="databaseAfterSplit")
    
    # 方式3：每N页拆分（例如：每10页一个PDF）
    # split_pdf_every_n_pages(INPUT_PDF, output_folder="pdf_split_10", chunk_size=10)
```

#### 3. 运行脚本

```bash
python 拆分pdf.py
```

### 输出说明

- **方式1**：生成指定文件名的PDF（如 `all_user.pdf`）
- **方式2**：在指定文件夹生成 `第1页.pdf`、`第2页.pdf` 等
- **方式3**：在指定文件夹生成 `第1-10页.pdf`、`第11-20页.pdf` 等

### 使用场景

- 从大型PDF中提取特定章节
- 将产品目录按单页拆分便于分类
- 将长文档按章节数量批量分割

---

## 工具2：Qwen_T.py - AI智能识别工具

### 功能介绍

基于阿里云通义千问视觉大模型（Qwen2-VL）的智能PDF识别工具，专门用于工业产品目录的自动化处理。

**核心功能：**
- 自动识别PDF中的产品分类名称
- 提取蓝色字体标注的材质系列编号
- 根据识别结果自动重命名PDF文件
- 生成CSV报告记录所有提取数据

### 使用说明

#### 1. 安装依赖

```bash
pip install pdf2image dashscope pandas pillow
```

#### 2. 安装 Poppler 工具

**Windows 用户：**

1. 下载 Poppler：https://github.com/oschwartz10612/poppler-windows/releases/
2. 解压到任意位置（如 `C:\Program Files\poppler`）
3. 记录 `bin` 文件夹的完整路径

**或者添加到系统环境变量：**
- 将 poppler 的 `bin` 目录添加到系统 PATH
- 然后在代码中设置 `POPPLER_PATH = None`

#### 3. 配置 API Key

需要阿里云 DashScope API 密钥：

1. 访问：https://dashscope.console.aliyun.com/
2. 注册并获取 API Key
3. 确保账户有足够余额（按调用次数计费）

#### 4. 修改配置

打开 `Qwen_T.py`，修改配置区：

```python
# ================= 配置区 =================
# 1. 设置阿里云 API Key
dashscope.api_key = "你的API密钥"

# 2. 设置文件夹路径
INPUT_PDF_DIR = r"C:\你的PDF文件夹路径"  # 存放原始PDF的文件夹
OUTPUT_DIR = "./dataBaseAfterIdentify"   # 处理后PDF保存位置
CSV_OUTPUT = "material_extraction_report.csv"  # CSV报告文件名
POPPLER_PATH = r"C:\你的poppler\bin路径"  # 或设置为 None
```

#### 5. 运行脚本

```bash
python Qwen_T.py
```

### 输出说明

**生成两类文件：**

1. **重命名的PDF文件**（保存在 `OUTPUT_DIR` 文件夹）
   - 文件名格式：`产品分类名称.pdf`
   - 例如：`顶料型凸模.pdf`、`导正销.pdf`

2. **CSV报告**（`material_extraction_report.csv`）
   - 包含字段：
     - 原文件名
     - 提取产品大类
     - 材质系列编号
     - 保存路径

### 识别示例

**输入：** `产品目录_001.pdf`

**识别结果：**
- 产品大类：顶料型凸模
- 材质系列：SJ, SJV, PJ, A-SJ

**输出：**
- 重命名为：`顶料型凸模.pdf`
- CSV记录：`产品目录_001.pdf | 顶料型凸模 | SJ, SJV, PJ, A-SJ | ./dataBaseAfterIdentify/顶料型凸模.pdf`

### 使用场景

- 批量整理工业产品目录PDF
- 自动提取产品分类和型号信息
- 建立产品数据库索引
- 标准化文件命名规范

---

## 环境配置

### Python 版本要求

- Python 3.7 或更高版本

### 完整依赖安装

```bash
# 拆分工具依赖
pip install PyPDF2

# AI识别工具依赖
pip install pdf2image dashscope pandas pillow
```

### 系统工具

- **Poppler**（仅 Qwen_T.py 需要）
  - Windows: 下载并配置路径
  - Linux: `sudo apt-get install poppler-utils`
  - macOS: `brew install poppler`

---

## 常见问题

### Q1: 拆分pdf.py 运行没有反应？

**A:** 检查以下几点：
- 确认 `if __name__ == "__main__":` 没有被注释
- 确认 PDF 文件路径正确
- 确认已安装 PyPDF2：`pip install PyPDF2`

### Q2: Qwen_T.py 提示找不到 poppler？

**A:** 两种解决方案：
1. 安装 poppler 并在代码中指定正确的 `POPPLER_PATH`
2. 将 poppler 的 bin 目录添加到系统 PATH，然后设置 `POPPLER_PATH = None`

### Q3: API 调用失败？

**A:** 检查：
- API Key 是否正确
- 阿里云账户是否有余额
- 网络连接是否正常
- 查看错误信息中的具体错误码

### Q4: 识别结果不准确？

**A:** 可以尝试：
- 确保 PDF 第一页包含产品信息
- 检查 PDF 图片质量是否清晰
- 修改 prompt 提示词使其更符合你的文档格式
- 使用更高分辨率转换 PDF（修改 `convert_from_path` 的 dpi 参数）

### Q5: 文件名包含非法字符？

**A:** 代码已自动过滤以下字符：`\ / : * ? " < > |`
如果仍有问题，检查 `safe_category` 变量的处理逻辑。

### Q6: 处理大量PDF时速度慢？

**A:** 
- AI识别工具需要调用云端API，速度取决于网络和API响应
- 可以考虑添加多线程处理（需要注意API并发限制）
- 拆分工具是本地处理，速度较快

---

## 工作流程建议

**典型使用流程：**

1. **第一步**：使用 `拆分pdf.py` 将大型PDF目录按单页拆分
   ```bash
   python 拆分pdf.py
   ```

2. **第二步**：使用 `Qwen_T.py` 对拆分后的PDF进行智能识别和分类
   ```bash
   python Qwen_T.py
   ```

3. **第三步**：查看生成的CSV报告，验证识别结果

---

## 技术支持

如遇到问题，请检查：
1. Python 版本和依赖库是否正确安装
2. 文件路径是否使用绝对路径或正确的相对路径
3. API Key 和网络连接状态
4. 查看控制台输出的错误信息

---

## 更新日志

- **v1.0** - 初始版本
  - 实现PDF拆分功能
  - 实现AI智能识别功能
  - 支持批量处理和自动重命名

---

## 许可说明

本工具仅供学习和内部使用，使用阿里云API需遵守其服务条款。
