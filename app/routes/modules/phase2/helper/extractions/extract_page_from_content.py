from ..models import TocEntries
from ..openai_client import client
import os
from .extract_toc_endpage import extract_toc_endpage
from ..normalize import format_toccontent_for_tocpage


def extract_page_from_content(page_contents, sections):
    """
    Extract the table of contents from non-TOC pages.
    """
    toc_end_page = extract_toc_endpage(page_contents)
    document_text = format_toccontent_for_tocpage(page_contents, toc_end_page)

    prompt_path = os.path.join(os.path.dirname(
        __file__), "../prompts/extract_page_from_content.txt")

    with open(prompt_path, "r", encoding="utf-8") as f:
        instructions = f.read()

    toc_lines = [f" {i+1}. {entry['section']}" for i,
                 entry in enumerate(sections)]

    toc_block = "- Toc Entries given as:\n" + "\n".join(toc_lines)

    doc_block = "- Document Text given as:\n" + document_text

    try:
        response = client.responses.parse(
            instructions=instructions,
            input=[{"role": "user", "content": f"{toc_block}\n\n{doc_block}"}],
            model="gpt-4o-mini",
            temperature=0,
            text_format=TocEntries,
        )

        response_content = response.output_parsed
        return [
            {"section": entry.name, "start_page": int(entry.page_number)}
            for entry in response_content.entries
        ]

    except Exception as e:
        print(f"⚠️ Error extracting TOC with GPT: {e}")
        raise Exception(
            f"Error extracting TOC with GPT: {e}. Please check the PDF content and try again."
        )
