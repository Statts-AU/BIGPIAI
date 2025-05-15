
from PyPDF2 import PdfReader
from .helper.converter.docx_to_pdf import convert_docx_to_pdf
from .helper.split_by_page import create_pdf_for_toc
from .helper.extractions.toc_extraction import extract_toc_from_nontoc_content, extract_toc_from_toc_page
from .helper.check_toc import check_toc_in_pdf
from .helper.normalize import read_pdf
import os


def process_document(input_docx):
    """Main function to process the document."""

    if input_docx is None:
        return
    
    pdf_file = convert_docx_to_pdf(input_docx)
    
    # pdf_file = 'document.pdf'
    page_contents = read_pdf(pdf_file)
    print("path for pdf file is : ", pdf_file)

    # list of dict containing section and start page [ {"section": "section_name", "start_page": 1} ..]
    toc_entries = []
    if not check_toc_in_pdf(page_contents):
        print("No Table of Contents found in the document.")
        # toc_insertion_page = find_toc_insertion_page(page_contents)
        toc_entries = extract_toc_from_nontoc_content(
            page_contents)
    else:
        print("Table of Contents found in the document.")
        toc_entries = extract_toc_from_toc_page(page_contents)

    add_end_page_in_toc_entries(toc_entries, pdf_file=pdf_file)
    print('document toc :')
    printTocEntries(toc_entries)
    print("-----------------------")

    output_dir = os.path.join(os.path.dirname(pdf_file), 'truncated_schedules')
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

        print(f"Extracted TOC for section: {title}")
        printTocEntries(curr_tocs)

        pdf_writer = create_pdf_for_toc(
            pdf_file, title, start_page, end_page, curr_tocs)

        # Generate output filename
        safe_title = "".join(x for x in title if x.isalnum()
                             or x in (' ', '-', '_')).strip()
        output_filename = f"{safe_title}.pdf"
        output_path = os.path.join(output_dir, output_filename)

        # Save the section
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        print(f"✅ Created: {output_filename}")
        print("-----------------------")
        output_paths.append(output_path)

    return output_paths


def add_end_page_in_toc_entries(toc_entries, pdf_file):
    pdf_reader = PdfReader(pdf_file)
    total_pages = len(pdf_reader.pages)
    for i in range(len(toc_entries)):
        # Calculate end page
        if i < len(toc_entries) - 1:
            # Get the page number of the next section's start
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
