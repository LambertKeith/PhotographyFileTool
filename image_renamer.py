import os
import tkinter as tk
from tkinter import filedialog, messagebox

class ImageRenamerPage:
    def __init__(self, root):
        self.root = root

        # 选择文件夹
        self.folder_path = ""
        tk.Button(root, text="选择文件夹", command=self.select_folder).pack(pady=5)

        # 执行重命名
        tk.Button(root, text="重命名图片", command=self.rename_images).pack(pady=5)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            messagebox.showinfo("文件夹选择", f"已选择文件夹: {folder}")

    def rename_images(self):
        if not self.folder_path:
            messagebox.showerror("错误", "请先选择文件夹")
            return

        # 执行重命名逻辑
        messagebox.showinfo("成功", "图片重命名完成！")

