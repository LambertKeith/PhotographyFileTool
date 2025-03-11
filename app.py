import tkinter as tk
from tkinter import ttk
from image_distributor import ImageDistributorPage
from image_renamer import ImageRenamerPage
from settings import SettingsPage

class ImageOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片管理工具")
        self.root.geometry("600x400")

        # 创建 Notebook 作为分页栏
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # 添加分页（功能模块）
        self.add_page("图片分配", ImageDistributorPage)
        self.add_page("图片重命名", ImageRenamerPage)
        self.add_page("设置", SettingsPage)

    def add_page(self, title, PageClass):
        """添加新功能页面到 Notebook"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        PageClass(frame)  # 初始化功能页面

def main():
    root = tk.Tk()
    app = ImageOrganizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
