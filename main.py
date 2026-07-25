from tkinter import Tk
from tkinter.filedialog import askopenfilename

from pdf_reader import read_pdf
from exporter import save_txt, save_docx
from analyzer import statistics


root = Tk()
root.withdraw()

file_path = askopenfilename(
    title="Select PDF",
    filetypes=[("PDF Files", "*.pdf")]
)

pdf, text = read_pdf(file_path)

statistics(pdf, text)

save_txt(text)

save_docx(text)

print("پروژه با موفقیت اجرا شد.")