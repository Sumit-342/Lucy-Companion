import customtkinter as ctk
from PIL import Image

app = ctk.CTk()

app.title("Lucy Companion")
app.geometry("300x400")

image = Image.open("../assets/standing.png")

mascot = ctk.CTkImage(
    light_image=image,
    dark_image=image,
    size=(240 , 360)
)

label = ctk.CTkLabel(
    app,
    image=mascot,
    text=""
)

label.pack(expand = True)



app.mainloop()