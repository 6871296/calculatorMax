from PIL import Image
import pytesseract

img_path = 'calc_img.jpg'  # 你的图片文件路径
img = Image.open(img_path)
result = pytesseract.image_to_string(img, lang='chi_sim')  # chi_sim为简体中文识别

print("识别到的算式：", result)