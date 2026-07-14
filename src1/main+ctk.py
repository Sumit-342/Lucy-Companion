import customtkinter as ctk
from PIL import Image
from win32 import win32gui
from win32.lib import win32con
from win32 import win32api

# =================================
# window constants
# ===================================
WINDOW_WIDTH = 360
WINDOW_HEIGHT = 450

# ===================================
# Mascot Constant 
# ===================================
MASCOT_WIDTH = 180
MASCOT_HEIGHT = 340


# Lucy Position
LUCY_X = 170
LUCY_Y = 260

# Bubble Position
BUBBLE_X = LUCY_X - 90
BUBBLE_Y = LUCY_Y - 180

BUBBLE_SIZES = {
    "small": (135, 280),
    "medium": (140, 300),
    "large": (170, 360)
}

app = ctk.CTk()

app.config(fg_color = "white")

# window settings
app.title("Lucy Companion")
app.overrideredirect(True)


# screen size
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

# window size 
window_height = 400
window_width = 300

# position calculate 
x = screen_width - window_width - 20
y = screen_height - window_height - 70



# window size +  postion
app.geometry(f"{window_width}x{window_height}+{x}+{y}")


# load image
image = Image.open("../assets/expressions/standing.png")

# ctk image
mascot = ctk.CTkImage(
    light_image=image,
    dark_image=image,
    size=(220 , 330)
)

# label
label = ctk.CTkLabel(
    app,
    image=mascot,
    text=""
)

label.place(
    x = LUCY_X,
    y = LUCY_Y,
    anchor = "center"
)

bubble_label = ctk.CTkLabel(
    app,
    text=""
)

bubble_text = ctk.CTkLabel(
    bubble_label,
    text="",
    fg_color="transparent",
    text_color="black",
    font=("Segoe UI",14),
    justify = "center"
)

bubble_text.place(
    relx = 0.48,
    rely = 0.43,
    anchor = "center"
)

bubble_label.place(
    x = BUBBLE_X + 20 ,
    y = BUBBLE_Y,
    anchor = "center"
)


def set_bubble_text(text):
    bubble_text.configure(text=text)
def show_speech_bubble(size):

    width, height = BUBBLE_SIZES[size]

    image = Image.open(f"../assets/speech/{size}.png")

    bubble = ctk.CTkImage(
        light_image=image,
        dark_image=image,
        size=(width, height)
    )

    bubble_label.configure(
        image=bubble,
        text="",
        width=width,
        height=height
    )

    bubble_label.image = bubble

    bubble_text.configure(
        wraplength=int(width * 0.7)
    )

def show_expression(expression):

    image = Image.open(f"../assets/expressions/{expression}.png")

    mascot = ctk.CTkImage(
        light_image=image,
        dark_image=image,
        size=(180, 340)
    )

    label.configure(
        image=mascot
    )

    label.image = mascot

def change_expression_after(expression , delay):
    app.after(
        delay,
        lambda : show_expression(expression)
    )

def hide_message():

    # Hide bubble
    bubble_label.configure(image = None)

    # Hide text
    bubble_text.configure(text = "")

    # Return lucy to standing 
    show_expression("thinking")


def show_message(text, expression, bubble, duration = 3000):

    # Change Lucy's expression
    show_expression(expression)

    # Show bubble
    show_speech_bubble(bubble)

    # Show text
    set_bubble_text(text)

    # Hide everthing after duration
    app.after(duration,hide_message)

def make_window_transparent():

    hwnd = win32gui.GetParent(app.winfo_id())

    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

    win32gui.SetWindowLong(
        hwnd,
        win32con.GWL_EXSTYLE,
        ex_style | win32con.WS_EX_LAYERED
    )

    win32gui.SetLayeredWindowAttributes(
        hwnd,
        win32api.RGB(255, 255, 255),
        0,
        win32con.LWA_COLORKEY
    )

show_message(
    text="its time for milk",
    expression="happy",
    bubble="medium",
    duration=3000
)
app.update()
make_window_transparent()
app.mainloop()