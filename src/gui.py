from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, StringVar
from main import TranslationApp

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()
translator = TranslationApp()
translation_direction = "en_to_ilo"

window.configure(bg="#F1F6FF")

# Center the Window Screen
window_width = 788
window_height = 677

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x_position = (screen_width // 2) - (window_width // 2)
y_position = (screen_height // 2) - (window_height // 2)

window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
window.title("Translation App")

canvas = Canvas(
    window,
    bg="#F1F6FF",
    height=677,
    width=788,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

canvas.create_text(
    45.0,
    29.0,
    anchor="nw",
    text="SOLAD",
    fill="#2D2D2D",
    font=("Poppins Bold", 24 * -1)
)

# Main Translation Container
main_container = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(394.0, 275.0, image=main_container)

# Dictionary Container
dictionary_container = PhotoImage(file=relative_to_assets("image_2.png"))
canvas.create_image(394.0, 559.0, image=dictionary_container)

# Translation English Label
english_label = canvas.create_text(
    69.0,
    106.0,
    anchor="nw",
    text="ENGLISH",
    fill="#4980F2",
    font=("Poppins SemiBold", 16 * -1)
)

# Translation Ilocano Label
ilocano_label = canvas.create_text(
    420.0,
    106.0,
    anchor="nw",
    text="ILOCANO",
    fill="#4980F2",
    font=("Poppins SemiBold", 16 * -1)
)

# Lines
image_data = [
    ("image_3.png", 393.0, 139.0),
    ("image_4.png", 393.0, 540.0),
    ("image_5.png", 393.0, 300.0),
]

loaded_images = []

for filename, x, y in image_data:
    img = PhotoImage(file=relative_to_assets(filename))
    canvas.create_image(x, y, image=img)
    loaded_images.append(img)

# Dictionary Label
canvas.create_text(
    69.0,
    499.0,
    anchor="nw",
    text="Dictionary",
    fill="#4980F2",
    font=("Poppins SemiBold", 16 * -1)
)

# Search Bar Background
search_bar = PhotoImage(file=relative_to_assets("image_6.png"))
canvas.create_image(593.0, 511.0, image=search_bar)

# Search Text Field
entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
canvas.create_image(580.0, 511.11111068725586, image=entry_image_1)

entry_1 = Entry(
    bd=0,
    bg="#F3F3F3",
    fg="#000716",
    highlightthickness=0,
    relief="flat",
    insertbackground="#000716",
    font=("Poppins", 10),
)
entry_1.place(x=491.0, y=503.0, width=178, height=18)

# Placeholder logic for search bar
search_placeholder = "Search for a word..."


def on_entry1_focus_in(event):
    if entry_1.get() == search_placeholder:
        entry_1.delete(0, "end")
        entry_1.config(fg="#000000")


def on_entry1_focus_out(event):
    if entry_1.get().strip() == "":
        entry_1.insert(0, search_placeholder)
        entry_1.config(fg="#A9A9A9")  # light gray


entry_1.insert(0, search_placeholder)
entry_1.config(fg="#A9A9A9")  # light gray text

entry_1.bind("<FocusIn>", on_entry1_focus_in)
entry_1.bind("<FocusOut>", on_entry1_focus_out)

# Character Counter
char_count = StringVar()
char_count.set("0 / 275")

char_count_text = canvas.create_text(
    92.0,
    417.0,
    anchor="nw",
    text=char_count.get(),
    fill="#000000",
    font=("Poppins Regular", 16 * -1),
    tags="char_count_text"
)

# Text areas
# FROM Language Text Language
entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
canvas.create_image(220.5, 275.5, image=entry_image_2)

entry_2 = Text(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=("Poppins", 12),
    wrap="word",
)
entry_2.place(x=64.0, y=150.0, width=313.0, height=249.0)

# TO Language Text Language
entry_image_3 = PhotoImage(file=relative_to_assets("entry_3.png"))
canvas.create_image(565.5, 275.5, image=entry_image_3)

entry_3 = Text(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=("Poppins", 12)
)
# Allow viewing results - change from disabled to normal
entry_3.config(state="normal")
entry_3.place(x=409.0, y=150.0, width=313.0, height=249.0)


# Functions
def update_char_count(*args):
    text_content = entry_2.get("1.0", "end-1c")
    text_length = len(text_content)
    char_count.set(f"{text_length} / 275")
    canvas.itemconfig(char_count_text, text=char_count.get())

    # Prevent typing beyond the limit
    if text_length >= 275:
        entry_2.bind("<Key>", prevent_input)
    else:
        entry_2.unbind("<Key>")


def prevent_input(event):
    if event.keysym not in ("BackSpace", "Delete"):
        return "break"


entry_2.bind("<KeyRelease>", update_char_count)


# In the translate_text function, change this:
def translate_text():
    text = entry_2.get("1.0", "end-1c").strip()
    if text:
        is_reversed = translation_direction == "ilo_to_en"  # Remove this line
        try:
            print(f"Translating: '{text}'")  # Removed reversed parameter
            translation, pos_tags, parse_tree = translator.translate(text)  # Removed is_reversed
            print(f"Translation result: '{translation}'")

            entry_3.config(state="normal")
            entry_3.delete("1.0", "end")
            entry_3.insert("1.0", translation)
        except Exception as e:
            print(f"Translation error: {e}")
            entry_3.config(state="normal")
            entry_3.delete("1.0", "end")
            entry_3.insert("1.0", f"Translation error: {e}")


def clear_entries(event=None):
    entry_2.delete("1.0", "end")
    entry_3.config(state="normal")
    entry_3.delete("1.0", "end")
    char_count.set("0 / 275")
    canvas.itemconfig(char_count_text, text=char_count.get())


# Translate Button
button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=translate_text,
    relief="flat"
)
button_1.place(x=255.0, y=411.0, width=121.0, height=36.0)

# Switch Icon
image_switch_icon = PhotoImage(file=relative_to_assets("image_7.png"))
switch_icon = canvas.create_image(393.0, 117.0, image=image_switch_icon)

# Trash Icon
image_trash_icon = PhotoImage(file=relative_to_assets("image_8.png"))
trash_icon = canvas.create_image(71.0, 428.0, image=image_trash_icon)
# Functionality
canvas.tag_bind(trash_icon, "<Button-1>", clear_entries)


def search_dictionary(event=None):
    word = entry_1.get().strip().lower()

    if word and word != search_placeholder.lower():
        try:
            meaning, direction = translator.word_translator.lookup(word)

            print(f"Dictionary lookup: '{word}' -> '{meaning}'")

            # Since we're unidirectional, always show English to Ilocano
            canvas.itemconfig(dictionary_from, text="ENGLISH")
            canvas.itemconfig(dictionary_to, text="ILOCANO")

            canvas.itemconfig(search_word_text, text=word.capitalize())
            canvas.itemconfig(translation_word_text, text=meaning.capitalize())

        except Exception as e:
            print(f"Dictionary lookup error: {e}")
            canvas.itemconfig(search_word_text, text="Error")
            canvas.itemconfig(translation_word_text, text=str(e))
    else:
        canvas.itemconfig(search_word_text, text="")
        canvas.itemconfig(translation_word_text, text="Please enter a word")


# Search Icon
image_search_icon = PhotoImage(file=relative_to_assets("image_9.png"))
search_icon = canvas.create_image(695.0, 510.0, image=image_search_icon)
# Functionality
canvas.tag_bind(search_icon, "<Button-1>", search_dictionary)

# Dictionary FROM Language Label
dictionary_from = canvas.create_text(
    69.0,
    551.0,
    anchor="nw",
    text="",
    fill="#4980F2",
    font=("Poppins SemiBold", 16 * -1)
)

# Dictionary TO Language Label
dictionary_to = canvas.create_text(
    409.0,
    551.0,
    anchor="nw",
    text="",
    fill="#4980F2",
    font=("Poppins SemiBold", 16 * -1)
)

# Search Word
search_word_text = canvas.create_text(
    69.0,
    581.0,
    anchor="nw",
    text="",
    fill="#000000",
    font=("Poppins", 16 * -1),
    tags="search_word_text"
)

# Translation Word
translation_word_text = canvas.create_text(
    409.0,
    581.0,
    anchor="nw",
    text="",
    fill="#000000",
    font=("Poppins", 16 * -1),
    tags="translation_word_text"
)

# Add debugging for dictionary structure at startup
print("Dictionary structure:", type(translator.translator.dictionary))
if isinstance(translator.translator.dictionary, dict):
    print(f"Dictionary keys: {translator.translator.dictionary.keys()}")

    # Print a few sample entries to check format
    if 'english_to_ilokano' in translator.translator.dictionary:
        sample = list(translator.translator.dictionary['english_to_ilokano'].items())[:3]
        print(f"Sample English->Ilokano entries: {sample}")
    elif len(translator.translator.dictionary) > 0:
        sample = list(translator.translator.dictionary.items())[:3]
        print(f"Sample dictionary entries: {sample}")

window.resizable(False, False)
window.mainloop()