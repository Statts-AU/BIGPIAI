import fitz  # PyMuPDF
import PyPDF2
import pymupdf4llm

def normalize_for_comparison(text):
    """Normalize text for comparison by standardizing hyphens and spaces"""
    # Replace all types of hyphens/dashes with standard hyphen
    replacements = {
        '\u2013': '-',  # en dash (–)
        '\u2014': '-',  # em dash (—)
        '\u2010': '-',  # hyphen
        '\u2011': '-',  # non-breaking hyphen
        '\u2012': '-',  # figure dash
        '\u2015': '-',  # horizontal bar
        '\u2212': '-',  # minus sign
    }

    for unicode_dash, replacement in replacements.items():
        text = text.replace(unicode_dash, replacement)


# def read_pdf(pdf_file):
#     pdf_reader = PyPDF2.PdfReader(pdf_file)
#     total_pages = len(pdf_reader.pages)

#     page_contents = []
#     for page_num in range(total_pages):
#         page = pdf_reader.pages[page_num]
#         text = page.extract_text()
#         page_content = {"page": page_num, "text": text}
#         page_contents.append(page_content)

#     return page_contents

def read_pdf(pdf_file):
    # Determine the total number of pages in the PDF
    with fitz.open(pdf_file) as doc:
        total_pages = doc.page_count

    pdf_reader = PyPDF2.PdfReader(pdf_file)
    total_pages = len(pdf_reader.pages)

    page_contents = []

    # Process each page individually
    for page_number in range(total_pages):
        md_text = pymupdf4llm.to_markdown(pdf_file, pages=[page_number])
        page_content = {"page": page_number, "text": md_text}
        page_contents.append(page_content)

    return page_contents


def format_content_for_toc_check(page_contents):
    """Format PDF content for checking Table of Contents"""
    # Extract the first 3 pages of text content
    first_pages_text = " ".join([page["text"] for page in page_contents[:5]])
    return first_pages_text


def format_content_for_toc_endpage_extraction(page_contents):
    """Format PDF content for extracting Table of Contents end page"""

    # Extract the first 3 pages of text content
    content = "\n".join(
        [f"=== PAGE {page['page']} ===\n{page['text']}\n"
         for page in page_contents[:6]]
    )
    return content


def format_toc_page_for_extraction(page_contents, toc_end_page):

    # Get TOC content for section extraction
    toc_text = "\n".join(
        [f"\n{page['text']}\n" for page in page_contents[:toc_end_page + 1]]
    )

    return toc_text


def format_non_toc_page_for_extraction(page_contents):
   
    document_text = "\n".join(
        [f"===== PAGE {page['page']} =====\n{page['text']}\n" for page in page_contents]
    )

    return document_text
