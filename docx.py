import os
import sys
from docx import Document

def convert_docx_to_txt(input_folder):
    # Ensure the input folder exists
    if not os.path.exists(input_folder):
        print(f"The folder {input_folder} does not exist.")
        return

    # Iterate through all files in the folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".docx"):
            docx_path = os.path.join(input_folder, filename)
            txt_path = os.path.join(input_folder, f"{os.path.splitext(filename)[0]}.txt")

            try:
                # Open the docx file
                doc = Document(docx_path)

                # Extract text from the document
                full_text = []
                for para in doc.paragraphs:
                    full_text.append(para.text)

                # Write the extracted text to a new txt file
                with open(txt_path, "w", encoding="utf-8") as txt_file:
                    txt_file.write("\n".join(full_text))

                print(f"Converted {filename} to TXT")
            except Exception as e:
                print(f"Error converting {filename}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python docx_to_txt_converter.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    convert_docx_to_txt(folder_path)