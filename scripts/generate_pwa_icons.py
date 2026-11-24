#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('assets/icons', exist_ok=True)

def generate_art_icon(size):
    # Museum Noir background
    img = Image.new('RGBA', (size, size), (7, 9, 14, 255))
    draw = ImageDraw.Draw(img)
    
    pad = int(size * 0.08)
    inner_pad = int(size * 0.14)
    
    # Outer frame border (LDS subtle hairline + accent)
    draw.rounded_rectangle([pad, pad, size - pad, size - pad], radius=int(size * 0.18), outline=(37, 99, 235, 200), width=max(2, int(size * 0.02)))
    
    # Inner elegant museum canvas frame
    draw.rounded_rectangle([inner_pad, inner_pad, size - inner_pad, size - inner_pad], radius=int(size * 0.12), outline=(245, 158, 11, 220), width=max(2, int(size * 0.025)))
    
    # Draw classical architectural pediment / sun & wave inside
    center_x = size // 2
    center_y = size // 2
    
    # Golden sun / star
    sun_r = int(size * 0.12)
    draw.ellipse([center_x - sun_r, center_y - int(size * 0.12) - sun_r, center_x + sun_r, center_y - int(size * 0.12) + sun_r], fill=(245, 158, 11, 240))
    
    # Elegant mountain / canvas waves
    p1 = (inner_pad + int(size * 0.06), inner_pad + int(size * 0.50))
    p2 = (center_x - int(size * 0.05), inner_pad + int(size * 0.28))
    p3 = (center_x + int(size * 0.15), inner_pad + int(size * 0.44))
    p4 = (size - inner_pad - int(size * 0.06), inner_pad + int(size * 0.32))
    p5 = (size - inner_pad - int(size * 0.06), size - inner_pad - int(size * 0.06))
    p6 = (inner_pad + int(size * 0.06), size - inner_pad - int(size * 0.06))
    
    draw.polygon([p1, p2, p3, p4, p5, p6], fill=(37, 99, 235, 180))
    
    # Foreground hill
    h1 = (inner_pad + int(size * 0.12), size - inner_pad - int(size * 0.06))
    h2 = (center_x + int(size * 0.05), inner_pad + int(size * 0.38))
    h3 = (size - inner_pad - int(size * 0.06), size - inner_pad - int(size * 0.06))
    draw.polygon([h1, h2, h3], fill=(16, 185, 129, 210))
    
    return img

for sz in [192, 512, 180, 128, 64, 32]:
    icon = generate_art_icon(sz)
    if sz == 180:
        icon.save('assets/icons/apple-touch-icon.png')
    elif sz == 32:
        icon.save('assets/icons/favicon-32.png')
    else:
        icon.save(f'assets/icons/icon-{sz}.png')

print("PWA icons generated successfully.")
