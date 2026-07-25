from PIL import Image

img = Image.open("assets/app_icon.png")

img.save("assets/app_icon.ico", format="ICO")

print("✅ Icon Created!")