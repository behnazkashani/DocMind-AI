from docx import Document


def save_txt(text):

    with open("output.txt", "w", encoding="utf-8") as file:
        file.write(text)


def save_docx(text):

    doc = Document()

    doc.add_heading("Extracted Text", level=1)

    doc.add_paragraph(text)

    doc.save("output.docx")