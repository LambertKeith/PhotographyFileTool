import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.CR2', '.CR3', '.CRW', '.NEF', '.NRW', '.ARV', '.SRF','.ARW', '.arw'}


class ImageDistributorPage:
    def __init__(self, root):
        self.root = root

        # 选择文件夹
        self.folder_path = ""
        tk.Button(root, text="选择文件夹", command=self.select_folder).pack(pady=5)

        # 批次数输入
        self.folder_count_label = tk.Label(root, text="请输入批次数：")
        self.folder_count_label.pack()
        self.folder_count_entry = tk.Entry(root)
        self.folder_count_entry.pack()

        # 确认按钮
        tk.Button(root, text="确认", command=self.generate_folder_inputs).pack(pady=5)

        # 容器框架
        self.input_frame = tk.Frame(root)
        self.input_frame.pack()

        # 复选框 - 选择是否重命名图片
        self.rename_checkbox = tk.IntVar()
        self.rename_checkbox_button = tk.Checkbutton(root, text="是否重命名图片", variable=self.rename_checkbox)
        self.rename_checkbox_button.pack(pady=5)

        # 最终确认按钮
        self.final_confirm_button = tk.Button(root, text="开始分配", command=self.collect_file_counts)
        self.final_confirm_button.pack(pady=5)

        # 动态输入框存储
        self.file_count_entries = []

    def select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            messagebox.showinfo("文件夹选择", f"已选择文件夹: {folder}")

    def generate_folder_inputs(self):
        """根据批次数动态生成输入框"""
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        try:
            folder_count = int(self.folder_count_entry.get())
            if folder_count <= 0:
                raise ValueError("批次数必须大于0")

            self.file_count_entries = []
            for i in range(folder_count):
                label = tk.Label(self.input_frame, text=f"第{i+1}批单款图片数量：")
                label.pack()
                entry = tk.Entry(self.input_frame)
                entry.pack()
                self.file_count_entries.append(entry)
        except ValueError:
            messagebox.showerror("错误", "请输入正确的批次数")

    def collect_file_counts(self):
        """检查用户输入，并执行图片分配"""
        file_counts = []
        try:
            for entry in self.file_count_entries:
                count = int(entry.get())
                if count <= 0:
                    raise ValueError("文件数必须大于0")
                file_counts.append(count)

            if not self.folder_path:
                messagebox.showerror("错误", "请先选择文件夹")
                return

            self.file_counts = file_counts  # 存储输入的分配数据

            # 检查图片总数是否满足要求
            if self.pre_verification():
                if self.rename_checkbox.get() == 1:
                    self.rename_images()
                self.distribute_images_into_subfolders()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的正整数")

    def pre_verification(self):
        """检查文件夹中的图片数量是否能按规则分配"""
        folder_path = self.folder_path
        numbers = self.file_counts

        if not os.path.exists(folder_path):
            messagebox.showerror("错误", "文件夹不存在")
            return False

        image_extensions = IMAGE_EXTENSIONS
        """ image_files = [f for f in os.listdir(folder_path)
                       if os.path.isfile(os.path.join(folder_path, f)) and
                       os.path.splitext(f)[1].lower() in image_extensions] """
        image_files = [f for f in os.listdir(folder_path)
                       if os.path.isfile(os.path.join(folder_path, f))]
        print(image_files)
        for i in image_files:
            pass
            #if os.path.splitext(i)[1] == 'ARW'

        image_count = len(image_files)
        total_sum = sum(numbers)

        # 判断是否可以整除
        if image_count % total_sum != 0:
            messagebox.showerror("错误", "图片数量无法整除")
            return False

        self.quotient = image_count // total_sum  # 计算可以生成的子文件夹数量

        # 预创建子文件夹
        for i in range(1, self.quotient + 1):
            subfolder_path = os.path.join(folder_path, str(i))
            if not os.path.exists(subfolder_path):
                os.makedirs(subfolder_path)

        return True

    def rename_images(self):
        """重命名文件夹内所有图片"""
        folder_path = self.folder_path

        if not os.path.exists(folder_path):
            messagebox.showerror("错误", "文件夹不存在")
            return

        image_extensions = IMAGE_EXTENSIONS
        image_files = sorted([f for f in os.listdir(folder_path)
                              if os.path.isfile(os.path.join(folder_path, f)) and
                              os.path.splitext(f)[1].lower() in image_extensions])

        for i, filename in enumerate(image_files):
            new_filename = f"{str(i+1).zfill(5)}{os.path.splitext(filename)[1]}"
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)

            os.rename(old_file_path, new_file_path)

        messagebox.showinfo("提示", "图片重命名完成！")

    def distribute_images_into_subfolders(self):
        """按用户输入的规则分配图片到子文件夹"""
        folder_path = self.folder_path
        quotient = self.quotient
        numbers = self.file_counts

        image_extensions = IMAGE_EXTENSIONS
        image_files = sorted([f for f in os.listdir(folder_path)
                              if os.path.isfile(os.path.join(folder_path, f))])

        if len(image_files) == 0:
            messagebox.showerror("错误", "没有找到可用的图片")
            return

        # 生成子文件夹路径
        subfolder_paths = [os.path.join(folder_path, str(i)) for i in range(1, quotient + 1)]

        # 确保子文件夹存在
        for subfolder in subfolder_paths:
            os.makedirs(subfolder, exist_ok=True)

        # 图片分配
        image_index = 0
        for equivalent_count in numbers:
            for i in range(quotient):
                if image_index >= len(image_files):
                    messagebox.showinfo("提示", "图片分配完成")
                    return

                target_folder = subfolder_paths[i]

                for _ in range(equivalent_count):
                    if image_index >= len(image_files):
                        return

                    image_file = image_files[image_index]
                    src_path = os.path.join(folder_path, image_file)
                    dest_path = os.path.join(target_folder, image_file)

                    shutil.move(src_path, dest_path)
                    image_index += 1

        messagebox.showinfo("提示", "图片分配完成！")
