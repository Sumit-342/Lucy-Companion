import customtkinter as ctk
from PIL import Image

# =================================
# window constants
# ===================================
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 400

# ===================================
# Mascot Constant 
# ===================================
MASCOT_WIDTH = 180
MASCOT_HEIGHT = 340

app = ctk.CTk()

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
image = Image.open("../assets/standing.png")

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

label.pack(expand = True)


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


show_expression("happy")

change_expression_after("thinking",2000)
change_expression_after("sleepy",5000)
change_expression_after("laughing",8000)

app.mainloop()