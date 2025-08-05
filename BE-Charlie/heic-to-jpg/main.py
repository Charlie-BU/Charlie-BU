import os
from pillow_heif import register_heif_opener
from PIL import Image

# 启用 heif 解码器
register_heif_opener()

folder = './imgs'

if __name__ == '__main__':
    # 遍历当前目录下所有文件
    for filename in os.listdir(folder):
        if filename.lower().endswith('.heic'):
            filepath = os.path.join(folder, filename)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(folder, base_name + '.jpg')

            try:
                # 打开 HEIC 文件
                img = Image.open(filepath)
                img = img.convert("RGB")  # 确保兼容 JPG 格式
                img.save(output_path, "JPEG", quality=95)
                os.remove(filepath)  # 删除原始 HEIC 文件
                print(f"✅ Converted & deleted: {filename} → {base_name}.jpg")
            except Exception as e:
                print(f"❌ Failed to convert {filename}: {e}")

    print("🎉 所有 HEIC 文件已转换为 JPG，原文件已删除")
