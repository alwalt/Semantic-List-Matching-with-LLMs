from PIL import Image, ImageDraw, ImageFont

# Load the uploaded image

image_path = "C:/Users/kayvo/OneDrive/Pictures/Screenshots/Screenshot 2024-06-12 091106.png"
image = Image.open(image_path)

# Set up the text to be added
text = "Kaji T."
font_size = 150

# Load a font
try:
    # Load a truetype or opentype font file, and create a font object.
    font = ImageFont.truetype("arial.ttf", font_size)
except IOError:
    # If the font file is not found, use a default font.
    font = ImageFont.load_default()

# Get a drawing context
draw = ImageDraw.Draw(image)

# Calculate text width and height to position it at the bottom center
text_width = draw.textlength(text, font)
text_height = draw.textlength(text, font)
image_width, image_height = image.size
text_x = (image_width - text_width) / 2
text_y = image_height - text_height - 10  # 10 pixels from the bottom

# Add text to image
draw.text((text_x, text_y), text, font=font, fill="white")

# Save the edited image
edited_image_path = "/mnt/data/Screenshot_edited.png"
image.save(edited_image_path)

edited_image_path
