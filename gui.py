import tkinter as tk
from tkinter import filedialog
from extractor import extract_links
from pdf_reader import read_pdf
from analyzer import statistics
from exporter import save_docx
from exporter import save_txt
from extractor import extract_emails
from extractor import extract_phones
from tkinter import ttk
from tkinter import Menu
from tkinter import messagebox

window = tk.Tk()

try:
    window.iconbitmap("assets/app_icon.ico")
except Exception as e:
    print(e)

window.title("AI PDF Assistant")

window.geometry("750x700")

window.configure(bg="#F5F7FA")

current_pdf = None
current_text = ""

menu_bar = Menu(window)

window.config(menu=menu_bar)

def update_progress(value):

    progress["value"] = value

    window.update_idletasks()


def select_pdf():

    progress["value"] = 0
    window.update_idletasks()

    global current_pdf
    global current_text

    file_path = filedialog.askopenfilename(
        title="انتخاب فایل PDF",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if file_path:

        current_pdf, current_text = read_pdf(
        file_path,
        update_progress
    )
        progress["value"] = 100
        window.update_idletasks()

        result_label.config(
            text=f"""✅ فایل با موفقیت انتخاب شد

📄 تعداد صفحات: {len(current_pdf)}

📝 تعداد کلمات: {len(current_text.split())}

🔤 تعداد کاراکترها: {len(current_text)}
"""
        )
        
        status_label.config(
    text="📊 تحلیل فایل انجام شد."
)


def export_word():

    if current_text == "":
        return

    save_docx(current_text)
    status_label.config(
    text="📝 فایل Word ذخیره شد."
)

def analyze_pdf():

    if current_pdf is None:

        result_label.config(
            text="❌ ابتدا یک فایل PDF انتخاب کنید."
        )

        return

    words = current_text.split()

    reading_time = round(len(words) / 200, 2)

    result_label.config(
        text=f"""📊 تحلیل فایل

📄 تعداد صفحات: {len(current_pdf)}

📝 تعداد کلمات: {len(words)}

🔤 تعداد کاراکترها: {len(current_text)}

⏱️ زمان مطالعه: {reading_time} دقیقه
"""
    )


def export_txt():

    if current_text == "":
        return

    save_txt(current_text)  
    status_label.config(
    text="💾 فایل TXT ذخیره شد."
)  

def show_emails():

    if current_text == "":

        result_label.config(
            text="❌ ابتدا یک فایل PDF انتخاب کنید."
        )

        return

    emails = extract_emails(current_text)

    if len(emails) == 0:

        result_label.config(
            text="📭 هیچ ایمیلی پیدا نشد."
        )

    else:

        result_label.config(
            text="📧 ایمیل‌های پیدا شده:\n\n" +
                 "\n".join(emails)
        )
    status_label.config(
    text=f"📧 {len(emails)} ایمیل پیدا شد."
)
def show_links():

    if current_text == "":

        result_label.config(
            text="❌ ابتدا یک فایل PDF انتخاب کنید."
        )

        return

    links = extract_links(current_text)

    if len(links) == 0:

        result_label.config(
            text="🌐 هیچ لینکی پیدا نشد."
        )

    else:

        result_label.config(
            text="🌐 لینک‌های پیدا شده:\n\n" +
                 "\n".join(links)
        )
    status_label.config(
    text=f"🌐 {len(links)} لینک پیدا شد."
)
def show_phones():

    if current_text == "":

        result_label.config(
            text="❌ ابتدا یک فایل PDF انتخاب کنید."
        )

        return

    phones = extract_phones(current_text)

    if len(phones) == 0:

        result_label.config(
            text="📞 هیچ شماره‌ای پیدا نشد."
        )

    else:

        result_label.config(
            text="📞 شماره‌های پیدا شده:\n\n" +
                 "\n".join(phones)
        )

def about():

    messagebox.showinfo(
        "About",
        "AI PDF Assistant\nVersion 1.0\nDeveloped by Behnaz Kashani"
    )


file_menu = Menu(menu_bar, tearoff=0)

menu_bar.add_cascade(label="File", menu=file_menu)

file_menu.add_command(label="Open PDF", command=select_pdf)

file_menu.add_separator()

file_menu.add_command(label="Save Word", command=export_word)

file_menu.add_command(label="Save TXT", command=export_txt)

file_menu.add_separator()

file_menu.add_command(label="Exit", command=window.destroy)


tools_menu = Menu(menu_bar, tearoff=0)

menu_bar.add_cascade(label="Tools", menu=tools_menu)

tools_menu.add_command(label="Analyze PDF", command=analyze_pdf)

tools_menu.add_command(label="Extract Emails", command=show_emails)

tools_menu.add_command(label="Extract Links", command=show_links)

tools_menu.add_command(label="Extract Phones", command=show_phones)

help_menu = Menu(menu_bar, tearoff=0)

menu_bar.add_cascade(label="Help", menu=help_menu)

help_menu.add_command(label="About", command=about)

title = tk.Label(
    window,
    text="AI PDF Assistant",
    font=("Arial", 24, "bold"),
    bg="#F5F7FA",
    fg="#0B5394"
)

title.pack(pady=20)    

subtitle = tk.Label(
    window,
    text="Professional PDF Analyzer",
    font=("Arial", 12),
    bg="#F5F7FA",
    fg="gray"
)

subtitle.pack(pady=5)

button_frame = tk.Frame(
    window,
    bg="#F5F7FA"
)

button_frame.pack(pady=20)

progress = ttk.Progressbar(
    window,
    orient="horizontal",
    length=500,
    mode="determinate"
)

progress.pack(pady=10)

select_button = tk.Button(
    button_frame,
    text="📂 انتخاب PDF",
    font=("Arial", 13),
    bg="#4CAF50",
    fg="white",
    width=20,
    command=select_pdf
)

select_button.grid(row=0, column=0, padx=10, pady=10)

analysis_button = tk.Button(
    button_frame,
    text="📊 تحلیل PDF",
    font=("Arial", 13),
    bg="#2196F3",
    fg="white",
    width=20,
    command=analyze_pdf
)

analysis_button.grid(row=0, column=1, padx=10, pady=10)

word_button = tk.Button(
    button_frame,
    text="📝 ذخیره Word",
    font=("Arial", 13),
    bg="#FF9800",
    fg="white",
    width=20,
    command=export_word
)

word_button.grid(row=1, column=0, padx=10, pady=10)

txt_button = tk.Button(
    button_frame,
    text="💾 ذخیره TXT",
    font=("Arial", 13),
    bg="#9C27B0",
    fg="white",
    width=20,
    command=export_txt
)

txt_button.grid(row=1, column=1, padx=10, pady=10)

email_button = tk.Button(
    button_frame,
    text="📧 استخراج ایمیل",
    font=("Arial", 13),
    bg="#009688",
    fg="white",
    width=20,
    command=show_emails
)

email_button.grid(row=2, column=0, padx=10, pady=10)

link_button = tk.Button(
    button_frame,
    text="🌐 استخراج لینک",
    font=("Arial", 13),
    bg="#3F51B5",
    fg="white",
    width=20,
    command=show_links
)

link_button.grid(row=3, column=0, padx=10, pady=10)

phone_button = tk.Button(
    button_frame,
    text="📞 استخراج شماره",
    font=("Arial", 13),
    bg="#795548",
    fg="white",
    width=20,
    command=show_phones
)

phone_button.grid(row=2, column=1, padx=10, pady=10)

exit_button = tk.Button(
    button_frame,
    text="❌ خروج",
    font=("Arial", 13),
    bg="#F44336",
    fg="white",
    width=20,
    command=window.destroy
)


exit_button.grid(row=3, column=1, padx=10, pady=10)

result_frame = tk.Frame(
    window,
    bg="white",
    bd=2,
    relief="groove"
)

result_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)

result_label = tk.Label(
    result_frame,
    text="📄 هنوز فایلی انتخاب نشده است.",
    font=("Arial", 12),
    bg="white",
    fg="#333333",
    justify="left",
    anchor="nw"
)

result_label.pack(
    padx=15,
    pady=15,
    anchor="nw"
)

status_label = tk.Label(
    window,
    text="✅ آماده",
    bd=1,
    relief="sunken",
    anchor="w",
    font=("Arial", 10),
    bg="#ECECEC"
)

status_label.pack(
    side="bottom",
    fill="x"
)


window.mainloop()