import shutil
import uuid
from flask import request, jsonify, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request
import io
import zipfile

from .modules.phase2.main import process_document
import os


def upload_phase2():
    # First verify the user isauthenticated
    try:
        verify_jwt_in_request()
    except:
        print("User is not authenticated")
        return redirect(url_for('login'))

    # Expecting a .zip file
    zip_file = request.files.get('zip_file')

    if not zip_file:
        print("Missing zip file!")
        return jsonify({'error': 'Missing zip file!'}), 400

    try:
        # Create an in-memory buffer to hold the zip file contents
        zip_buffer = io.BytesIO(zip_file.read())

        with zipfile.ZipFile(zip_buffer, 'r') as z:
            word_file = None

            # Loop through the files inside the zip and find the Word file
            for file_name in z.namelist():
                if file_name.endswith('.docx') or file_name.endswith('.doc'):
                    word_file = io.BytesIO(z.read(file_name))
                    word_file_name = file_name  # Save the file name

            # Check if the Word file was found
            if not word_file:
                return jsonify({'error': 'Word file required inside the zip.'}), 400

            # Get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # generate a unique folder name
            unique_num = f"input-{uuid.uuid4().hex[:8]}"

            # Create an 'input' folder if it doesn't exist
            input_folder = os.path.join(current_dir, f'input-${unique_num}')
            os.makedirs(input_folder, exist_ok=True)

            # Save the Word file to the 'input' folder
            docx_path = os.path.join(input_folder, word_file_name)

            with open(docx_path, 'wb') as f:
                f.write(word_file.getbuffer())
                print('Saved input Word file:', docx_path)

            # Process the document
            documents = process_document(docx_path)

            print('converting the pdf to docx back !')
            # conversion of pdf to docx
            from .modules.phase2.helper.converter.pdf_to_docx import convert_pdf_to_docx_pdfrest

            docx_urls = [
                {"filename": os.path.basename(
                    pdf_path), "docxurl": convert_pdf_to_docx_pdfrest(pdf_path)}
                for pdf_path in documents
            ]
            print("docx url : ", docx_urls)

            # Remove the input folder and its contents
            remove_files_in_folder(input_folder)

        # docx_urls = [{'filename': 'Annexure 1 - Tender Acknowledgement and Execution.pdf', 'docxurl': 'https://api.pdfrest.com/resource/223d3b5a4-79eb-4735-8a43-ce114482aea2?format=file'}, {'filename': 'Annexure 2 - Volume 1 Tenderer Details.pdf', 'docxurl': 'https://api.pdfrest.com/resource/204866a2b-1876-4f0b-95b3-42f7658814a6?format=file'}, {'filename': 'Volume 2 Delivery Capability and Experience.pdf', 'docxurl': 'https://api.pdfrest.com/resource/2ceed7cb5-da4f-4796-b11c-0f0ce8a97568?format=file'}, {'filename': 'Volume 3 Workplace Health Safety and Environment WHSE.pdf',
            #  'docxurl': 'https://api.pdfrest.com/resource/23ac90013-7793-4a27-9de8-f7e791f186d7?format=file'}, {'filename': 'Volume 4 Delivery Strategy.pdf', 'docxurl': 'https://api.pdfrest.com/resource/22cfc5d4f-0198-47fe-bf9b-3a7e6ed37d61?format=file'}, {'filename': 'Volume 5 Pricing.pdf', 'docxurl': 'https://api.pdfrest.com/resource/2e12b5eef-6175-4950-859a-837d55f7615a?format=file'}, {'filename': 'Volume 6 Departures.pdf', 'docxurl': 'https://api.pdfrest.com/resource/2e25537c8-b0b1-4edd-a194-8ae4c417449d?format=file'}]

        return jsonify({'files': docx_urls}), 200

    except Exception as e:
        import time
        time.sleep(0.2)
        # Remove the input folder and its contents
        remove_files_in_folder(input_folder)
        print(e)
        return jsonify({'error': f'An error occurred during processing: {str(e)}'}), 500


def remove_files_in_folder(folder_path):
    """Remove a folder and all its contents if it exists."""
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
