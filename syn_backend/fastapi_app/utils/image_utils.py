from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
import random


def generate_custom_image(text: str, output_dir: Path) -> Path:
    """
    生成包含指定文本的图片
    
    Args:
        text: 要显示的文本
        output_dir: 输出目录
    
    Returns:
        生成的图片路径
    """
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成随机文件名
    random_id = random.randint(100000, 999999)
    filename = f"custom_{random_id}.png"
    output_path = output_dir / filename
    
    # 设置图片参数
    width, height = 800, 600
    background_color = (240, 240, 240)
    text_color = (50, 50, 50)
    
    # 创建图片
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)
    
    # 尝试使用系统字体
    font_path = None
    
    # 尝试不同的字体路径
    font_candidates = [
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux 默认字体
    ]
    
    for candidate in font_candidates:
        if os.path.exists(candidate):
            font_path = candidate
            break
    
    # 根据是否找到字体设置字体
    if font_path:
        font = ImageFont.truetype(font_path, 48)
    else:
        # 使用默认字体
        font = ImageFont.load_default()
    
    # 计算文本位置
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 绘制文本
    draw.text((x, y), text, font=font, fill=text_color)
    
    # 添加"自创"标识
    if font_path:
        small_font = ImageFont.truetype(font_path, 24)
    else:
        small_font = ImageFont.load_default()
    
    # 计算"自创"文本位置
    custom_text = "自创"
    custom_bbox = draw.textbbox((0, 0), custom_text, font=small_font)
    custom_width = custom_bbox[2] - custom_bbox[0]
    custom_x = width - custom_width - 20
    custom_y = height - 40
    
    # 绘制"自创"标识
    draw.text((custom_x, custom_y), custom_text, font=small_font, fill=(100, 100, 100))
    
    # 保存图片
    image.save(output_path)
    
    return output_path


def generate_custom_cover(text: str, base_dir: Path) -> Path:
    """
    生成包含文本和"自创"标识的封面图片
    
    Args:
        text: 用户输入的文本内容
        base_dir: 基础目录
    
    Returns:
        生成的图片路径
    """
    # 创建创意采集目录
    cc_dir = base_dir / "creative_collection"
    return generate_custom_image(text, cc_dir)