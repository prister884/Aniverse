import ast
import re
import json

input_file = "pokemon.py"  # Input file
output_file = "parsed_data.py"  # Output file

def clean_and_load(file_path):
    """
    Cleans the file content by removing variable assignments (e.g., 'parsed_data = ') and loads the data.

    Args:
    - file_path (str): Path to the file.

    Returns:
    - list: Parsed data from the file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Remove the variable assignment part if it exists
    cleaned_content = re.sub(r'^\s*\w+\s*=\s*', '', content, count=1)

    # Fix invalid empty fields like 'attack': , 'health': , 'value': ,
    cleaned_content = re.sub(r"'(attack|health|value)':\s*,", r"'\1': '',", cleaned_content)

    # Replace problematic characters like `✨`, `🐉`, etc., before evaluating
    cleaned_content = cleaned_content.replace('✨', '').replace('🐉', '').replace('⚡️', '').replace('🩸', '').replace('🧩', '')

    return ast.literal_eval(cleaned_content)

def extract_data_from_text(extracted_text):
    """
    Extracts attack, health, and value from the given text.

    Args:
    - extracted_text (str): The OCR extracted text.

    Returns:
    - dict: A dictionary containing attack, health, and value fields.
    """
    data = {"attack": "", "health": "", "value": ""}

    attack_match = re.search(r"Ataka:\s*(\d+)", extracted_text)
    health_match = re.search(r"3aopoebe:\s*(\d+)", extracted_text)
    value_match = re.search(r"Uennoctn:\s*(\d+)", extracted_text)

    if attack_match:
        data["attack"] = attack_match.group(1).strip()
    if health_match:
        data["health"] = health_match.group(1).strip()
    if value_match:
        data["value"] = value_match.group(1).strip()

    return data

def merge_data(input_file, output_file):
    """
    Merges data from the input file into the output file.

    Args:
    - input_file (str): Path to the input file containing extracted data.
    - output_file (str): Path to the output file where the merged data will be saved.
    """
    input_data = clean_and_load(input_file)
    output_data = clean_and_load(output_file)

    input_dict = {}
    for idx, entry in enumerate(input_data, start=1):
        extracted_text = entry.get("extracted_text", "")
        input_dict[idx] = extract_data_from_text(extracted_text)

    for entry in output_data:
        entry_id = entry["id"]
        if entry_id in input_dict:
            # Update only the relevant fields; keep name unchanged
            entry.update({k: v for k, v in input_dict[entry_id].items() if k in ["attack", "health", "value"]})

    # Save the updated data as a JSON file
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump({"parsed_data": output_data}, file, ensure_ascii=False, indent=4)

    print(f"Data successfully merged and saved to {output_file}")

def main():
    merge_data(input_file, output_file)

if __name__ == "__main__":
    main()
