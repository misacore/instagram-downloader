from PIL import Image, ImageDraw, ImageFont
import os

def create_gradient_icon(size, filename):
    """ساخت آیکون با گرادیانت زیبا"""
    img = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(img)
    
    # ساخت گرادیانت
    for y in range(size):
        ratio = y / size
        r = int(102 + (118 - 102) * ratio)
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b))
    
    # اضافه کردن آیکون دانلود
    icon_size = size // 2
    margin = size // 4
    
    # مستطیل دانلود
    arrow_width = icon_size // 3
    arrow_x = (size - arrow_width) // 2
    arrow_y = margin
    
    # فلش
    draw.rectangle([arrow_x, arrow_y, arrow_x + arrow_width, arrow_y + icon_size // 2], 
                   fill='white', outline='white', width=3)
    
    # نوک فلش
    points = [
        (size // 2, arrow_y + icon_size // 2 + arrow_width),
        (arrow_x - arrow_width // 2, arrow_y + icon_size // 2),
        (arrow_x + arrow_width + arrow_width // 2, arrow_y + icon_size // 2)
    ]
    draw.polygon(points, fill='white')
    
    # خط پایین
    line_y = arrow_y + icon_size // 2 + arrow_width + 10
    draw.line([(margin, line_y), (size - margin, line_y)], fill='white', width=5)
    
    # ذخیره
    img.save(filename, 'PNG')
    print(f'✅ آیکون {size}x{size} ساخته شد: {filename}')

# ساخت پوشه static
os.makedirs('static', exist_ok=True)

# ساخت آیکون‌ها
create_gradient_icon(192, 'static/icon-192.png')
create_gradient_icon(512, 'static/icon-512.png')

print('\n🎉 تمام آیکون‌ها با موفقیت ساخته شدند!')
