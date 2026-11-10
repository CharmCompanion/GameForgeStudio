from PIL import Image, ImageDraw, ImageFilter

def create_gameforge_icon():
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded outer shield / squircle background in Obsidian Slate
    # #0b1118 with border #2d425c
    corner = 80
    bg_box = [16, 16, size - 16, size - 16]
    draw.rounded_rectangle(bg_box, radius=corner, fill=(11, 17, 24, 255), outline=(50, 75, 105, 255), width=8)

    # Subtle inner gradient glow
    for inset in range(24, 60, 4):
        alpha = int(25 * (1 - (inset - 24) / 36))
        draw.rounded_rectangle(
            [inset, inset, size - inset, size - inset],
            radius=corner - inset // 2,
            outline=(96, 165, 250, alpha),
            width=2
        )

    # Central Forge Hammer / Gaming Gem Polygon
    # Anvil base:
    # Top horn (left), flat face (top), foot (bottom)
    # Slate / Steel color: #1e293b, highlight: #60a5fa
    anvil_points = [
        (130, 240), # Left horn tip
        (200, 220), # Horn to face
        (380, 220), # Face right
        (390, 260), # Right heel
        (320, 280), # Body right
        (330, 360), # Base right
        (370, 400), # Foot right
        (140, 400), # Foot left
        (180, 360), # Base left
        (190, 280), # Body left
        (130, 240)  # Close
    ]
    draw.polygon(anvil_points, fill=(28, 41, 56, 255), outline=(70, 100, 135, 255))

    # Glowing Crystal / Sword Core in Electric Blue (#60a5fa & #38bdf8 & #ffffff)
    gem_points = [
        (256, 100), # Top apex
        (300, 170), # Right diamond
        (256, 250), # Bottom diamond
        (212, 170), # Left diamond
    ]
    draw.polygon(gem_points, fill=(56, 189, 248, 255), outline=(224, 242, 254, 255))

    # Facets on the gem
    draw.line([(256, 100), (256, 250)], fill=(255, 255, 255, 230), width=4)
    draw.line([(212, 170), (300, 170)], fill=(255, 255, 255, 200), width=3)
    draw.polygon([(256, 100), (256, 250), (300, 170)], fill=(96, 165, 250, 180))

    # Small game controller D-pad accent on anvil face
    cx, cy = 256, 330
    arm = 14
    thick = 8
    draw.rectangle([cx - thick, cy - arm, cx + thick, cy + arm], fill=(96, 165, 250, 220))
    draw.rectangle([cx - arm, cy - thick, cx + arm, cy + thick], fill=(96, 165, 250, 220))

    # Downscale for crisp multi-resolution ICO
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save('app.png', format='PNG')
    img.save('app.ico', format='ICO', sizes=icon_sizes)
    print("Generated app.ico and app.png successfully!")

if __name__ == '__main__':
    create_gameforge_icon()
