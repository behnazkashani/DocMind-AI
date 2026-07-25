import fitz


from pypdf import PdfReader

def read_pdf(file_path, progress_callback=None):

    reader = PdfReader(file_path)

    text = ""

    total_pages = len(reader.pages)

    for i, page in enumerate(reader.pages):

        page_text = page.extract_text()

        if page_text:
            text += page_text

        if progress_callback:
            percent = int(((i + 1) / total_pages) * 100)
            progress_callback(percent)

    return reader.pages, text