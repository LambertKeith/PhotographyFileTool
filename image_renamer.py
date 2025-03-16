import os
import shutil
import tkinter as tk
import random
from tkinter import filedialog, messagebox
from tqdm import tqdm
import ocr
from pathlib import Path
import io
from PIL import Image

from zhipuai import ZhipuAI
import base64
from io import BytesIO


class ImageRenamerPage:
    def __init__(self, root):
        self.root = root

        # 选择文件夹
        self.folder_path = ""
        tk.Button(root, text="选择文件夹", command=self.select_folder).pack(pady=5)

        # 执行重命名
        tk.Button(root, text="重命名文件", command=self.file_open_rename).pack(pady=5)

    def select_folder(self):
        folder = filedialog.askdirectory(title="选择一个文件夹", initialdir="/", mustexist=True)
        if folder:
            self.folder_path = folder
            messagebox.showinfo("文件夹选择", f"已选择文件夹: {folder}")
        else:
            messagebox.showinfo("用户取消文件夹选择")

    def compress_image_to_1mb(self,image_path):
        """
        将图片压缩至 1MB 以内，并返回压缩后的图片二进制数据。
        """
        target_size_kb = 1024  # 目标大小 1MB
        quality = 85  # 初始质量
        max_width = 1920  # 最大宽度
        max_height = 1080  # 最大高度

        # 打开图片
        image = Image.open(image_path)

        # 如果图片尺寸超过最大限制，按比例缩小
        width, height = image.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)  # 使用 LANCZOS 替代 ANTIALIAS

        # 创建一个内存中的字节流
        buffer = io.BytesIO()

        # 循环调整质量，直到图片大小满足要求
        while True:
            # 保存图片到内存中的字节流
            buffer.seek(0)  # 清空缓冲区
            image.save(buffer, format="JPEG", quality=quality)
            buffer.seek(0)  # 移动指针到字节流的开头
            compressed_size_kb = buffer.getbuffer().nbytes / 1024  # 获取当前大小（单位：KB）

            # 如果图片大小小于目标大小，直接返回
            if compressed_size_kb <= target_size_kb:
                break

            # 如果图片大小大于目标大小，降低质量并重新尝试
            quality -= 5
            if quality < 10:  # 防止质量过低
                raise ValueError("无法将图片压缩到指定大小，请尝试进一步降低目标大小或调整图片尺寸。")

        # 返回压缩后的图片二进制数据
        return buffer.getvalue()

    def compress_image(self,img_path, target_size=1 * 1024 * 1024, max_size=(800, 800), initial_quality=90, step=5):
        with Image.open(img_path) as img:
            img = img.convert("RGB")  # 确保格式兼容
            img.thumbnail(max_size)  # 限制尺寸
            # 逐步降低质量直到满足大小要求
            quality = initial_quality
            while quality > 10:
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=quality)
                size = buffer.tell()  # 获取当前文件大小
                if size <= target_size:
                    return base64.b64encode(buffer.getvalue()).decode('utf-8')
                quality -= step  # 降低质量
            # 如果最低质量仍然超出目标大小，返回最终压缩结果
            return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def create_base_image(self,img_path):
        # 原始图片大小
        original_size = os.path.getsize(img_path)
        # 仅当图片大于 1MB 时压缩
        if original_size > 1 * 1024 * 1024:
            img_base = self.compress_image(img_path)
        else:
            with open(img_path, 'rb') as img_file:
                img_base = base64.b64encode(img_file.read()).decode('utf-8')
        return img_base

    def process_string(self,input_string):
        # 使用换行符进行分割
        split_data = input_string.split('\n')
        for i in split_data:
            if len(i) > 8:
                input_string = i
                break
        # 找到第一个换行符的位置
        newline_index = input_string.find("\n")

        # 如果存在换行符，移除换行符之后的所有内容
        if newline_index != -1:
            input_string = input_string[:newline_index]

        # 检查是否包含冒号
        if ":" in input_string:
            # 提取冒号之后的内容
            colon_index = input_string.find(":")
            result = input_string[colon_index + 1:].strip()  # 去除多余的空格
        else:
            # 如果没有冒号，保留原字符串
            result = input_string

        return result

    def glm_v4(self,img_base):
        client = ZhipuAI(api_key="1579ecae63f81f1f64c186f91cbd50cb.bC6OyvDrlSvI4Ffz")  # 填写您自己的APIKey
        response = client.chat.completions.create(
            model="glm-4v-flash",  # 填写需要调用的模型名称
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": img_base
                            }
                        },
                        {
                            "type": "text",
                            "text": "需要识别内容为货号，开头为字母，结尾为数字，且位数在8位以上。判断该内容是否为手写体，如果是，请输出true和货号，格式为true，货号；不是输出false；无法判断也输出false。不需要输出别的信息"
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content



    def rename_file(self,f):
        print(f)
        # 遍历目录下的所有文件
        for file_name in tqdm(reversed(list(os.listdir(f)))):
            if file_name.endswith((".jpg", ".png",".JPG",".PNG")):
                # 构建图像文件的完整路径
                image_path = os.path.join(f, file_name)
                # 压缩图片
                compress_img = self.compress_image_to_1mb(image_path)
                if 'true' in self.glm_v4(self.create_base_image(image_path)):
                    text = self.glm_v4(self.create_base_image(image_path))
                    break
                else:
                    # 执行ocr识别
                    text = ocr.crete_text(compress_img)
                    # 处理text
                    text = self.process_string(text)
                    if text != '' and text[0].isalpha() and text[-1].isdigit():
                        break

        # 使用 pathlib 获取文件所在的文件夹路径
        file = Path(image_path)
        folder_path = file.parent  # 获取文件所在的文件夹路径


        #ocr为识别出来的文件夹内追加txt文件
        if (text == ''):
            text = "无法识别"+str(random.randint(1, 100))

        elif 'true' in text:
            comma_split = text.split(',', 1)
            if len(comma_split)>1:
                text = comma_split[1].strip()
                text = text + "手写"

        elif not text[0].isalpha() or not text[-1].isdigit():
            text = text + "无法识别"

        else:
            text = text


        # 构造新的文件夹路径
        new_folder_path = folder_path.parent / text
        # 判断文件是否存在
        if new_folder_path.exists():
            print("失败")
            # messagebox.showinfo("失败", new_folder_path / "已存在")
        else:
        # 重命名文件夹
            folder_path.rename(new_folder_path)


    def file_open_rename(self):
        print(self.folder_path)
        if not self.folder_path:
            messagebox.showerror("错误", "请先选择文件夹")
            return

            # 遍历目录下的所有文件
        for file_name in os.listdir(self.folder_path):
            try:
                # 尝试执行可能引发异常的代码
                result = self.rename_file(os.path.join(self.folder_path, file_name))
            except IndexError as e:
                # 捕获异常并处理
                print(f"捕获到异常: {e}")
                # 可以选择重新抛出异常（可选）
                # raise
            except Exception as e:
                # 捕获其他类型的异常
                print(f"捕获到其他异常: {e}")
                # 可以选择重新抛出异常（可选）
                # raise
            finally:
                # 无论是否捕获到异常，都会执行 finally 块
                print("程序继续执行，执行后续清理或逻辑。")
        
        messagebox.showinfo("结束","操作已完成，请检查")







def main():
    root = tk.Tk()
    app = ImageRenamerPage(root)
    root.mainloop()

if __name__ == "__main__":
    main()
