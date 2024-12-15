# import os
# import pytesseract
# from PIL import Image

# # Ensure pytesseract points to the correct path of your Tesseract executable.
# # Update this path based on your installation
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # For Windows users

# # Directory containing the pre-made dataset of images (screenshots)
# dataset_directory = "screenshots"  # Update this to your dataset directory path

# # Output Python file where the extracted text will be saved
# output_file = "pokemon.py"

# def ocr_from_image(image_path):
#     """
#     Perform OCR on an image and return the extracted text.
    
#     :param image_path: Path to the image to be processed.
#     :return: Extracted text from the image.
#     """
#     try:
#         # Open the image using Pillow
#         img = Image.open(image_path)

#         # Perform OCR on the image using Tesseract
#         extracted_text = pytesseract.image_to_string(img)

#         return extracted_text

#     except Exception as e:
#         print(f"Error during OCR: {e}")
#         return ""


# def process_images_from_directory(directory_path):
#     """
#     Process all images from the provided directory, perform OCR, and return the extracted text.
    
#     :param directory_path: Path to the directory containing images.
#     :return: List of extracted text from all images in the directory.
#     """
#     extracted_data = []

#     # Loop through all files in the directory
#     for filename in os.listdir(directory_path):
#         # Only process PNG and JPG files (you can adjust the extensions if needed)
#         if filename.endswith(".png") or filename.endswith(".jpg"):
#             image_path = os.path.join(directory_path, filename)

#             print(f"Processing image: {image_path}")
            
#             # Perform OCR on the image
#             extracted_text = ocr_from_image(image_path)

#             # Store the extracted text with the filename as the identifier
#             extracted_data.append({
#                 "image_filename": filename,
#                 "extracted_text": extracted_text
#             })

#     return extracted_data


# def save_extracted_data(extracted_data):
#     """
#     Save the extracted data to a Python file (parsed_data.py).
    
#     :param extracted_data: List of extracted text to be saved.
#     """
#     with open(output_file, "w", encoding="utf-8") as file:
#         file.write("parsed_data = [\n")
#         for item in extracted_data:
#             file.write(f"    {{\n")
#             file.write(f"        'image_filename': '{item['image_filename']}',\n")
#             file.write(f"        'extracted_text': '''{item['extracted_text']}''',\n")
#             file.write(f"    }},\n")
#         file.write("]\n")
#     print(f"Data successfully saved to {output_file}")


# def main():
#     # Process images from the provided dataset directory
#     extracted_data = process_images_from_directory(dataset_directory)

#     # Save the extracted data to a Python file
#     if extracted_data:
#         save_extracted_data(extracted_data)
#     else:
#         print("No data extracted, please check the dataset directory.")

# if __name__ == "__main__":
#     main()



import os
import pytesseract
from PIL import Image
import re
import time

# Ensure pytesseract points to the correct path of your Tesseract executable.
# Update this path based on your installation
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # For Windows users

# Directory containing the pre-made dataset of images (screenshots)
dataset_directory = "screenshots"  # Update this to your dataset directory path

# Output Python file where the extracted text will be saved
output_file = "pokemon1.py"

def ocr_from_image(image_path):
    """
    Perform OCR on an image and return the extracted text using Russian language.
    
    :param image_path: Path to the image to be processed.
    :return: Extracted text from the image.
    """
    try:
        # Open the image using Pillow
        img = Image.open(image_path)

        # Perform OCR on the image using Tesseract with Russian language
        extracted_text = pytesseract.image_to_string(img, lang='rus')

        return extracted_text

    except Exception as e:
        print(f"Error during OCR: {e}")
        return ""


def parse_extracted_text(extracted_text, image_id):
    """
    Parse the extracted text and format it into the required template.
    
    :param extracted_text: The OCR extracted text.
    :param image_id: The id to be used for the image URL (iteration number).
    :return: A dictionary with structured data.
    """
    # Initialize the structure
    parsed_data = {
        "id": image_id,
        "name": "",
        "rarity": "",
        "attack": "",
        "health": "",
        "value": "",
        "image_url": f"https://raw.githubusercontent.com/prister884/aniverse-files/refs/heads/main/bleach/{image_id}.jpg"
    }

    # Extract the name (first line in the OCR text)
    lines = extracted_text.split("\n")
    if lines:
        parsed_data["name"] = lines[0].strip()

    # Extract other fields using regular expressions (patterns adjusted)
    rarity_match = re.search(r"⚜️\s*Редкость:\s*([^\n]*)", extracted_text)
    attack_match = re.search(r"🗡️\s*Атака:\s*(\d+)", extracted_text)
    health_match = re.search(r"❤️\s*Здоровье:\s*(\d+)", extracted_text)
    value_match = re.search(r"💠\s*Ценность:\s*(\d+)", extracted_text)

    if rarity_match:
        parsed_data["rarity"] = rarity_match.group(1).strip()
    if attack_match:
        parsed_data["attack"] = int(attack_match.group(1))
    if health_match:
        parsed_data["health"] = int(health_match.group(1))
    if value_match:
        parsed_data["value"] = int(value_match.group(1))

    return parsed_data


def process_images_from_directory(directory_path):
    """
    Process all images from the provided directory, perform OCR, parse the text, and return the structured data.
    
    :param directory_path: Path to the directory containing images.
    :return: List of structured data from all images in the directory.
    """
    extracted_data = []

    # Loop through all files in the directory
    for idx, filename in enumerate(os.listdir(directory_path), start=1):
        # Only process PNG and JPG files (you can adjust the extensions if needed)
        if filename.endswith(".png") or filename.endswith(".jpg"):
            image_path = os.path.join(directory_path, filename)

            print(f"Processing image: {image_path}")
            
            # Perform OCR on the image
            extracted_text = ocr_from_image(image_path)

            # Parse the extracted text into the required format
            parsed_data = parse_extracted_text(extracted_text, idx)

            # Store the parsed data
            extracted_data.append(parsed_data)

    return extracted_data


def save_extracted_data(extracted_data):
    """
    Save the extracted data to a Python file (parsed_data.py).
    
    :param extracted_data: List of extracted text to be saved.
    """
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("parsed_data = [\n")
        for item in extracted_data:
            file.write(f"    {{\n")
            file.write(f"        'id': {item['id']},\n")
            file.write(f"        'name': '{item['name']}',\n")
            file.write(f"        'rarity': '{item['rarity']}',\n")
            file.write(f"        'attack': {item['attack']},\n")
            file.write(f"        'health': {item['health']},\n")
            file.write(f"        'value': {item['value']},\n")
            file.write(f"        'image_url': '{item['image_url']}',\n")
            file.write(f"    }},\n")
        file.write("]\n")
    print(f"Data successfully saved to {output_file}")


def main():
    # Process images from the provided dataset directory
    extracted_data = process_images_from_directory(dataset_directory)

    # Save the extracted data to a Python file
    if extracted_data:
        save_extracted_data(extracted_data)
    else:
        print("No data extracted, please check the dataset directory.")

if __name__ == "__main__":
    main()
