
import os
import urllib.parse
import pythoncom
import win32com.client

# import subprocess
# def convert_docx_to_pdf(input_path):
#     dir = os.path.dirname(input_path)
#     if not os.path.exists(input_path):
#         raise FileNotFoundError(f"Input file does not exist: {input_path}")

#     os.makedirs(dir, exist_ok=True)

#     subprocess.run([
#         "soffice",
#         "--headless",
#         "--convert-to", "pdf",
#         "--outdir", dir,
#         input_path
#     ], check=True)

#     return os.path.join(dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")


def convert_docx_to_pdf(docx_file):
    pythoncom.CoInitialize()

    pdf_file = os.path.splitext(docx_file)[0] + ".pdf"
    print(f"PDF file path: {pdf_file}")

    try:
        normalized_path = os.path.normpath(docx_file)
        decoded_path = urllib.parse.unquote(normalized_path)

        if not os.path.exists(decoded_path):
            raise FileNotFoundError(f"DOCX file not found: {decoded_path}")

        output_folder = os.path.dirname(pdf_file)
        os.makedirs(output_folder, exist_ok=True)

        word = win32com.client.DispatchEx('Word.Application')  # <- fix
        word.Visible = False
        word.DisplayAlerts = False  # optional safety
        doc = word.Documents.Open(decoded_path)

        print(doc.TablesOfContents)
        for toc in doc.TablesOfContents:
            toc.Update()

        doc.SaveAs(pdf_file, FileFormat=17)
        doc.Close(False)
        word.Quit()

        print(f"✅ Converted DOCX to PDF: {pdf_file}")
        return pdf_file

    except Exception as e:
        raise Exception(
            f"Error converting DOCX to PDF: {e}. Please check the DOCX file and try again."
        )


if __name__ == "__main__":
    docx_file = "../../input_files/input_document.docx"
    docx_file = os.path.abspath(docx_file)
    convert_docx_to_pdf(docx_file)
