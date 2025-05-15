# Add the parent directory to sys.path
import os 
import sys 


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def import_custom():
    from ..normalize import format_content_for_toc_endpage_extraction
    return  format_content_for_toc_endpage_extraction


format_content_for_toc_endpage_extraction = import_custom()


def extract_toc_endpage(page_contents):

    page_contents = format_content_for_toc_endpage_extraction(page_contents)
    toc_end_prompt = f"""
    Analyze these pages and identify which page number the Table of Contents ends on.
    Look for these indicators:
    1. Change in content structure from list-like TOC format to regular content
    2. End of section/chapter listings
    3. Start of actual document content
    
    Return ONLY the page number (0-based index) where TOC ends. Just the number, no other text.

    Document Pages:
    {page_contents}
    """

    try:
        toc_end_response = client.chat.completions.create(
            messages=[{"role": "user", "content": toc_end_prompt}],
            model="gpt-4o-mini",
        )
        toc_end_page = int(toc_end_response.choices[0].message.content.strip())
        # print('toc_end_page', toc_end_page)
    except Exception as e:
        print(f"⚠️ Error detecting TOC end page: {e}")
        toc_end_page = 0

    return toc_end_page
