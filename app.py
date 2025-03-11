import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

# 获取当前脚本所在目录，兼容打包和开发环境
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class FolderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("赫德摄影部图片分配工具")
        self.root.geometry("400x600")

        # 设置图标
        icon_path = os.path.join(BASE_DIR, "ico.ico")
        try:
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"图标加载失败: {e}")

        # 选择文件夹按钮
        self.folder_path = ""
        self.select_folder_button = tk.Button(root, text="选择文件夹路径", command=self.select_folder)
        self.select_folder_button.pack(pady=10)

        # 文件夹数量输入框和确认按钮
        self.folder_count_label = tk.Label(root, text="请输入该文件夹中已经放入几批文件：")
        self.folder_count_label.pack()

        self.folder_count_entry = tk.Entry(root)
        self.folder_count_entry.pack()

        self.confirm_folder_count_button = tk.Button(root, text="确认", command=self.generate_folder_inputs)
        self.confirm_folder_count_button.pack(pady=5)

        # 容器框架，用于放动态生成的输入框
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=10)

        # 复选框，是否选择重命名
        self_check_frame = tk.Frame(root)
        self_check_frame.pack(pady=10)
        self.rename_checkbox = tk.IntVar()
        self.rename_checkbox.set(0)
        self.rename_checkbox_label = tk.Label(self_check_frame, text="是否选择重命名")
        self.rename_checkbox_label.pack(side=tk.LEFT)
        self.rename_checkbox_button = tk.Checkbutton(self_check_frame, variable=self.rename_checkbox)
        self.rename_checkbox_button.pack(side=tk.LEFT)

        # 最终确认按钮
        self.final_confirm_button = tk.Button(root, text="确认文件数量", command=self.collect_file_counts)
        self.final_confirm_button.pack(pady=10)

        # 存储动态生成的输入框
        self.file_count_entries = []

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            messagebox.showinfo("文件夹选择", f"已选择文件夹: {folder}")

    def generate_folder_inputs(self):
        # 清空旧的输入框
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        try:
            folder_count = int(self.folder_count_entry.get())
            if folder_count <= 0:
                raise ValueError("数量必须大于0")
            self.folder_count = folder_count

            self.file_count_entries = []

            for i in range(folder_count):
                label = tk.Label(self.input_frame, text=f"第{i+1}批 单款鞋子图片数量：")
                label.pack()

                entry = tk.Entry(self.input_frame)
                entry.pack()
                self.file_count_entries.append(entry)

        except ValueError:
            messagebox.showerror("错误", "请输入正确的数量（正整数）")

    def collect_file_counts(self):
        file_counts = []
        try:
            for entry in self.file_count_entries:
                count = int(entry.get())
                if count <= 0:
                    raise ValueError("文件数必须大于0")
                file_counts.append(count)
            if self.folder_path == "":  # 检查文件夹路径是否为空
                messagebox.showerror("错误", "请先选择文件夹路径")
                return

            self.file_counts = file_counts
            #messagebox.showinfo("文件数量确认", f"你输入的文件数量列表是: {file_counts}")
            print("文件数量列表:", file_counts)

            # 在这里可以把 file_counts 传递到后续处理逻辑中
        except ValueError:
            messagebox.showerror("错误", "请确保每个文件数量都是正整数")
            return
        
        if self.pre_verification():
            if self.rename_checkbox.get() == 1:
                #将所有的图片重命名
                self.rename_images()
            else:
                pass
            self.distribute_images_into_subfolders()
            pass
    

    def rename_images(self):
        folder_path = self.folder_path
        numbers = self.file_counts
        # 1. 获取当前文件夹下的所有文件（不包括子文件夹）
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"指定的文件夹不存在: {folder_path}")
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        image_files = [f for f in os.listdir(folder_path) 
                    if os.path.isfile(os.path.join(folder_path, f)) and 
                    os.path.splitext(f)[1].lower() in image_extensions]

        # 2. 对图片进行重命名
        for i, filename in enumerate(image_files):
            # 构造新的文件名，格式为：00001.jpg
            new_filename = f"{str(i+1).zfill(5)}{os.path.splitext(filename)[1]}"
            # 构造完整的文件路径
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)

            # 重命名文件
            os.rename(old_file_path, new_file_path)
            
        
        

    def pre_verification(self):
        folder_path = self.folder_path
        numbers = self.file_counts
        # 1. 获取当前文件夹下的所有文件（不包括子文件夹）
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"指定的文件夹不存在: {folder_path}")
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        image_files = [f for f in os.listdir(folder_path) 
                    if os.path.isfile(os.path.join(folder_path, f))]
        
        image_count = len(image_files)

        # 2. 计算正整数列表的和
        total_sum = sum(numbers)

        # 3. 计算商并判断是否整除
        if image_count % total_sum != 0:
            messagebox.showerror("错误", "图片数量不能整除")
            return False  # 不能整除直接返回

        self.quotient = image_count // total_sum

        # 4. 检查并新建子文件夹
        for i in range(1, self.quotient + 1):
            subfolder_path = os.path.join(folder_path, str(i))
            if not os.path.exists(subfolder_path):
                os.makedirs(subfolder_path)

        return True  # 处理完成返回True        


    def distribute_images_into_subfolders(self):
        root_folder, quotient, numbers = self.folder_path, self.quotient, self.file_counts
        """
        遍历整数列表，将对应数量的图片均匀分配到子文件夹。
        
        :param root_folder: 根文件夹路径
        :param quotient: 需要创建的子文件夹数量
        :param numbers: 需要分配的整数列表
        """
        # 确保根文件夹存在
        if not os.path.exists(root_folder):
            raise FileNotFoundError(f"根文件夹不存在: {root_folder}")
        
        # 获取所有图片文件
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        image_files = [f for f in os.listdir(root_folder) 
                    if os.path.isfile(os.path.join(root_folder, f)) and 
                    os.path.splitext(f)[1].lower() in image_extensions]
        
        if len(image_files) == 0:
            print("没有找到可用的图片文件。")
            return False

        # 生成子文件夹路径
        subfolder_paths = [os.path.join(root_folder, str(i)) for i in range(1, quotient + 1)]
        
        # 确保子文件夹存在
        for subfolder in subfolder_paths:
            os.makedirs(subfolder, exist_ok=True)

        # 遍历整数列表，进行图片分配
        image_index = 0  # 记录已分配的图片索引
        for equivalent_count in numbers:
            for i in range(quotient):
                # 确保不会超出图片总数
                if image_index >= len(image_files):
                    print("图片已全部分配完成。")
                    return True
                
                # 获取当前子文件夹
                target_folder = subfolder_paths[i]
                
                # 取出 equivalent_count 张图片
                for _ in range(equivalent_count):
                    if image_index >= len(image_files):  # 如果图片不足，则终止
                        return True
                    
                    image_file = image_files[image_index]
                    src_path = os.path.join(root_folder, image_file)
                    dest_path = os.path.join(target_folder, image_file)

                    # 移动图片到目标子文件夹
                    shutil.move(src_path, dest_path)
                    image_index += 1  # 递增索引

        print("图片分配完成。")
        messagebox.showinfo("提示", "图片分配完成。")
        return True


def main():
    root = tk.Tk()
    app = FolderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
