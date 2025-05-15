import os
import urllib.parse
import win32com.client
import pythoncom


import os
import subprocess


def convert_docx_to_pdf(input_path):
    dir = os.path.dirname(input_path)
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    os.makedirs(dir, exist_ok=True)

    subprocess.run([
        "soffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", dir,
        input_path
    ], check=True)

    return os.path.join(dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")



# def convert_docx_to_pdf(docx_file):
#     """Converts DOCX to PDF using win32com.client."""
#     pythoncom.CoInitialize()

#     pdf_file = os.path.splitext(docx_file)[0] + ".pdf"
#     print(f"PDF file path: {pdf_file}")

#     try:
#         # Normalize the path and decode any URL-encoded characters
#         # Normalize path to avoid double slashes
#         normalized_path = os.path.normpath(docx_file)
#         decoded_path = urllib.parse.unquote(
#             # Decode any percent-encoded characters (like %20 for spaces)
#             normalized_path)

#         print(f"Converting DOCX to PDF: {decoded_path}")

#         # Ensure the folder for PDF file exists
#         output_folder = os.path.dirname(pdf_file)
#         if not os.path.exists(output_folder):
#             print(f"⚠️ Folder does not exist. Creating: {output_folder}")
#             os.makedirs(output_folder)

#         # Check if DOCX file exists before opening it
#         if not os.path.exists(decoded_path):
#             print(f"⚠️ DOCX file not found: {decoded_path}")
#             return

#         # Open the Word application and the DOCX file
#         word = win32com.client.Dispatch('Word.Application')
#         word.Visible = False
#         doc = word.Documents.Open(decoded_path)  # Use the decoded path

#         # Automatically update all Tables of Contents before saving
#         for toc in doc.TablesOfContents:
#             toc.Update()

#         doc.SaveAs(pdf_file, FileFormat=17)  # 17 is the file format for PDF
#         doc.Close()
#         word.Quit()

#         print(f"✅ Converted DOCX to PDF: {pdf_file}")
#         return pdf_file
#     except Exception as e:
#         print(f"⚠️ Error converting DOCX to PDF: {e}")
#         return ""


if __name__ == "__main__":
    docx_file = "../../input_files/input_document.docx"
    docx_file = os.path.abspath(docx_file)
    convert_docx_to_pdf(docx_file)
