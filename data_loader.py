import os
import csv
from PIL import Image

CSV_PATH = "operators_info.csv"
IMG_DIR = "resource_logo"

def load_operators(csv_path=CSV_PATH):
    operators = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            operators.append(row)
    return operators

def load_avatars(operators, img_dir=IMG_DIR):
    avatars = {}
    for op in operators:
        zh_name = op["zh_name"].strip()
        img_path = os.path.join(img_dir, f"头像_{zh_name}.png")
        if os.path.exists(img_path):
            try:
                img = Image.open(img_path).resize((64, 64))
                avatars[zh_name] = img  # 返回的是 PIL.Image
            except Exception as e:
                print(f"⚠️ 加载失败: {img_path} -> {e}")
        else:
            print(f"❌ 找不到头像：{img_path}")
    return avatars
