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
"""

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

MAX_TAG_LENGTH = 30
TAG_PATTERN = re.compile(r'_\[#([^\]]+)\]$')

class TaggerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.title("File & Folder Tagger")
        self.geometry("900x700")

        self.paths = []
        self.filtered_paths = []
        self.tags = []

        self._build_ui()

    def _build_ui(self):
        top = ctk.CTkFrame(self)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top.grid_columnconfigure(tuple(range(6)), weight=1)

        ctk.CTkButton(top, text="Select Folder", command=self.on_select_folder).grid(row=0, column=0, padx=5)
        ctk.CTkButton(top, text="Select Files",  command=self.on_select_files).grid(row=0, column=1, padx=5)
        ctk.CTkButton(top, text="Remove Tags",   command=self.on_remove_tags).grid(row=0, column=2, padx=5)
        ctk.CTkButton(top, text="Refresh",       command=self.on_refresh).grid(row=0, column=3, padx=5)
        self.entry_custom = ctk.CTkEntry(top, placeholder_text="Custom Tag")
        self.entry_custom.grid(row=0, column=4, padx=5, sticky="ew")
        ctk.CTkButton(top, text="Add Custom Tag", command=self.on_add_custom_tag).grid(row=0, column=5, padx=5)

        ctk.CTkLabel(top, text="Tag Filter:").grid(row=1, column=0, sticky="w", padx=5)
        self.option_tag = ctk.CTkOptionMenu(top, values=["All"], command=self.on_filter_change)
        self.option_tag.grid(row=1, column=1, sticky="ew", padx=5)
        ctk.CTkLabel(top, text="Type Filter:").grid(row=1, column=2, sticky="w", padx=5)
        self.option_ext = ctk.CTkOptionMenu(top, values=["All"], command=self.on_filter_change)
        self.option_ext.grid(row=1, column=3, sticky="ew", padx=5)
        ctk.CTkButton(top, text="Select All", command=self.on_select_all).grid(row=1, column=4, padx=5)

        file_frame = ctk.CTkFrame(self)
        file_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        file_frame.grid_columnconfigure(0, weight=1)
        file_frame.grid_rowconfigure(0, weight=1)

        self.listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED, activestyle="none", highlightthickness=0)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        self.listbox.bind("<Control-a>", lambda e: self.on_select_all())

        scrollbar = tk.Scrollbar(file_frame, command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.tag_frame = ctk.CTkScrollableFrame(self, height=100)
        self.tag_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,10))

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

    def update_filter_menus(self):
        self.detect_tags()
        self.option_tag.configure(values=["All"] + self.tags)
        self.option_tag.set("All")
        exts = sorted(set(os.path.splitext(p)[1].lower() or 'folder' for p in self.paths))
        self.option_ext.configure(values=["All"] + exts)
        self.option_ext.set("All")

    def update_file_list(self):
        tag_sel = self.option_tag.get()
        ext_sel = self.option_ext.get()
        self.filtered_paths = []
        for p in self.paths:
            name = os.path.splitext(os.path.basename(p))[0]
            has_tag = (tag_sel == "All") or (tag_sel in name)
            ext = os.path.splitext(p)[1].lower() or 'folder'
            has_ext = (ext_sel == "All") or (ext_sel == ext)
            if has_tag and has_ext:
                self.filtered_paths.append(p)

        self.listbox.delete(0, tk.END)
        for p in self.filtered_paths:
            self.listbox.insert(tk.END, p)

    def update_tag_buttons(self):
        for w in self.tag_frame.winfo_children():
            w.destroy()
        for tag in self.tags:
            btn = ctk.CTkButton(self.tag_frame, text=tag, command=lambda t=tag: self.toggle_tag(t))
            btn.pack(side="left", padx=5, pady=5)

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
        base_name = name
        if m:
            base_name = TAG_PATTERN.sub('', name)
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
                messagebox.showwarning("跳过超长标签", f"{t} 超过 {MAX_TAG_LENGTH} 字符，已跳过")
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
            messagebox.showerror("重命名失败", f"找不到：{orig}")
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
            messagebox.showerror("重命名失败", f"找不到：{orig}")
            return orig

    def _batch_rename(self, targets, func):
        """
        通用批量重命名：先按路径深度（子层级）降序排序，
        然后逐一调用 func(orig)->new_path，对 self.paths 及其子路径做更新。
        """
        # 先深度排序，保证子项先改
        targets_sorted = sorted(targets, key=lambda p: p.count(os.sep), reverse=True)
        for orig in targets_sorted:
            if orig not in self.paths:
                continue
            # 调用具体重命名函数
            new = func(orig)
            # 精确替换重命名前的路径
            self.paths = [new if p == orig else p for p in self.paths]
            # 如果是目录（无扩展名），还要把所有子路径前缀一并改掉
            _, base = os.path.split(orig)
            _, ext = os.path.splitext(base)
            if ext == '':
                for idx, p in enumerate(self.paths):
                    if p.startswith(orig + os.sep):
                        self.paths[idx] = new + p[len(orig):]

    def toggle_tag(self, tag):
        sel_idx = self.listbox.curselection()
        sel = [self.filtered_paths[i] for i in sel_idx]
        if not sel:
            return
        # 先改子，再改父
        self._batch_rename(sel, lambda p: self.apply_toggle(p, tag))
        self.update_filter_menus()
        self.update_file_list()
        self.update_tag_buttons()

    def on_remove_tags(self):
        sel_idx = self.listbox.curselection()
        sel = [self.filtered_paths[i] for i in sel_idx]
        if not sel:
            return
        # 先改子，再改父
        self._batch_rename(sel, self.apply_strip)
        self.update_filter_menus()
        self.update_file_list()
        self.update_tag_buttons()

    def on_add_custom_tag(self):
        raw = self.entry_custom.get().strip()
        if not raw:
            return
        txt = raw.lstrip('#').lower().replace(' ', '_')
        if len(txt) > MAX_TAG_LENGTH:
            messagebox.showerror("标签太长", f"限 {MAX_TAG_LENGTH} 字符")
            return
        self.toggle_tag('#' + txt)
        self.entry_custom.delete(0, tk.END)

    def on_select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.paths = [os.path.normpath(p) for p in self.scan_folder(folder)]
            self.update_filter_menus()
            self.update_file_list()
            self.update_tag_buttons()

    def on_select_files(self):
        fs = filedialog.askopenfilenames()
        if fs:
            self.paths = [os.path.normpath(p) for p in fs]
            self.update_filter_menus()
            self.update_file_list()
            self.update_tag_buttons()

    def on_refresh(self):
        self.update_filter_menus()
        self.update_file_list()
        self.update_tag_buttons()

if __name__ == "__main__":
    app = TaggerApp()
    app.mainloop()
