import os
import json
from pypdf import PdfReader
from pptx import Presentation
import google.generativeai as genai
from docx import Document


api_key = "YOUR API KEY"
genai.configure(api_key=api_key)
model_gen = genai.GenerativeModel('gemini-1.5-flash')

print("Example: ")
print(r"C:\Users\domin\Downloads\Anatomy-of-Livestock.pptx")

# Use raw string notation for the prompt to avoid escape sequence issues
input_file_input = input(r"Paste the path of your file: (e.g., C:\Users\user\Downloads\Anatomy-of-Livestock.pptx or .pdf): ")

# Remove double quotes and single quotes from the input
input_file_input = input_file_input.replace('"', '').replace("'", '')

# Replace backslashes with forward slashes
input_file_input = input_file_input.replace("\\", "/")

# Remove leading/trailing whitespace
input_file = input_file_input.strip()

print(f"File path received: {input_file}")

number_of_cards = input("How many cards do you want? ")

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = []
    for page in reader.pages:
        text.append(page.extract_text())
    return " ".join(text)

def extract_text_from_pptx(file_path):
    presentation = Presentation(file_path)
    text = []
    for slide in presentation.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text.append(shape.text)
    return "\n".join(text)

def extract_text(file_path):
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.pptx'):
        return extract_text_from_pptx(file_path)
    else:
        raise ValueError("Unsupported file format")

def generate_flashcards(text):
    response = model_gen.generate_content(
        f"generate {number_of_cards} flashcards for the following as an array of objects only nothing else just the array as 'front': for the question and 'back': for the answer (no ```json```): {text}"
    )

    if hasattr(response, 'text'):
        result = response.text
    else:
        result = response

    cleaned_data = result.strip().strip('```javascript').strip('```')
    
    try:
        flashcards = json.loads(cleaned_data)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        flashcards = []
    
    return flashcards

def save_flashcards_to_txt(flashcards, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for card in flashcards:
            file.write(f"{card['front']}:{card['back']}\n")
    print(f"Flashcards saved to {output_file}")

text = extract_text(input_file)

print("Has all of the text! Sending to AI.")

flashcards = generate_flashcards(text)

print("Flashcards have been generated!")

file_name = input('Enter the name of the .txt file (without extension): ')

# Get the path to the Downloads folder
downloads_folder = os.path.expanduser("~/Downloads")

# Create the full path for the output file
output_file = os.path.join(downloads_folder, f'{file_name}.txt')

save_flashcards_to_txt(flashcards, output_file)
