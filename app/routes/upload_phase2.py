import shutil
import uuid
from flask import request, jsonify, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request
import io
import zipfile
from flask import Flask, send_file
from io import BytesIO
from zipfile import ZipFile
import os

from .modules.phase2.main import process_document


def upload_phase2():
    from app import socketio
    input_folder = None
    # First verify the user isauthenticated
    try:
        verify_jwt_in_request()
    except:
        print("User is not authenticated")
        return redirect(url_for('login'))

    # Expecting a .zip file
    zip_file = request.files.get('zip_file')
    upload_id = request.form['upload_id']
    print('upload id is :', upload_id)

    if not zip_file:
        print("Missing zip file!")
        return jsonify({'error': 'Missing zip file!'}), 400

    try:
        # Create an in-memory buffer to hold the zip file contents
        zip_buffer = io.BytesIO(zip_file.read())

        with zipfile.ZipFile(zip_buffer, 'r') as z:
            word_file = None
            odt_file = None

            # Loop through the files inside the zip and find the Word file
            for file_name in z.namelist():
                print('file name : ', file_name)
                if file_name.endswith('.docx') or file_name.endswith('.doc'):
                    word_file = io.BytesIO(z.read(file_name))
                    word_file_name = file_name  # Save the file name

                if file_name.endswith('.dotx'):
                    odt_file = io.BytesIO(z.read(file_name))
                    odt_file_name = file_name  # Save the file name

            # Check if the Word file was found
            if not word_file:
                return jsonify({'error': 'Word file required inside the zip.'}), 400

            # Get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # generate a unique folder name
            unique_num = f"input-{uuid.uuid4().hex[:8]}"

            # Create an 'input' folder if it doesn't exist
            input_folder = os.path.join(current_dir, f'{unique_num}')
            os.makedirs(input_folder, exist_ok=True)

            # Save the Word file to the 'input' folder
            docx_path = os.path.join(input_folder, word_file_name)

            odt_path = os.path.join(
                input_folder, odt_file_name) if odt_file else None

            socketio.emit(
                'message', {'msg': 'word file is uploaded', 'progress': '5%'}, room=upload_id, namespace='/phase2')

            with open(docx_path, 'wb') as f:
                f.write(word_file.getbuffer())
                print('Saved input Word file:', docx_path)

            if (odt_file):
                with open(odt_path, 'wb') as f:
                    f.write(odt_file.getbuffer())
                    print('Saved input odt file:', odt_path)

            # Process the document
            document_paths = process_document(
                docx_path, upload_id=upload_id, dotx_path=odt_path)

            socketio.emit(
                'message', {'msg': 'Send outputs file', 'progress': '100%'}, room=upload_id, namespace='/phase2')

            stream = BytesIO()
            with ZipFile(stream, 'w') as zf:
                for path in document_paths:
                    if os.path.exists(path):
                        zf.write(path, arcname=os.path.basename(path))
            stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name='selected_documents.zip',
            mimetype='application/zip'
        )

    except Exception as e:
        import time
        time.sleep(0.2)
        # Remove the input folder and its contents
        remove_files_in_folder(input_folder)
        print(e)
        return jsonify({'error': f'An error occurred during processing: {str(e)}'}), 500

    finally:
        # Ensure the input folder is removed after processing
        remove_files_in_folder(input_folder)


def remove_files_in_folder(folder_path):
    """Remove a folder and all its contents if it exists."""
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
