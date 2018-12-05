try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    import Tkinter as tk
    from Tkinter import filedialog
import os, sys
from PIL import Image, ImageTk
import math
import pickle

class settings_GUI:
    def __init__(self, settings_filepath):
        self.settings = pickle.load(open(settings_filepath, 'rb'))
        print(self.settings)
        self.createGUI()
        self.mainloop()

    def createGUI(self):
        self.bg_color = '#e6e6ff'
        font = ('calibri', 13)
        title_font = ('calibri', 16)
        self.top = tk.Toplevel(bg=self.bg_color)
        self.top.title("Settings")
        self.top.wm_protocol("WM_DELETE_WINDOW", self.on_close)
        self.top.resizable(False, False)

        self.headerFrame = tk.Frame(self.top, bg=self.bg_color)
        self.bodyFrame = tk.Frame(self.top, bg=self.bg_color)
        self.buttonsFrame = tk.Frame(self.top, bg=self.bg_color)
        self.headerFrame.pack()
        self.bodyFrame.pack()
        self.buttonsFrame.pack()

        #Header frame combonents
        sub_frame = tk.Frame(self.bodyFrame, bg=self.bg_color)
        sub_frame.pack()
        width = 50
        tk.Label(self.headerFrame, text="General settings",\
            bg=self.bg_color, font=title_font).pack()
        #Body frame combonents
        self.download_path_entry = tk.Entry(sub_frame, width=width, font=font)
        self.download_path_entry.insert(0, self.settings["path"])
        self.download_path_entry.pack(side="left")
        tk.Button(sub_frame, text="Browse", command=self.on_browse).pack(side="left")

        tk.Label(self.bodyFrame, text="Documents types:", font=font,\
            bg=self.bg_color, anchor="w").pack()
        self.doc_entry = tk.Entry(self.bodyFrame, width=width, font=font)
        self.insert_list(self.doc_entry, self.settings["documents"]["doc_types"])
        self.doc_entry.pack()
        tk.Label(self.bodyFrame, text="Images types:", font=font,\
            bg=self.bg_color, anchor="w").pack()
        self.img_entry = tk.Entry(self.bodyFrame, width=width, font=font)
        self.insert_list(self.img_entry, self.settings["images"]["img_types"])
        self.img_entry.pack()
        tk.Label(self.bodyFrame, text="Audios types:", font=font,\
            bg=self.bg_color, anchor="w").pack()
        self.aud_entry = tk.Entry(self.bodyFrame, width=width, font=font)
        self.insert_list(self.aud_entry, self.settings["audios"]["aud_types"])
        self.aud_entry.pack()
        tk.Label(self.bodyFrame, text="Videos types:", font=font,\
            bg=self.bg_color, anchor="w").pack()
        self.vid_entry = tk.Entry(self.bodyFrame, width=width, font=font)
        self.insert_list(self.vid_entry, self.settings["videos"]["vid_types"])
        self.vid_entry.pack()

        #Buttons frame combonents
        padx = 10
        pady = 10
        button_color = '#ffffe6'
        buttonimg = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'button.png')))
        okButton = tk.Button(self.buttonsFrame, text="Ok", font=font,\
                            image=buttonimg, border=0, highlightthickness=0,\
                            bg=self.bg_color, activebackground=self.bg_color,\
                            compound=tk.CENTER, command=self.on_ok)
        okButton.photo = buttonimg
        okButton.pack(side="left", padx=padx, pady=pady)
        defaultsButton = tk.Button(self.buttonsFrame, text="Restore defaults",\
                            image=buttonimg, border=0, highlightthickness=0,\
                            bg=self.bg_color, activebackground=self.bg_color,\
                            compound=tk.CENTER, font=font, command=self.on_default)
        defaultsButton.photo = buttonimg
        defaultsButton.pack(side="left", padx=padx, pady=pady)
        cancelButton = tk.Button(self.buttonsFrame, text="Cancel", font=font,\
                            image=buttonimg, border=0, highlightthickness=0,\
                            bg=self.bg_color, activebackground=self.bg_color,\
                            compound=tk.CENTER, command=self.on_close)
        cancelButton.photo = buttonimg
        cancelButton.pack(side="left", padx=padx, pady=pady)

    def insert_list(self, combonent, list_):
        text = ""
        for elem in list_:
            text += elem + ", "
        text = text[:-2]
        combonent.insert(0, text)

    def on_close(self):
        self.top.destroy()

    def mainloop(self):
        tk.mainloop()

    def on_ok(self):
        print("OK pressed")

    def on_default(self):
        path = "."
        img_types = ['jpg', 'jpeg', 'png', 'gif', 'svg']
        doc_types = ['txt', 'py', 'java', 'php', 'pdf', 'md', 'gitignore', 'c']
        vid_types = ['mp4', 'avi', 'mpeg', 'mpg', 'wmv', 'mov', 'flv', 'swf', 'mkv', '3gp', 'webm', 'ogg']
        aud_types = ['mp3', 'aac', 'wma', 'wav', 'm4a']
        self.doc_entry.delete(0, "end")
        self.img_entry.delete(0, "end")
        self.aud_entry.delete(0, "end")
        self.vid_entry.delete(0, "end")
        self.insert_list(self.doc_entry, doc_types)
        self.insert_list(self.img_entry, img_types)
        self.insert_list(self.aud_entry, aud_types)
        self.insert_list(self.vid_entry, vid_types)

    def on_browse(self):
        filename = filedialog.askdirectory()
        self.download_path_entry.delete(0, "end")
        self.download_path_entry.insert(0, filename)

if __name__ == '__main__':
    settings_GUI('settings.sav')
