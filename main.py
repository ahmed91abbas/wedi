try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import sys
import pickle
import os
import runGUI
from PIL import Image, ImageTk

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
        font = ('calibri', 13)
        menufont = ('calibri', 16, 'bold')
        menufont1 = ('calibri', 16)
        box_width = 40
        self.root = tk.Tk()
        self.root.configure(background=self.bg_color)
        self.root.title("WeDi")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)

        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        prefmenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Preferences", menu=prefmenu)
        prefmenu.add_command(label="Settings", command=self.about)
        helpmenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="How to...", command=self.about)
        helpmenu.add_command(label="Disclaimer", command=self.about)
        helpmenu.add_command(label="About", command=self.about)

        self.docgray = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'docgray.png')))
        self.docgreen = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'docgreen.png')))
        self.imggray = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'imggray.png')))
        self.imggreen = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'imggreen.png')))
        self.audgray = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'audgray.png')))
        self.audgreen = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'audgreen.png')))
        self.devgray = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'devgray.png')))
        self.devgreen = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'devgreen.png')))
        self.vidgray = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'vidgray.png')))
        self.vidgreen = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'vidgreen.png')))
        self.buttonframe = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'buttonframe.png')))
        self.titleimg = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'titleimg.png')))
        self.pasteimg = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'pasteimg.png')))
        self.delimg = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'delimg.png')))
        self.buttonimg = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'button.png')))

        self.start_frame = tk.Frame(self.root, bg=self.bg_color)
        self.start_frame2 = tk.Frame(self.root, bg=self.bg_color)
        self.body_frame = tk.Frame(self.root, bg=self.bg_color)
        self.end_frame = tk.Frame(self.root, bg=self.bg_color)

        self.title = tk.Label(self.start_frame, image=self.titleimg, bg=self.bg_color, pady=35)
        self.title.pack(side='top')
        self.siteEntry = tk.Entry(self.start_frame, width=box_width+25, font=font)
        self.siteEntry.pack(side='top')
        try:
            clipboard = self.root.clipboard_get()
        except:
            clipboard = ""
        if len(clipboard) > 10 and clipboard[:4] == 'http':
            self.siteEntry.insert(0, clipboard)
        tk.Button(self.start_frame, image=self.delimg, bg=self.button_color, command=self.clear_site).pack(side='right')
        tk.Button(self.start_frame, image=self.pasteimg, bg=self.button_color, command=self.paste_site).pack(side='right')
        tk.Label(self.start_frame2, text="Choose what you want to download", font=font, padx=20, pady=20, bg=self.bg_color).pack(side='top')

        color = self.docgray
        if self.settings['documents']['run']:
            color = self.docgreen
        self.doc_button = tk.Button(self.body_frame, image=color, border=0, bg= self.bg_color, activebackground=self.bg_color, command=self.on_documents)
        self.doc_button.grid(row=0, column=0, padx=20, pady=10)
        color = self.imggray
        if self.settings['images']['run']:
            color = self.imggreen
        self.img_button = tk.Button(self.body_frame, image=color, border=0, bg= self.bg_color, activebackground=self.bg_color, command=self.on_images)
        self.img_button.grid(row=0, column=1, padx=20, pady=10)
        color = self.audgray
        if self.settings['audios']['run']:
            color = self.audgreen
        self.aud_button = tk.Button(self.body_frame, image=color, border=0, bg= self.bg_color, activebackground=self.bg_color, command=self.on_audios)
        self.aud_button.grid(row=1, column=0, padx=20, pady=10)
        color = self.devgray
        if self.settings['dev']['run']:
            color = self.devgreen
        self.dev_button = tk.Button(self.body_frame, image=color, border=0, bg= self.bg_color, activebackground=self.bg_color, command=self.on_analytics)
        self.dev_button.grid(row=1, column=1, padx=20, pady=10)
        color = self.vidgray
        if self.settings['videos']['run']:
            color = self.vidgreen
        self.vid_button = tk.Button(self.body_frame, image=color, border=0, bg= self.bg_color, activebackground=self.bg_color, command=self.on_videos)
        self.vid_button.grid(row=2, column=0, padx=20, pady=10)

        def set_format(value):
            self.settings['videos']['format'] = self.format_dict[value]
        formats = ["Best video quality", "Worst video quality", "Only video (no audio)"]
        self.option = tk.StringVar()
        self.option.set(self.inv_format_dict[self.settings['videos']['format']])
        self.options = tk.OptionMenu(self.body_frame, self.option, *formats, command=set_format)  # creates drop down menu
        self.options.config(indicatoron=0,bg=self.bg_color, border=0, highlightthickness=0, image=self.buttonframe, compound=tk.CENTER, activebackground=self.bg_color, font=menufont)
        self.options["menu"].config(bg=self.button_color, font=menufont1)
        self.options.grid(row=2, column=1)

        self.run_button = tk.Button(self.end_frame, text="Fast run", font=font, image=self.buttonimg, border=0, bg=self.bg_color, activebackground=self.bg_color,compound=tk.CENTER, command=self.on_run)
        self.run_button.pack(side='left', padx=50, pady=30)
        self.button = tk.Button(self.end_frame, text='Extensive run', font=font, image=self.buttonimg, border=0, bg=self.bg_color, activebackground=self.bg_color,compound=tk.CENTER, command=self.on_extensive_run)
        self.button.pack(side='left', padx=50, pady=30)

        self.start_frame.pack(side="top")
        self.start_frame2.pack(side="top")
        self.body_frame.pack()
        self.end_frame.pack(side="bottom")

        self.root.mainloop()

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
            self.vid_button['image'] = self.vidgreen
        else:
            self.vid_button['image'] = self.vidgray

    def on_documents(self):
        self.settings['documents']['run'] = not self.settings['documents']['run']
        if self.settings['documents']['run']:
            self.doc_button['image'] = self.docgreen
        else:
            self.doc_button['image'] = self.docgray

    def on_images(self):
        self.settings['images']['run'] = not self.settings['images']['run']
        if self.settings['images']['run']:
            self.img_button['image'] = self.imggreen
        else:
            self.img_button['image'] = self.imggray

    def on_audios(self):
        self.settings['audios']['run'] = not self.settings['audios']['run']
        if self.settings['audios']['run']:
            self.aud_button['image'] = self.audgreen
        else:
            self.aud_button['image'] = self.audgray

    def on_analytics(self):
        self.settings['dev']['run'] = not self.settings['dev']['run']
        if self.settings['dev']['run']:
            self.dev_button['image'] = self.devgreen
        else:
            self.dev_button['image'] = self.devgray

    def about(self):
        print("About", "WeDi (Web Dissector) is...")

    def default_settings(self):
        path = "."
        extensive = False
        img_types = ['jpg', 'jpeg', 'png', 'gif']
        doc_types = ['py', 'txt', 'java', 'php', 'pdf', 'md', 'gitignore', 'c']
        vid_types = ['mp4', 'avi', 'mpeg', 'mpg', 'wmv', 'mov', 'flv', 'swf', 'mkv', '3gp']
        aud_types = ['mp3', 'aac', 'wma', 'wav']
        img_settings = {'run':True, 'img_types':img_types}
        doc_settings = {'run':True, 'doc_types':doc_types}
        vid_settings = {'run':True, 'vid_types':vid_types, 'format':'best'}
        aud_settings = {'run':True, 'aud_types':aud_types}
        dev_settings = {'run':True}
        settings = {'path':path, 'extensive':extensive,'images':img_settings, 'documents':doc_settings, 'videos':vid_settings, 'audios':aud_settings, 'dev':dev_settings}
        pickle.dump(settings, open('settings.sav', 'wb'))
        return settings

    def on_extensive_run(self):
        self.settings['extensive'] = True
        self.on_run()

    def on_run(self):
        site = self.siteEntry.get()
        if len(site) > 10 and site[:4] == 'http':
            pickle.dump(self.settings, open('settings.sav', 'wb'))
            runGUI.runGUI(site, self.settings)
        else:
            print("Enter the webpage url!")

if __name__ == '__main__':
    GUI()
