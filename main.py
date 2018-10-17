import tkinter as tk
from WeDi import services
import sys
import threading
import pickle
import os

# self.loadimage = tk.PhotoImage(file="rounded_button.png")
# self.roundedbutton = tk.Button(self, image=self.loadimage)
# self.roundedbutton["bg"] = "white"
# self.roundedbutton["border"] = "0"

class GUI:
    def __init__(self):
        try:
            self.settings = pickle.load(open('settings.sav', 'rb'))
        except:
            self.settings = self.default_settings()
        self.format_dict = {"Best video quality":'best', "Worst video quality":'worst', "Only video (no audio)":'bestvideo'}
        self.inv_format_dict = {v: k for k, v in self.format_dict.items()}
        self.bg_color = '#e6e6ff'
        self.green_color = '#4af441'
        self.button_color = '#ffffe6'
        title_font = ("calibri", 25)
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

        self.whitebutton = tk.PhotoImage(file=os.path.join('textures', 'wdocimg.gif'))
        self.greenbutton = tk.PhotoImage(file=os.path.join('textures', 'green_button.gif'))

        self.start_frame = tk.Frame(self.root, bg=self.bg_color)
        self.start_frame2 = tk.Frame(self.root, bg=self.bg_color)
        self.body_frame = tk.Frame(self.root, bg=self.bg_color)
        self.end_frame = tk.Frame(self.root, bg=self.bg_color)

        self.title = tk.Label(self.start_frame, text="WeDi", font=title_font, bg=self.bg_color, pady=35)
        self.title.pack(side='top')
        self.siteEntry = tk.Entry(self.start_frame, width=box_width+25, font=font)
        self.siteEntry.pack(side='top')
        try:
            clipboard = self.root.clipboard_get()
        except:
            clipboard = ""
        if len(clipboard) > 10 and clipboard[:4] == 'http':
            self.siteEntry.insert(0, clipboard)
        tk.Button(self.start_frame, text=" X ", font=font, bg=self.button_color, width=5, command=self.clear_site).pack(side='right')
        tk.Button(self.start_frame, text=" P ", font=font, bg=self.button_color, width=5, command=self.paste_site).pack(side='right')
        tk.Label(self.start_frame2, text="Choose what you want to download", font=font, padx=20, pady=20, bg=self.bg_color).pack(side='top')
