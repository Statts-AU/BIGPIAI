
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2 import PageObject
import io
from reportlab.pdfgen import canvas



def create_pdf_for_toc(pdf_file, title, start_page, end_page, toc_entries):
    pdf_reader = PdfReader(pdf_file)
    pdf_writer = PdfWriter()

    # Add the heading page
    add_heading_page(title, pdf_writer, pdf_reader)

    # Add the TOC page
    add_toc_page(toc_entries, pdf_writer, pdf_reader)

    # Add the pages from start_page to end_page
    for page_num in range(start_page, end_page+1):
        pdf_writer.add_page(pdf_reader.pages[page_num])

    return pdf_writer


def add_heading_page(title, pdf_writer, pdf_reader):
    # Get dimensions from the first page of source PDF to match other pages
    source_page = pdf_reader.pages[0]
    page_width = float(source_page.mediabox.width)
    page_height = float(source_page.mediabox.height)

    # Create a new first page matching source dimensions
    first_page = PageObject.create_blank_page(
        width=page_width, height=page_height)
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # Set up the page with white background
    can.setFillColorRGB(1, 1, 1)  # White background
    can.rect(0, 0, page_width, page_height, fill=1)

    # Calculate text wrapping for title
    font_size = 36
    can.setFont("Helvetica-Bold", font_size)
    title_upper = title.upper()
    max_width = page_width * 0.8  # Use 80% of page width as maximum
    words = title_upper.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if can.stringWidth(test_line) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))

    # Draw wrapped title
    vertical_center = page_height / 2
    y_start = vertical_center + (len(lines) - 1) * (font_size + 10) / 2
    for i, line in enumerate(lines):
        y_pos = y_start - i * (font_size + 10)
        # Draw text in red
        can.setFillColorRGB(1, 0, 0)  # Red color
        can.drawCentredString(page_width / 2, y_pos, line)

    can.save()
    packet.seek(0)

    new_pdf = PdfReader(packet)
    first_page.merge_page(new_pdf.pages[0])
    pdf_writer.add_page(first_page)


def add_toc_page(toc_entries, pdf_writer, pdf_reader):
    # Get dimensions from the first page of source PDF to match other pages
    source_page = pdf_reader.pages[0]
    page_width = float(source_page.mediabox.width)
    page_height = float(source_page.mediabox.height)

    # Create a new TOC page matching source dimensions
    toc_page = PageObject.create_blank_page(
        width=page_width, height=page_height)
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # Set up the page with white background
    can.setFillColorRGB(1, 1, 1)  # White background
    can.rect(0, 0, page_width, page_height, fill=1)

    # Add "Table of Contents" title
    font_size_title = 24
    can.setFont("Helvetica-Bold", font_size_title)
    can.setFillColorRGB(0, 0, 0)  # Black color
    can.drawCentredString(page_width / 2, page_height -
                          50, "TABLE OF CONTENTS")

    # Add TOC entries
    font_size_entry = 12
    can.setFont("Helvetica", font_size_entry)
    y_position = page_height - 100
    line_spacing = 15

    current_page = toc_entries[0]['start_page'] if toc_entries else 0
    for entry in toc_entries:
        title = entry['section']
        page_number = entry['start_page'] - current_page + \
            1 + 2  # Adjust for the heading page and TOC page
        # Page numbers are 1-based
        toc_line = f"{title} .......... {page_number}"
        can.drawString(50, y_position, toc_line)
        y_position -= line_spacing
        if y_position < 50:  # Avoid writing beyond the page
            break

    can.save()
    packet.seek(0)

    new_pdf = PdfReader(packet)
    toc_page.merge_page(new_pdf.pages[0])
    pdf_writer.add_page(toc_page)


