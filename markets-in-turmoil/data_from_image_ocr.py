import cv2
import pytesseract
import pandas as pd
import numpy as np

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

image_path = "images/cropped_table.png" 

# Pre-process image for better results
img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
_, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Extract text to string
custom_config = r'--oem 3 --psm 6'  # OCR Engine Mode and Page Segmentation Mode
text = pytesseract.image_to_string(thresh, config=custom_config)

# Strip string 
rows = text.strip().split("\n")
df = pd.DataFrame([row.split() for row in rows if row.strip()])

# Save to csv
df.to_csv("data/raw_data.csv", index=False)


