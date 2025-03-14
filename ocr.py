import requests

def ocr_space_file(image_data, api_key = 'K83980480488957'):
    """ 使用OCR.space API识别本地文件中的文本
    :param image_data: 二进制图片
    :param api_key: OCR.space API密钥
    :return: 返回的JSON格式结果
    """
    api_url = 'https://api.ocr.space/parse/image'
    files = {"image": ("image.jpg", image_data, "image/jpeg")}
    data = {
        'apikey': api_key,
        'isOverlayRequired': True,
        'detectOrientation': True,
        'OCREngine': 2,
        "language": "eng"
    }
    response = requests.post(api_url, data=data, files=files)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"OCR Space API 请求失败，状态码: {response.status_code}")

def crete_text(file_path):
    result = ocr_space_file(file_path)
    # 输出识别的文本
    parsed_text = result.get('ParsedResults')[0].get('ParsedText')
    return parsed_text




