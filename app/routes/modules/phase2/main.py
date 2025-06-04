
from PyPDF2 import PdfReader

from .helper.extractions.extract_toc_endpage import extract_toc_endpage

from .helper.extractions.extract_page_from_content import extract_page_from_content, find_section_start_pages
from .helper.converter.docx_to_pdf import convert_docx_to_pdf
from .helper.split_by_page import create_docx_start_endpage
from .helper.extractions.toc_extraction import extract_toc_from_nontoc_content, extract_toc_from_toc_page
from .helper.check_toc import check_toc_in_pdf
from .helper.normalize import read_pdf
import os


def process_document(input_docx):
    """Main function to process the document."""

    try:

        if input_docx is None:
            return

        pdf_file = convert_docx_to_pdf(input_docx)

        page_contents = read_pdf(pdf_file)

        print("path for pdf file is : ", pdf_file)



        # list of dict containing section and start page [ {"section": "section_name", "start_page": 1} ..]
        toc_entries = []
        toc_end_page = -1
        if not check_toc_in_pdf(page_contents):
            print("No Table of Contents found in the document.")
            toc_entries = extract_toc_from_nontoc_content(
                page_contents)
        else:
            print("Table of Contents found in the document.")
            toc_end_page = extract_toc_endpage(page_contents)
            sections = extract_toc_from_toc_page(page_contents)
            toc_entries = extract_page_from_content(
                page_contents, sections, toc_end_page)

        print("Extracted TOC Entries by GPT :")
        printTocEntries(toc_entries)
        print("-----------------------")

        print("Extracted TOC Entries by My functions :")
        toc_entries = find_section_start_pages(
            document_pages=page_contents[toc_end_page+1:], toc_entries=toc_entries)
        add_end_page_in_toc_entries(toc_entries, pdf_file=pdf_file)
        printTocEntries(toc_entries)
        print("-----------------------")
        print("------------------------\n")

        output_dir = os.path.join(os.path.dirname(
            pdf_file), 'truncated_schedules')
        print(f"output folder is{output_dir}")

        if not os.path.exists(output_dir):
            print(f"⚠️ Folder does not exist. Creating: {output_dir}")
            os.makedirs(output_dir)

        output_paths = []
        for toc_entry in toc_entries:
            start_page = toc_entry['start_page']
            end_page = toc_entry['end_page']
            title = toc_entry['section']

            curr_tocs = extract_toc_from_nontoc_content(
                page_contents=page_contents[start_page:end_page+1])

            print(f"Extracted TOC for section by GPT: {title}")
            printTocEntries(curr_tocs)
            print("-----------------------")
            curr_tocs = find_section_start_pages(
                document_pages=page_contents[start_page:end_page+1], toc_entries=curr_tocs)
            print(
                f"Updated TOC with start pages for section by My function: {title}")
            printTocEntries(curr_tocs)
            print("-----------------------")
            print("------------------------\n")

            import re
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)

            output_path = os.path.join(
                output_dir, f"{safe_title}.docx")

            create_docx_start_endpage(
                input_path=input_docx,
                start_page=start_page+1,
                end_page=end_page+1,
                output_path=output_path,
                title=title,
                toc_entries=curr_tocs
            )

            output_paths.append(output_path)

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


# if __name__ == "__main__":
#     input_docx = os.path.abspath('input_files/input_document.docx')
#     process_document(input_docx)
