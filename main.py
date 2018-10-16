import tkinter as tk
import WeDi
import sys

class GUI:
    def __init__(self):
        self.vid_run = False
        self.doc_run = False
        self.img_run = False
        self.dev_run = False
        self.aud_run = False

        self.bg_color = '#e6e6ff'
        self.green_color = '#4af441'
        self.button_color = '#ffffe6'
        title_font = ("calibri", 20)
        font = ('calibri', 13)
        box_width = 40
        self.root = tk.Tk()
        self.root.configure(background=self.bg_color)
        self.root.title("WeDi")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)

        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        helpmenu = tk.Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=self.about)


        self.start_frame = tk.Frame(self.root, bg=self.bg_color)
        self.body_frame = tk.Frame(self.root, bg=self.bg_color)
        self.end_frame = tk.Frame(self.root, bg=self.bg_color)

        self.title = tk.Label(self.start_frame, text="WeDi", font=title_font, bg=self.bg_color, pady=35)
        self.title.pack(side='top')
        self.siteEntry = tk.Entry(self.start_frame, width=box_width+25, font=font)
        self.siteEntry.pack(side='top')
        clipboard = self.root.clipboard_get()
        if len(clipboard) > 4 and clipboard[:4] == 'http':
            self.siteEntry.insert(0, clipboard)
        tk.Button(self.start_frame, text=" X ", font=font, bg=self.button_color, width=5, command=self.clear_site).pack(side='right')
        tk.Label(self.start_frame, text="Choose what you want to download", font=font, padx=20, pady=20, bg=self.bg_color).pack(side='top')

        self.doc_button = tk.Button(self.body_frame, text="Documents", font=font, bg=self.button_color, width=box_width, command=self.on_documents)
        self.doc_button.grid(row=0, column=0, padx=20, pady=10)
        self.img_button = tk.Button(self.body_frame, text="Images", font=font, bg=self.button_color, width=box_width, command=self.on_images)
        self.img_button.grid(row=0, column=1, padx=20, pady=10)
        self.aud_button = tk.Button(self.body_frame, text="Audios", font=font, bg=self.button_color, width=box_width, command=self.on_audios)
        self.aud_button.grid(row=1, column=0, padx=20, pady=10)
        self.dev_button = tk.Button(self.body_frame, text="Analytics", font=font, bg=self.button_color, width=box_width, command=self.on_analytics)
        self.dev_button.grid(row=1, column=1, padx=20, pady=10)
        self.vid_button = tk.Button(self.body_frame, text="Videos", font=font, bg=self.button_color, width=box_width, command=self.on_videos)
        self.vid_button.grid(row=2, column=0, padx=20, pady=10)

        def set_format(value):
            self.vid_format = value
        formats = ["Best video quality", "Worst video quality", "Only video (no audio)"]
        self.option = tk.StringVar()
        self.option.set(formats[0]) #from setting TODO
        self.options = tk.OptionMenu(self.body_frame, self.option, *formats, command=set_format)  # creates drop down menu
        self.options.config(bg = self.button_color, fg='black', font=font, width=box_width-4)
        self.options["menu"].config(bg=self.button_color, font=font, fg='black')
        self.options.grid(row=2, column=1)



        self.run_button = tk.Button(self.end_frame, text='Run', font=font, bg=self.button_color, padx=50, pady=10, command=self.on_run)
        self.run_button.pack(side='left', padx=50, pady=30)
        self.button = tk.Button(self.end_frame, text='Exit', font=font, bg=self.button_color, padx=50, pady=10, command=self.on_close)
        self.button.pack(side='left', padx=50, pady=30)

        self.start_frame.pack(side="top")
        self.body_frame.pack()
        self.end_frame.pack(side="bottom")

        tk.mainloop()

    def clear_site(self):
        self.siteEntry.delete(0, "end")

    def on_close(self):
        self.root.quit()
        sys.exit(1)

    def on_videos(self):
        self.vid_run = not self.vid_run
        if self.vid_run:
            self.vid_button['bg'] = self.green_color
        else:
            self.vid_button['bg'] = self.button_color

    def on_documents(self):
        self.doc_run = not self.doc_run
        if self.doc_run:
            self.doc_button['bg'] = self.green_color
        else:
            self.doc_button['bg'] = self.button_color

    def on_images(self):
        self.img_run = not self.img_run
        if self.img_run:
            self.img_button['bg'] = self.green_color
        else:
            self.img_button['bg'] = self.button_color

    def on_audios(self):
        self.aud_run = not self.aud_run
        if self.aud_run:
            self.aud_button['bg'] = self.green_color
        else:
            self.aud_button['bg'] = self.button_color

    def on_analytics(self):
        self.dev_run = not self.dev_run
        if self.dev_run:
            self.dev_button['bg'] = self.green_color
        else:
            self.dev_button['bg'] = self.button_color

    def about(self):
        messagebox.showinfo("About", "WeDi (Web Dissector) is...")

    def on_run(self):
        print("run wedi")

if __name__ == '__main__':
    GUI()
