import json
import requests
from requests_toolbelt import MultipartEncoder
import os
# from pdf2docx import Converter
from dotenv import load_dotenv
import os
load_dotenv

apiKey = os.getenv("PDF_REST_API_KEY")


# def convert_pdf_to_docx(pdf_file):
#     # Define the output file name
#     docx_file = os.path.splitext(pdf_file)[0] + ".docx"

#     try:
#         cv = Converter(pdf_file)
#         cv.convert(docx_file, start=0, end=None, exact=True)
#         cv.close()
#         print(f"Conversion successful: {docx_file}")
#     except Exception as e:
#         print(f"Error during conversion: {str(e)}")
#         return False

#     return True


def convert_pdf_to_docx_pdfrest(pdf_file):
    base_name = os.path.basename(pdf_file)
    # Split the base name into name and extension
    pdf_name, _ = os.path.splitext(base_name)
    word_endpoint_url = 'https://api.pdfrest.com/word'

    # Open the file and keep it open until the request is complete
    file = open(pdf_file, 'rb')

    mp_encoder_word = MultipartEncoder(
        fields={
            'file': ('document.pdf', file, 'application/pdf'),
            'output': pdf_name
        }
    )

    headers = {
        'Accept': 'application/json',
        'Content-Type': mp_encoder_word.content_type,
        'Api-Key': apiKey
    }

    print("Sending POST request to word endpoint...")

    response = requests.post(
        word_endpoint_url, data=mp_encoder_word, headers=headers)

    print("Response status code: " + str(response.status_code))

    if response.ok:
        response_json = response.json()
        print(json.dumps(response_json, indent=2))

        # Extract the output URL from the response
        output_url = response_json.get("outputUrl")

        if output_url:
            return output_url
        else:
            return None

        # if output_url:
        #     # Download the file from the output URL
        #     output_file = "converted_document.docx"
        #     download_response = requests.get(output_url)
        #     if download_response.ok:
        #         with open(output_file, "wb") as f:
        #             f.write(download_response.content)
        #         print(f"File downloaded successfully: {output_file}")
            # else:
            #     print(f"Failed to download the file. Status code: {download_response.status_code}")
    #     else:
    #         print("Output URL not found in the response.")

    # else:
    #     print(response.json())


def main():
    pdf_path = os.path.abspath("../../input_files/document.pdf")
    print(f"Processing file: {pdf_path}")

    if convert_pdf_to_docx_pdfrest(pdf_path):
        print("PDF to DOCX conversion completed successfully.")
    else:
        print("PDF to DOCX conversion encountered errors.")


if __name__ == "__main__":
    main()
