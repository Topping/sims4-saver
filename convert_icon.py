from PIL import Image

image = Image.open("icon.png")

if image.mode != "RGBA":
    image = image.convert("RGBA")

image.save("icon.ico", format="ICO")