# self.loadimage = tk.PhotoImage(file="rounded_button.png")
# self.roundedbutton = tk.Button(self, image=self.loadimage)
# self.roundedbutton["bg"] = "white"
# self.roundedbutton["border"] = "0"

        color = self.button_color
        if self.settings['documents']['run']:
            color = self.green_color
        self.doc_button = tk.Button(self.body_frame, image=self.whitebutton, border=0, bg=self.bg_color, activebackground=self.bg_color, command=self.on_documents)
        #self.doc_button = tk.Button(self.body_frame, text="Documents", font=font, bg=color, width=box_width, command=self.on_documents)
        self.doc_button.grid(row=0, column=0, padx=20, pady=10)
        color = self.button_color
        if self.settings['images']['run']:
            color = self.green_color
        self.img_button = tk.Button(self.body_frame, text="Images", font=font, bg=color, width=box_width, command=self.on_images)
        self.img_button.grid(row=0, column=1, padx=20, pady=10)
        color = self.button_color
        if self.settings['audios']['run']:
            color = self.green_color
        self.aud_button = tk.Button(self.body_frame, text="Audios", font=font, bg=color, width=box_width, command=self.on_audios)
        self.aud_button.grid(row=1, column=0, padx=20, pady=10)
        color = self.button_color
        if self.settings['dev']['run']:
            color = self.green_color
        self.dev_button = tk.Button(self.body_frame, text="Analytics", font=font, bg=color, width=box_width, command=self.on_analytics)
        self.dev_button.grid(row=1, column=1, padx=20, pady=10)
        color = self.button_color
        if self.settings['videos']['run']:
            color = self.green_color
        self.vid_button = tk.Button(self.body_frame, text="Videos", font=font, bg=color, width=box_width, command=self.on_videos)
        self.vid_button.grid(row=2, column=0, padx=20, pady=10)

        def set_format(value):
            self.settings['videos']['format'] = self.format_dict[value]
        formats = ["Best video quality", "Worst video quality", "Only video (no audio)"]
        self.option = tk.StringVar()
        self.option.set(self.inv_format_dict[self.settings['videos']['format']])
        self.options = tk.OptionMenu(self.body_frame, self.option, *formats, command=set_format)  # creates drop down menu
        self.options.config(bg = self.button_color, fg='black', font=font, width=box_width-4)
        self.options["menu"].config(bg=self.button_color, font=font, fg='black')
        self.options.grid(row=2, column=1)

        self.run_button = tk.Button(self.end_frame, text='Run', font=font, bg=self.button_color, padx=50, pady=10, command=self.on_run)
        self.run_button.pack(side='left', padx=50, pady=30)
        self.button = tk.Button(self.end_frame, text='Exit', font=font, bg=self.button_color, padx=50, pady=10, command=self.on_close)
        self.button.pack(side='left', padx=50, pady=30)

        self.start_frame.pack(side="top")
        self.start_frame2.pack(side="top")
        self.body_frame.pack()
        self.end_frame.pack(side="bottom")

        tk.mainloop()

    def clear_site(self):
        self.siteEntry.delete(0, "end")

    def paste_site(self):
        self.siteEntry.delete(0, "end")
        try:
            clipboard = self.root.clipboard_get()
        except:
            clipboard = ""
        if len(clipboard) > 10 and clipboard[:4] == 'http':
            self.siteEntry.insert(0, clipboard)

    def on_close(self):
        self.root.quit()
        sys.exit(1)

    def on_videos(self):
        self.settings['videos']['run'] = not self.settings['videos']['run']
        if self.settings['videos']['run']:
            self.vid_button['bg'] = self.green_color
        else:
            self.vid_button['bg'] = self.button_color

    def on_documents(self):
        self.settings['documents']['run'] = not self.settings['documents']['run']
        if self.settings['documents']['run']:
            self.doc_button['image'] = self.greenbutton
        else:
            self.doc_button['image'] = self.whitebutton

    def on_images(self):
        self.settings['images']['run'] = not self.settings['images']['run']
        if self.settings['images']['run']:
            self.img_button['bg'] = self.green_color
        else:
            self.img_button['bg'] = self.button_color

    def on_audios(self):
        self.settings['audios']['run'] = not self.settings['audios']['run']
        if self.settings['audios']['run']:
            self.aud_button['bg'] = self.green_color
        else:
            self.aud_button['bg'] = self.button_color

    def on_analytics(self):
        self.settings['dev']['run'] = not self.settings['dev']['run']
        if self.settings['dev']['run']:
            self.dev_button['bg'] = self.green_color
        else:
            self.dev_button['bg'] = self.button_color

    def about(self):
        tk.messagebox.showinfo("About", "WeDi (Web Dissector) is...")

    def default_settings(self):
        path = "."
        img_types = ['jpg', 'jpeg', 'png', 'gif']
        doc_types = ['py', 'txt', 'java', 'php', 'pdf', 'md', 'gitignore', 'c']
        vid_types = ['mp4', 'avi', 'mpeg', 'mpg', 'wmv', 'mov', 'flv', 'swf', 'mkv', '3gp']
        aud_types = ['mp3', 'aac', 'wma', 'wav']
        img_settings = {'run':True, 'img_types':img_types}
        doc_settings = {'run':True, 'doc_types':doc_types}
        vid_settings = {'run':True, 'vid_types':vid_types, 'format':'best'}
        aud_settings = {'run':True, 'aud_types':aud_types}
        dev_settings = {'run':True}
        settings = {'path':path, 'images':img_settings, 'documents':doc_settings, 'videos':vid_settings, 'audios':aud_settings, 'dev':dev_settings}
        pickle.dump(settings, open('settings.sav', 'wb'))
        return settings

    def on_run(self):
        site = self.siteEntry.get()
        if len(site) > 10 and site[:4] == 'http':
            pickle.dump(self.settings, open('settings.sav', 'wb'))
            thread = threading.Thread(target= services, args=(site, self.settings, ))
            thread.daemon = True
            thread.start()
        else:
            print("Enter site!")

if __name__ == '__main__':
    GUI()
