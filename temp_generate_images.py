from PIL import Image, ImageDraw, ImageFont
import os

# Brand colors
CORAL = '#E85A4F'
NAVY = '#1A1A2E'
MINT = '#7EC8A3'
NEUTRAL_BG = '#FAF7F5'

# Tagline
TAGLINE = "Favorites on repeat. New loves on deck. Groceries on autopilot."

def create_image(width, height, filename, bg_color=NEUTRAL_BG, text_color=NAVY, title="Go, Cart!", subtitle=""):
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load a font, fallback to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=min(width//10, 80))
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size=min(width//20, 40))
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()

    # Draw title
    bbox = draw.textbbox((0,0), title, font=font_large)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    y = height // 4
    draw.text((x, y), title, fill=text_color, font=font_large)

    # Draw subtitle if provided
    if subtitle:
        bbox = draw.textbbox((0,0), subtitle, font=font_medium)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = height // 2 + 50
        draw.text((x, y), subtitle, fill=CORAL, font=font_medium)

    # Save
    img.save(os.path.join('frontend/public', filename))
    print(f"Created {filename} ({width}x{height})")

# OG Image
create_image(1200, 630, 'og-image.png', subtitle=TAGLINE[:60] + "...")  # Shorten tagline

# Favicon set - simple "GC" logo for icons
def create_favicon(size, filename):
    img = Image.new('RGB', (size, size), NEUTRAL_BG)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=size//2)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0,0), "GC", font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    draw.text((x, y), "GC", fill=CORAL, font=font)
    img.save(os.path.join('frontend/public', filename))
    print(f"Created favicon {filename} ({size}x{size})")

sizes = [
    (16, 'favicon-16x16.png'),
    (32, 'favicon-32x32.png'),
    (96, 'favicon-96x96.png'),
    (180, 'apple-touch-icon-180x180.png'),
    (192, 'favicon-192x192.png'),
    (512, 'favicon-512x512.png')
]

for size, filename in sizes:
    create_favicon(size, filename)

print("All images generated successfully!")
