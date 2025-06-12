
import PyPDF2




def read_pdf(pdf_file):

    pdf_reader = PyPDF2.PdfReader(pdf_file)
    total_pages = len(pdf_reader.pages)

    page_contents = []

    # Process each page individually
    for page_number in range(total_pages):
        # md_text = pymupdf4llm.to_markdown(pdf_file, pages=[page_number])
        text = pdf_reader.pages[page_number].extract_text()
        page_content = {"page": page_number, "text": text}
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
        [f"=====PAGE {page['page']}=====\n{page['text']}\n"
         for page in page_contents[:4]]
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
        [f"=====PAGE {page['page']}=====\n{page['text']}\n" for page in page_contents]
    )

    return document_text


def format_toccontent_for_tocpage(page_contents, toc_end_page):

    toc_text = "\n".join(
        [
            f"=====PAGE {page['page']}=====\n{page['text']}"
            for page in page_contents[toc_end_page + 1:]
        ]
    )

    return toc_text
