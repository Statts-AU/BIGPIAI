
from win32com.client import DispatchEx, constants
import win32com.client as win32
import pythoncom
import gc
import time
import os
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


def create_docx_start_endpage(input_path: str,
                              start_page: int,
                              end_page: int,
                              output_path: str,
                              title: str,
                              toc_entries: list[dict]) -> None:
    """
    Opens `input_docx`, pulls pages [start_page..end_page], then
    builds a new document:
      • page 1 = title
      • page 2 = manual right-aligned TOC
      • pages 3+ = the extracted pages
    and saves it to `output_docx`.

    This version:
    - Converts both paths to absolute.
    - Suppresses Word alerts.
    - Ensures both docs are closed before quitting Word.
    - Uses DispatchEx to avoid reusing an existing Word instance.
    """

    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)

    # 2) Kill any stale lock-files (~$...)
    for path in (input_path, output_path):
        lock = os.path.join(os.path.dirname(
            path), "~$" + os.path.basename(path))
        if os.path.exists(lock):
            try:
                os.remove(lock)
            except:
                pass

    # 3) Remove old output so SaveAs2 won’t complain
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except PermissionError:
            # if locked, rename it
            os.replace(output_path, output_path + ".old")

    # 4) Start Word
    pythoncom.CoInitialize()
    word = DispatchEx("Word.Application")
    # suppress any prompts
    word.DisplayAlerts = constants.wdAlertsNone
    word.Visible = False

    src = out = None
    try:
        # 5) Open source read-only
        src = word.Documents.Open(
            input_path,
            ReadOnly=True,
            ConfirmConversions=False,
            AddToRecentFiles=False
        )

        # 6) Clamp pages
        total = src.ComputeStatistics(constants.wdStatisticPages)
        if not (1 <= start_page <= total):
            raise ValueError(f"start_page must be between 1 and {total}")
        end_page = min(end_page, total)

        # 7) Copy the requested slice
        go1 = src.GoTo(What=constants.wdGoToPage,
                       Which=constants.wdGoToAbsolute,
                       Count=start_page)
        if end_page < total:
            go2 = src.GoTo(What=constants.wdGoToPage,
                           Which=constants.wdGoToAbsolute,
                           Count=end_page+1)
            slice_end = go2.Start - 1
        else:
            slice_end = src.Content.End

        src.Range(Start=go1.Start, End=slice_end).Copy()

        # 8) Build the new doc via Selection
        out = word.Documents.Add()
        word.Selection.HomeKey(Unit=constants.wdStory)

        # 8a) Title page
        word.Selection.ParagraphFormat.Alignment = constants.wdAlignParagraphCenter
        word.Selection.Font.Size = 36
        word.Selection.Font.Bold = True
        word.Selection.Font.Color = constants.wdColorRed
        word.Selection.TypeText(title)
        word.Selection.Font.Size = 12  # Reset to default after title
        word.Selection.Font.Bold = False
        word.Selection.ParagraphFormat.Alignment = constants.wdAlignParagraphLeft
        word.Selection.InsertBreak(constants.wdPageBreak)

        # 8b) TOC page with right-aligned numbers
        pw = out.PageSetup.PageWidth
        lm = out.PageSetup.LeftMargin
        rm = out.PageSetup.RightMargin
        usable = pw - lm - rm

        pf = word.Selection.ParagraphFormat
        pf.TabStops.ClearAll()
        pf.TabStops.Add(Position=usable, Alignment=constants.wdAlignTabRight)

        word.Selection.Font.Bold = True
        word.Selection.Font.Color = constants.wdColorRed
        word.Selection.TypeText("Table of Contents")
        word.Selection.TypeParagraph()
        word.Selection.Font.Bold = False
        word.Selection.Font.Color = constants.wdColorAutomatic
        word.Selection.TypeParagraph()
        for entry in toc_entries:
            sec = entry.get("section", "")
            pg = entry.get("start_page", "")-start_page + 2
            word.Selection.TypeText(f"{sec}\t{pg}")
            word.Selection.TypeParagraph()
        word.Selection.InsertBreak(constants.wdPageBreak)

        # 8c) Paste the pages slice
        word.Selection.EndKey(Unit=constants.wdStory)
        word.Selection.Paste()

        # 9) Save
        out.SaveAs2(FileName=output_path)

    finally:
        # 10) Always close documents (no prompts)
        if out:
            try:
                out.Close(SaveChanges=False)
            except:
                pass
        if src:
            try:
                src.Close(SaveChanges=False)
            except:
                pass
        # 11) Quit Word & uninit COM
        try:
            word.Quit()
        except:
            pass
        pythoncom.CoUninitialize()


def slice_docx_by_pages(input_path: str, start_page: int, end_page: int, output_path: str) -> None:
    """
    Extracts pages from start_page to end_page (inclusive) from input_path
    and saves to output_path. No title or TOC is added.
    """

    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)

    # Clean up any lock files
    for path in (input_path, output_path):
        lock = os.path.join(os.path.dirname(
            path), "~$" + os.path.basename(path))
        if os.path.exists(lock):
            try:
                os.remove(lock)
            except:
                pass

    # Remove existing output file
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except PermissionError:
            os.replace(output_path, output_path + ".old")

    pythoncom.CoInitialize()
    word = DispatchEx("Word.Application")
    word.DisplayAlerts = constants.wdAlertsNone
    word.Visible = False

    src = out = None
    try:
        src = word.Documents.Open(
            input_path, ReadOnly=True, ConfirmConversions=False, AddToRecentFiles=False)

        total = src.ComputeStatistics(constants.wdStatisticPages)
        if not (1 <= start_page <= total):
            raise ValueError(f"start_page must be between 1 and {total}")
        end_page = min(end_page, total)

        # Get start and end range
        go1 = src.GoTo(What=constants.wdGoToPage,
                       Which=constants.wdGoToAbsolute, Count=start_page)
        if end_page < total:
            go2 = src.GoTo(What=constants.wdGoToPage,
                           Which=constants.wdGoToAbsolute, Count=end_page + 1)
            slice_end = go2.Start - 1
        else:
            slice_end = src.Content.End

        src.Range(Start=go1.Start, End=slice_end).Copy()

        out = word.Documents.Add()
        word.Selection.Paste()
        out.SaveAs2(FileName=output_path)

    finally:
        if out:
            try:
                out.Close(SaveChanges=False)
            except:
                pass
        if src:
            try:
                src.Close(SaveChanges=False)
            except:
                pass
        try:
            word.Quit()
        except:
            pass
        pythoncom.CoUninitialize()
