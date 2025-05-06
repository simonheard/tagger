#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tagger.py - 跨平台文件/文件夹 名称标签工具 (CustomTkinter)
功能：
1. 选择文件夹，批量添加/移除标签（支持文件 & 目录）
2. 直接选择若干文件，批量添加/移除标签
3. 自动检索已有标签并生成快捷按钮
4. 统一标签规则：以 # 开头，全部小写，单词间用 _
5. 重命名文件/文件夹名，示例：name_[#tag1,#tag2].ext
6. 保留文件原有扩展名，目录无扩展名
7. 自动检测标签字符数，避免超长（可配 MAX_TAG_LENGTH）
8. 去除标签时自动删除 _[...] 整块
9. 支持递归子文件夹批量操作，自动处理重名冲突
10. Ctrl+A 全选 / 鼠标拖拽多选
11. 按 Tag / 类型 筛选列表
12. 主题与语言切换、Usage 弹窗、双语支持、双语报错提示
"""

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from locales import LOCALES

MAX_TAG_LENGTH = 120
TAG_PATTERN = re.compile(r'_\[#([^\]]+)\]$')

class TaggerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # 初始化外观与主题
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        # 默认语言为英文
        self.lang = 'en'
        # 扩展名显示 → 真正扩展名映射
        self.ext_map = {}
        self._build_ui()
        self._update_ui_texts()

    def gettext(self, key):
        """根据当前语言获取文案"""
        return LOCALES[self.lang].get(key, key)

    def _build_ui(self):
        # 窗口基础设置
        self.title(self.gettext('app_title'))
        self.geometry("900x700")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ===== Header：Usage 按钮 + 主题/语言 切换 =====
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header.grid_columnconfigure(0, weight=1)

        # Usage 弹窗按钮
        self.btn_usage = ctk.CTkButton(header, command=self.show_usage)
        self.btn_usage.grid(row=0, column=1, padx=5, sticky="e")

        # 主题切换开关（🌞/🌙）
        self.var_theme = tk.BooleanVar(value=(ctk.get_appearance_mode()=="Dark"))
        self.switch_theme = ctk.CTkSwitch(
            header,
            text="🌞/🌙",
            command=self.toggle_theme,
            variable=self.var_theme,
            onvalue=True,
            offvalue=False
        )
        self.switch_theme.grid(row=0, column=2, padx=5, sticky="e")

        # 语言切换开关（中/EN）
        self.var_lang = tk.BooleanVar(value=False)  # False = English
        self.switch_language = ctk.CTkSwitch(
            header,
            text="EN/中",
            command=self.toggle_language,
            variable=self.var_lang,
            onvalue=True,
            offvalue=False
        )
        self.switch_language.grid(row=0, column=3, padx=5, sticky="e")

        # ===== Main controls =====
        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content.grid_columnconfigure((0,1,2,3), weight=1)
        content.grid_rowconfigure(3, weight=1)

        # 第一行：选择文件夹、选择文件、刷新（带图标）
        self.btn_select_folder = ctk.CTkButton(content, command=self.on_select_folder)
        self.btn_select_folder.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.btn_select_files = ctk.CTkButton(content, command=self.on_select_files)
        self.btn_select_files.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.btn_refresh = ctk.CTkButton(content, command=self.on_refresh)
        self.btn_refresh.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # 第二行：标签过滤、类型过滤
        self.lbl_tag_filter = ctk.CTkLabel(content)
        self.lbl_tag_filter.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.option_tag = ctk.CTkOptionMenu(content, command=self.on_filter_change)
        self.option_tag.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.lbl_type_filter = ctk.CTkLabel(content)
        self.lbl_type_filter.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.option_ext = ctk.CTkOptionMenu(content, command=self.on_filter_change)
        self.option_ext.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # 第三行：全选、自定义标签输入、添加自定义、移除标签
        self.btn_select_all = ctk.CTkButton(content, command=self.on_select_all)
        self.btn_select_all.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.entry_custom = ctk.CTkEntry(content)
        self.entry_custom.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.btn_add_custom = ctk.CTkButton(content, command=self.on_add_custom_tag)
        self.btn_add_custom.grid(row=2, column=2, padx=5, pady=5, sticky="ew")
        self.btn_remove_tags = ctk.CTkButton(content, command=self.on_remove_tags)
        self.btn_remove_tags.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        # 文件列表
        file_frame = ctk.CTkFrame(content)
        file_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=5)
        file_frame.grid_columnconfigure(0, weight=1)
        file_frame.grid_rowconfigure(0, weight=1)
        self.listbox = tk.Listbox(
            file_frame,
            selectmode=tk.EXTENDED,
            activestyle="none",
            highlightthickness=0
        )
        self.listbox.grid(row=0, column=0, sticky="nsew")
        self.listbox.bind("<Control-a>", lambda e: self.on_select_all())
        scrollbar = tk.Scrollbar(file_frame, command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # 标签按钮区（网格 4 列）
        self.tag_frame = ctk.CTkScrollableFrame(content, height=60)
        self.tag_frame.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(0,10))
        for c in range(4):
            self.tag_frame.grid_columnconfigure(c, weight=1)

        # 数据容器
        self.paths = []
        self.filtered_paths = []
        self.tags = []

    def toggle_theme(self):
        mode = 'Dark' if self.var_theme.get() else 'Light'
        ctk.set_appearance_mode(mode)

    def toggle_language(self):
        self.lang = 'zh' if self.var_lang.get() else 'en'
        self._update_ui_texts()

    def show_usage(self):
        modal = ctk.CTkToplevel(self)
        modal.title(self.gettext('usage_button'))
        modal.geometry("600x300")
        lbl = ctk.CTkLabel(modal, text=self.gettext('usage_text'), justify="left")
        lbl.pack(fill="both", expand=True, padx=20, pady=20)
        btn = ctk.CTkButton(modal, text=self.gettext('close'), command=modal.destroy)
        btn.pack(pady=(0,20))

    def _update_ui_texts(self):
        L = LOCALES[self.lang]
        # 窗口标题 & Usage 按钮
        self.title(L['app_title'])
        self.btn_usage.configure(text=L['usage_button'])
        # 第一行按钮
        self.btn_select_folder.configure(text=L['select_folder'])
        self.btn_select_files.configure(text=L['select_files'])
        self.btn_refresh.configure(text=f"{L['refresh']}")
        # 第二行过滤
        self.lbl_tag_filter.configure(text=L['tag_filter'])
        self.detect_tags()
        self.option_tag.configure(values=[L['all']] + self.tags)
        self.option_tag.set(L['all'])
        self.lbl_type_filter.configure(text=L['type_filter'])
        # 构建扩展名下拉
        exts = sorted(set(os.path.splitext(p)[1].lower() or 'folder' for p in self.paths))
        display_exts = [L['all']]
        self.ext_map.clear()
        for e in exts:
            disp = L['folder'] if e=='folder' else e
            display_exts.append(disp)
            self.ext_map[disp] = e
        self.option_ext.configure(values=display_exts)
        self.option_ext.set(L['all'])
        # 第三行按钮
        self.btn_select_all.configure(text=L['select_all'])
        self.entry_custom.configure(placeholder_text=L['custom_tag_placeholder'])
        self.btn_add_custom.configure(text=L['add_custom_tag'])
        self.btn_remove_tags.configure(text=L['remove_tags'])
        # 刷新列表与标签按钮
        self.update_file_list()
        self.update_tag_buttons()

    def scan_folder(self, folder):
        items = []
        for root, dirs, files in os.walk(folder):
            for d in dirs:
                items.append(os.path.normpath(os.path.join(root, d)))
            for f in files:
                items.append(os.path.normpath(os.path.join(root, f)))
        return items

    def detect_tags(self):
        tags = set()
        for p in self.paths:
            name = os.path.splitext(os.path.basename(p))[0]
            m = TAG_PATTERN.search(name)
            if m:
                for t in m.group(1).split(','):
                    t = t.strip()
                    if t:
                        tags.add('#' + t.lstrip('#').lower())
        self.tags = sorted(tags)

    def update_file_list(self):
        L = LOCALES[self.lang]
        tag_sel = self.option_tag.get()
        ext_disp = self.option_ext.get()
        self.filtered_paths = []
        for p in self.paths:
            name = os.path.splitext(os.path.basename(p))[0]
            has_tag = (tag_sel == L['all']) or (tag_sel in name)
            ext = os.path.splitext(p)[1].lower() or 'folder'
            if ext_disp == L['all']:
                has_ext = True
            else:
                has_ext = (ext == self.ext_map.get(ext_disp))
            if has_tag and has_ext:
                self.filtered_paths.append(p)
        self.listbox.delete(0, tk.END)
        for p in self.filtered_paths:
            self.listbox.insert(tk.END, p)

    def update_tag_buttons(self):
        for w in self.tag_frame.winfo_children():
            w.destroy()
        cols = 4
        for idx, tag in enumerate(self.tags):
            r, c = divmod(idx, cols)
            btn = ctk.CTkButton(
                self.tag_frame,
                text=tag,
                width=100,
                command=lambda t=tag: self.toggle_tag(t)
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="w")

    def on_select_all(self):
        self.listbox.select_set(0, tk.END)
        return "break"

    def on_filter_change(self, _=None):
        self.update_file_list()

    def apply_toggle(self, path, tag):
        orig = os.path.normpath(path)
        dirp, base = os.path.split(orig)
        name, ext = os.path.splitext(base)
        m = TAG_PATTERN.search(name)
        tags = set()
        base_name = m and TAG_PATTERN.sub('', name) or name
        if m:
            for t in m.group(1).split(','):
                t = t.strip()
                if t:
                    tags.add('#' + t.lstrip('#'))
        if tag in tags:
            tags.remove(tag)
        else:
            tags.add(tag)
        norm = []
        for t in tags:
            txt = t.lstrip('#').lower().replace(' ', '_')
            if len(txt) > MAX_TAG_LENGTH:
                messagebox.showwarning(
                    self.gettext('warning_long_tag_title'),
                    self.gettext('warning_long_tag_msg').format(tag=t, max=MAX_TAG_LENGTH)
                )
                continue
            norm.append('#' + txt)
        block = f'_[{",".join(norm)}]' if norm else ''
        new_name = f"{base_name}{block}{ext}"
        new_path = os.path.normpath(os.path.join(dirp, new_name))
        try:
            if new_path != orig:
                os.rename(orig, new_path)
            return new_path
        except FileNotFoundError:
            messagebox.showerror(
                self.gettext('error_rename_fail_title'),
                self.gettext('error_rename_fail_msg').format(path=orig)
            )
            return orig

    def apply_strip(self, path):
        orig = os.path.normpath(path)
        dirp, base = os.path.split(orig)
        name, ext = os.path.splitext(base)
        new_name = f"{TAG_PATTERN.sub('', name)}{ext}"
        new_path = os.path.normpath(os.path.join(dirp, new_name))
        try:
            if new_path != orig:
                os.rename(orig, new_path)
            return new_path
        except FileNotFoundError:
            messagebox.showerror(
                self.gettext('error_rename_fail_title'),
                self.gettext('error_rename_fail_msg').format(path=orig)
            )
            return orig

    def _batch_rename(self, targets, func):
        # 先对子路径按深度降序，再逐个重命名并更新 self.paths
        targets_sorted = sorted(targets, key=lambda p: p.count(os.sep), reverse=True)
        for orig in targets_sorted:
            if orig not in self.paths:
                continue
            new = func(orig)
            self.paths = [new if p == orig else p for p in self.paths]
            # 如果是目录，更新子项路径
            _, base = os.path.split(orig)
            _, ext = os.path.splitext(base)
            if ext == '':
                for i, p in enumerate(self.paths):
                    if p.startswith(orig + os.sep):
                        self.paths[i] = new + p[len(orig):]

    def toggle_tag(self, tag):
        sel = [self.filtered_paths[i] for i in self.listbox.curselection()]
        if not sel:
            return
        self._batch_rename(sel, lambda p: self.apply_toggle(p, tag))
        self._update_ui_texts()

    def on_remove_tags(self):
        sel = [self.filtered_paths[i] for i in self.listbox.curselection()]
        if not sel:
            return
        self._batch_rename(sel, self.apply_strip)
        self._update_ui_texts()

    def on_add_custom_tag(self):
        raw = self.entry_custom.get().strip()
        if not raw:
            return
        txt = raw.lstrip('#').lower().replace(' ', '_')
        if len(txt) > MAX_TAG_LENGTH:
            messagebox.showwarning(
                self.gettext('warning_long_tag_title'),
                self.gettext('warning_long_tag_msg').format(tag=raw, max=MAX_TAG_LENGTH)
            )
            return
        self.toggle_tag('#' + txt)
        self.entry_custom.delete(0, tk.END)

    def on_select_folder(self):
        folder = filedialog.askdirectory(
            parent=self,
            title=self.gettext('select_folder')
        )
        if folder:
            self.paths = [os.path.normpath(p) for p in self.scan_folder(folder)]
            self._update_ui_texts()

    def on_select_files(self):
        fs = filedialog.askopenfilenames(
            parent=self,
            title=self.gettext('select_files')
        )
        if fs:
            self.paths = [os.path.normpath(p) for p in fs]
            self._update_ui_texts()

    def on_refresh(self):
        self._update_ui_texts()


if __name__ == "__main__":
    app = TaggerApp()
    app.mainloop()
