# 🏷️ File & Folder Tagger 文件/文件夹标签工具

A cross-platform tagging and renaming tool for files and folders, powered by Python and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).  
基于 Python + CustomTkinter 的文件/文件夹批量标签管理工具，支持图形化操作。

---

## 🌟 Features 功能亮点

- ✅ Bulk tagging / untagging for files & folders  
  支持对文件和文件夹批量添加/移除标签
- ✅ Custom tag format: `_[#tag1,#tag2]`  
  统一格式：以 `#` 开头，小写、单词下划线连接
- ✅ Recursively rename in correct order  
  避免重命名冲突，自动先改子项再改父项
- ✅ Visual filters by tag / file type  
  支持按标签或扩展名筛选列表
- ✅ Usage help, language/theme toggle  
  自带使用说明、主题切换、语言切换（中/英）
- ✅ Smart UI: Ctrl+A select all, scrollable tags  
  支持快捷键 Ctrl+A，全键盘操作友好

---

## 🚀 Getting Started 快速上手

### 🐍 Run with Python（推荐）

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 运行程序：

```bash
python tagger.py
```

---

### 📦 Optionally use `.exe`（可选打包）

此项目可使用 `pyinstaller` 打包为 Windows 可执行文件。**打包后大小大、可能误报毒，请自行判断。**

> ⚠️ 若不放心 `.exe` 文件，请使用原始 Python 源码运行！

---

## 📖 How to Use 使用方法

1. **Select Folder / Files**  
   选择整个文件夹或部分文件  
2. **Add Custom Tag**  
   自定义标签后点“添加自定义标签”  
3. **Click Tag Buttons**  
   点击标签按钮添加/移除标签  
4. **Remove Tags**  
   选中项目 → 点“移除标签”清除所有标签  
5. **Filter & Refresh**  
   使用筛选器筛选列表，必要时刷新  
6. **Theme & Language**  
   右上角可切换深浅色主题与中英文界面  
7. **Usage Button**  
   点击“Usage”按钮可查看操作说明

---

## ⚖️ License 许可证 & 免责声明

This project is licensed under the **MIT License** — free to use, modify, and distribute.

> ⚠️ This project was **entirely generated and structured by AI** (ChatGPT).  
> There is **no author responsible**, no copyright claim, and **no permission needed**.  
> Use at your own risk. You're free to fork, remix, or discard.

---

本项目使用 **MIT 开源许可证**，你可以自由使用、修改、分发，无需授权。

> ⚠️ 本项目 **完全由 AI（ChatGPT）生成**，无任何实际作者主张，无版权争议。  
> 不对任何后果负责，自行判断使用。  
> 欢迎随意拿去用、魔改或丢掉。