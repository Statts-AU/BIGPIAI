
from PyPDF2 import PdfReader
from .helper.extractions.extract_toc_endpage import extract_toc_endpage
from .helper.extractions.extract_page_from_content import extract_page_from_content, find_section_start_pages
from .helper.converter.docx_to_pdf import convert_docx_to_pdf
from .helper.split_by_page import create_docx_start_endpage
from .helper.extractions.toc_extraction import extract_toc_from_nontoc_content, extract_toc_from_toc_page
from .helper.check_toc import check_toc_in_pdf
from .helper.normalize import read_pdf
import os


def process_document(input_docx, upload_id, dotx_path):
    """Main function to process the document."""
    from app import socketio
    try:

        if input_docx is None:
            return

        socketio.emit(
            'message', {'msg': 'Reading word file...', 'progress': '8%'}, room=upload_id, namespace='/phase2')

        pdf_file = convert_docx_to_pdf(input_docx)
        page_contents = read_pdf(pdf_file)

        print("path for pdf file is : ", pdf_file)

        # list of dict containing section and start page [ {"section": "section_name", "start_page": 1} ..]
        socketio.emit(
            'message', {'msg': 'Getting Table of Content...', "progress": '10%'}, room=upload_id, namespace='/phase2')

        toc_entries = []
        toc_end_page = -1
        if not check_toc_in_pdf(page_contents):
            print("No Table of Contents found in the document.")
            socketio.emit(
                'message', {'msg': 'No Table of Content Section found in the document..\ntrying to create one', "progress": '20%'}, room=upload_id, namespace='/phase2')

            toc_entries = extract_toc_from_nontoc_content(
                page_contents)

            socketio.emit(
                'message', {'msg': 'Table of Content created!', "progress": '30%'}, room=upload_id, namespace='/phase2')
        else:
            print("Table of Contents found in the document.")
            socketio.emit(
                'message', {'msg': 'Table of Content found in the document \n trying to fetch details...', "progress": '40%'}, room=upload_id, namespace='/phase2')
            toc_end_page = extract_toc_endpage(page_contents)
            sections = extract_toc_from_toc_page(page_contents)
            toc_entries = extract_page_from_content(
                page_contents, sections, toc_end_page)
            socketio.emit(
                'message', {'msg': 'Fetched the Toc Entries', "progress": '50%'}, room=upload_id, namespace='/phase2')

        print("Extracted TOC Entries by My functions :")
        toc_entries = find_section_start_pages(
            document_pages=page_contents[toc_end_page+1:], toc_entries=toc_entries)
        add_end_page_in_toc_entries(toc_entries, pdf_file=pdf_file)
        printTocEntries(toc_entries)
        socketio.emit(
            'message', {'msg': tocEntriesToString(toc_entries=toc_entries)}, room=upload_id, namespace='/phase2')
        print("-----------------------")
        print("-----------------------")

        output_dir = os.path.join(os.path.dirname(
            pdf_file), 'truncated_schedules')
        print(f"output folder is{output_dir}")

        if not os.path.exists(output_dir):
            print(f"Folder does not exist. Creating: {output_dir}")
            os.makedirs(output_dir)

        socketio.emit(
            'message', {'msg': 'Creating Table of Content for Each Section ...', "progress": '60%'}, room=upload_id, namespace='/phase2')
        output_paths = []
        for toc_entry in toc_entries:
            start_page = toc_entry['start_page']
            end_page = toc_entry['end_page']
            title = toc_entry['section']

            curr_tocs = extract_toc_from_nontoc_content(
                page_contents=page_contents[start_page:end_page+1])

            curr_tocs = find_section_start_pages(
                document_pages=page_contents[start_page:end_page+1], toc_entries=curr_tocs)

            socketio.emit(
                'message', {'msg': f'Created Table of Content for {title}', "progress": '70%'}, room=upload_id, namespace='/phase2')
            socketio.emit(
                'message', {'msg': tocEntriesToString(toc_entries=curr_tocs)}, room=upload_id, namespace='/phase2')

            print(
                f"Updated TOC with start pages for section by My function: {title}")
            printTocEntries(curr_tocs)

            print("-----------------------")

            import re
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)

            output_path = os.path.join(
                output_dir, f"{safe_title}.docx")

            socketio.emit(
                'message', {'msg': f'splitting {title} from {start_page} to {end_page}', "progress": '80%'}, room=upload_id, namespace='/phase2')

            create_docx_start_endpage(
                input_path=input_docx,
                start_page=start_page+1,
                end_page=end_page+1,
                output_path=output_path,
                title=title,
                toc_entries=curr_tocs,
                dotx_path=dotx_path)

            output_paths.append(output_path)

        socketio.emit(
            'message', {'msg': '🎉 All sections have been successfully processed and saved!', "progress": '100%'}, room=upload_id, namespace='/phase2')

        return output_paths

    except Exception as e:
        print(f"⚠️ Error processing document: {e}")
        raise Exception({e})


def add_end_page_in_toc_entries(toc_entries, pdf_file):
    pdf_reader = PdfReader(pdf_file)
    total_pages = len(pdf_reader.pages)
    for i in range(len(toc_entries)):
        # Calculate end page
        if i < len(toc_entries) - 1:
            # Get the page number of the next section's start
            if toc_entries[i + 1]['start_page'] is not None and toc_entries[i+1]['start_page'] == toc_entries[i]['start_page']:
                end_page = toc_entries[i]['start_page']
            else:
                end_page = toc_entries[i + 1]['start_page'] - 1
        else:
            # For the last section, use the total number of pages
            end_page = total_pages-1

        # Add the end page to the current toc entry
        toc_entries[i]['end_page'] = end_page


def printTocEntries(toc_entries):
    for entry in toc_entries:
        section = entry.get('section', 'Unknown Section')
        start_page = entry.get('start_page', 'N/A')
        end_page = entry.get('end_page', 'N/A')
        print(
            f"Section: {section}, Start Page: {start_page}, End Page: {end_page}")


def tocEntriesToString(toc_entries):
    lines = []
    for entry in toc_entries:
        section = entry.get('section', 'Unknown Section')
        start_page = entry.get('start_page', 'N/A')
        end_page = entry.get('end_page', '_')
        lines.append(
            f"Section: {section}, Start Page: {start_page}, End Page: {end_page}")
    return "\n".join(lines)


# if __name__ == "__main__":
#     input_docx = os.path.abspath('input_files/input_document.docx')
#     process_document(input_docx)
