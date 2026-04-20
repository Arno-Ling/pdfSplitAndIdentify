# 工业产品目录 PDF 智能处理工具集

一套专为工业产品目录设计的 PDF 自动化处理工具，支持 PDF 拆分、AI 智能识别、数据提取和格式转换。

## 📋 目录

- [功能概览](#功能概览)
- [快速开始](#快速开始)
- [工具说明](#工具说明)
  - [PdfSplit.py - PDF 拆分工具](#pdfsplitpy---pdf-拆分工具)
  - [Qwen.py - AI 智能识别工具](#qwenpy---ai-智能识别工具)
  - [JsonConvertCsv.py - 数据格式转换工具](#jsonconvertcsvpy---数据格式转换工具)
- [环境配置](#环境配置)
- [典型工作流程](#典型工作流程)
- [常见问题](#常见问题)

---

## 功能概览

本工具集包含三个核心模块：

| 工具 | 功能 | 适用场景 |
|------|------|---------|
| **PdfSplit.py** | PDF 多模式拆分 | 大型目录按页拆分、章节提取 |
| **Qwen.py** | AI 智能识别与分类 | 自动提取产品信息、智能命名 |
| **JsonConvertCsv.py** | JSON 转 CSV | 数据汇总、报表生成 |

---

## 快速开始

### 环境要求

- Python 3.7+
- Windows / Linux / macOS

### 一键安装依赖

```bash
pip install PyPDF2 pdf2image dashscope pandas pillow
```

### 基础使用流程

```bash
# 1. 拆分 PDF
python PdfSplit.py

# 2. AI 识别与分类
python Qwen.py

# 3. 生成 CSV 报表
python JsonConvertCsv.py
```

---

## 工具说明

### PdfSplit.py - PDF 拆分工具

#### 功能特性

支持三种拆分模式：

1. **按页码范围拆分** - 提取指定页码生成新 PDF
2. **单页拆分** - 每页生成独立 PDF 文件
3. **批量分组拆分** - 按固定页数（如每 10 页）分割

#### 使用方法

**配置文件路径**

编辑 `PdfSplit.py` 文件末尾：

```python
if __name__ == "__main__":
    INPUT_PDF = "你的文件.pdf"  # 修改为实际文件名
    
    # 选择一种拆分方式（取消注释对应行）
    
    # 方式1：按页码范围拆分
    # split_pdf_by_range(INPUT_PDF, "输出文件.pdf", start_page=1, end_page=10)
    
    # 方式2：单页拆分（推荐用于产品目录）
    split_pdf_single_pages(INPUT_PDF, output_folder="databaseAfterSplit")
    
    # 方式3：每 N 页拆分
    # split_pdf_every_n_pages(INPUT_PDF, output_folder="output", chunk_size=10)
```

**运行**

```bash
python PdfSplit.py
```

#### 输出示例

- **单页拆分**：`databaseAfterSplit/第1页.pdf`, `第2页.pdf`, ...
- **范围拆分**：`输出文件.pdf`
- **分组拆分**：`第1-10页.pdf`, `第11-20页.pdf`, ...

---

### Qwen.py - AI 智能识别工具

#### 功能特性

基于阿里云通义千问视觉大模型（Qwen2-VL），实现：

- 自动识别产品件名（含主标题 + 处理信息）
- 提取 Catalog Type 型号列表
- 提取追加工 Code 代码
- 智能重命名 PDF 文件
- 生成结构化 JSON 数据

#### 前置准备

**1. 安装 Poppler（PDF 转图片必需）**

- **Windows**: 
  1. 下载 [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
  2. 解压到任意位置（如 `C:\poppler`）
  3. 记录 `bin` 文件夹路径

- **Linux**: 
  ```bash
  sudo apt-get install poppler-utils
  ```

- **macOS**: 
  ```bash
  brew install poppler
  ```

**2. 获取阿里云 API Key**

1. 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
2. 注册并创建 API Key
3. 确保账户余额充足（按调用次数计费）

#### 配置说明

编辑 `Qwen.py` 配置区：

```python
# ================= 配置区 =================
# 1. 设置阿里云 API Key
dashscope.api_key = "sk-your-api-key-here"

# 2. 设置文件夹路径
INPUT_PDF_DIR = r"C:\path\to\your\pdf\folder"  # 输入 PDF 文件夹
OUTPUT_JSON_DIR = "./output_json"              # JSON 输出目录
OUTPUT_PDF_DIR = "./output_pdf"                # 重命名 PDF 输出目录
POPPLER_PATH = r"C:\poppler\Library\bin"       # Poppler bin 路径
# ==========================================
```

#### 运行

```bash
python Qwen.py
```

#### 输出说明

**1. JSON 数据文件**（`output_json/` 目录）

每个识别的件名生成一个 JSON 文件：

```json
{
  "item_name": "定位销孔顶料型凸模－固定块配合加工已完成・RW涂覆处理",
  "catalog_types": ["SJ", "SJV", "PJ"],
  "additional_codes": ["LKC", "LJ2", "DICOAT"],
  "source_file": "第1页.pdf"
}
```

**2. 重命名的 PDF 文件**（`output_pdf/` 目录）

原文件 `第1页.pdf` → 重命名为 `定位销孔顶料型凸模－固定块配合加工已完成・RW涂覆处理.pdf`

#### 识别逻辑

- **件名提取**：从页面顶部蓝色标题条提取主标题 + 处理信息行
- **型号提取**：识别 Catalog No. 区块的 Type 列
- **代码提取**：识别追加工区块的蓝色加粗 Code 列
- **左右分页处理**：自动将页面按中线切分，分别识别左右两侧数据

---

### JsonConvertCsv.py - 数据格式转换工具

#### 功能特性

将 `Qwen.py` 生成的 JSON 文件转换为 CSV 格式：

- 生成二维矩阵表格（件名 × 追加工代码）
- 为每个件名生成独立 CSV
- 生成汇总报告（包含所有件名）

#### 配置说明

编辑 `JsonConvertCsv.py` 配置区：

```python
# ================= 配置区 =================
INPUT_JSON_DIR = "./output_json"    # JSON 输入目录
OUTPUT_CSV_DIR = "./output_csv"     # CSV 输出目录
# ==========================================
```

#### 运行

```bash
python JsonConvertCsv.py
```

#### 输出示例

**单个件名 CSV**（`output_csv/件名.csv`）

| Catalog No. | LKC | LJ2 | DICOAT |
|-------------|-----|-----|--------|
| SJ          |     |     |        |
| SJV         |     |     |        |
| PJ          |     |     |        |

**汇总报告**（`output_csv/汇总报告.csv`）

| 件名 | Catalog No. | LKC | LJ2 | DICOAT |
|------|-------------|-----|-----|--------|
| 定位销孔顶料型凸模 | SJ |  |  |  |
| 定位销孔顶料型凸模 | SJV |  |  |  |
| 导正销 | A-SJ |  |  |  |

---

## 环境配置

### 依赖库清单

```bash
# PDF 处理
PyPDF2>=3.0.0
pdf2image>=1.16.0
Pillow>=9.0.0

# 数据处理
pandas>=1.5.0

# AI 识别
dashscope>=1.20.0
```

### 系统工具

- **Poppler**（仅 Qwen.py 需要）
  - 用于 PDF 转图片
  - 必须配置正确的 `POPPLER_PATH`

---

## 典型工作流程

### 场景：批量处理工业产品目录

```bash
# 步骤 1：拆分大型 PDF 目录为单页
python PdfSplit.py
# 输出：databaseAfterSplit/第1页.pdf, 第2页.pdf, ...

# 步骤 2：AI 识别并分类
python Qwen.py
# 输出：
#   - output_json/件名.json（结构化数据）
#   - output_pdf/件名.pdf（重命名文件）

# 步骤 3：生成 CSV 报表
python JsonConvertCsv.py
# 输出：
#   - output_csv/件名.csv（单个件名表格）
#   - output_csv/汇总报告.csv（全部数据汇总）
```

---

## 常见问题

### Q1: `PdfSplit.py` 运行无输出？

**解决方案：**
- 检查 `INPUT_PDF` 文件路径是否正确
- 确认已安装 `PyPDF2`：`pip install PyPDF2`
- 确认拆分方法未被注释

### Q2: `Qwen.py` 提示找不到 Poppler？

**解决方案：**
- 确认已下载并解压 Poppler
- 检查 `POPPLER_PATH` 是否指向 `bin` 目录
- 或将 Poppler 的 `bin` 目录添加到系统 PATH，设置 `POPPLER_PATH = None`

### Q3: API 调用失败？

**检查清单：**
- API Key 是否正确配置
- 阿里云账户余额是否充足
- 网络连接是否正常
- 查看控制台错误码详情

### Q4: 识别结果不准确？

**优化建议：**
- 确保 PDF 第一页包含完整产品信息
- 提高 PDF 转图片分辨率（修改 `convert_from_path` 的 `dpi` 参数）
- 根据实际文档格式调整 prompt 提示词
- 检查标题区域裁剪比例（`height * 0.30`）

### Q5: 文件名包含非法字符？

**说明：**
- 代码已自动过滤 `\ / : * ? " < > |` 等非法字符
- 如仍有问题，检查 `safe_name` 变量处理逻辑

### Q6: 处理速度慢？

**原因与优化：**
- AI 识别需调用云端 API，速度取决于网络
- 可考虑多线程处理（注意 API 并发限制）
- PDF 拆分为本地处理，速度较快

---

## 项目结构

```
.
├── PdfSplit.py              # PDF 拆分工具
├── Qwen.py                  # AI 智能识别工具
├── JsonConvertCsv.py        # JSON 转 CSV 工具
├── README.md                # 项目文档
├── Database/                # 原始数据库目录
├── databaseAfterSplit/      # 拆分后 PDF 存放目录
├── output_json/             # JSON 数据输出目录
├── output_pdf/              # 重命名 PDF 输出目录
└── output_csv/              # CSV 报表输出目录
```

---

## 许可说明

本工具仅供学习和内部使用。使用阿里云 API 需遵守其服务条款。

---

## 更新日志

**v1.0** (当前版本)
- 实现 PDF 三种模式拆分
- 实现基于 Qwen2-VL 的智能识别
- 支持 JSON 到 CSV 格式转换
- 支持批量处理和自动重命名
