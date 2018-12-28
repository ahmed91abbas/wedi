try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import sys
import pickle
import os
import runGUI
import webbrowser
from PIL import Image, ImageTk
from ToolTip import ToolTip
from settingsGUI import settings_GUI

class GUI:
    def __init__(self, settings_filepath):
        self.settings_filepath = settings_filepath
        try:
            self.settings = pickle.load(open(settings_filepath, 'rb'))
        except:
            self.settings = self.default_settings()
        self.format_dict = {"Best video quality":'best', "Worst video quality":'worst', "Only video (no audio)":'bestvideo'}
        self.inv_format_dict = {v: k for k, v in self.format_dict.items()}
        self.info_on = False
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
        prefmenu.add_command(label="Settings", command=self.on_settings_menu)
        helpmenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="Open download folder", command=self.on_open_download_folder)
        helpmenu.add_command(label="Open Github page", command=self.on_open_github)
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
        self.infoOnImg = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'info_on.png')))
        self.infoOffImg = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'info_off.png')))
        self.imgicon = ImageTk.PhotoImage(Image.open(os.path.join('textures', 'icon.ico')))

        #set the window icon
        self.root.tk.call('wm', 'iconphoto', self.root._w, self.imgicon)

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
        self.del_button = tk.Button(self.start_frame, image=self.delimg, bg=self.button_color, command=self.clear_site)
        self.del_button.pack(side='right')
        self.paste_button = tk.Button(self.start_frame, image=self.pasteimg, bg=self.button_color, command=self.paste_site)
        self.paste_button.pack(side='right')
        self.info_button = tk.Button(self.start_frame, image=self.infoOffImg, border=0, highlightthickness=0, bg=self.bg_color, activebackground=self.bg_color, command=self.on_info)
        self.info_button.pack(side='left')
        text = "Activate to show hover over help text"
        self.info_toolTip = self.createToolTip(self.info_button, text)

        tk.Label(self.start_frame2, text="Choose what you want to download", font=font, padx=20, pady=20, bg=self.bg_color).pack(side='top')

        color = self.docgray
        if self.settings['documents']['run']:
            color = self.docgreen
        self.doc_button = tk.Button(self.body_frame, image=color, border=0, highlightthickness=0, bg= self.bg_color, activebackground=self.bg_color, command=self.on_documents)
        self.doc_button.grid(row=0, column=0, padx=20, pady=10)
        color = self.imggray
        if self.settings['images']['run']:
            color = self.imggreen
        self.img_button = tk.Button(self.body_frame, image=color, border=0, highlightthickness=0, bg= self.bg_color, activebackground=self.bg_color, command=self.on_images)
        self.img_button.grid(row=0, column=1, padx=20, pady=10)
        color = self.audgray
        if self.settings['audios']['run']:
            color = self.audgreen
        self.aud_button = tk.Button(self.body_frame, image=color, border=0, highlightthickness=0, bg= self.bg_color, activebackground=self.bg_color, command=self.on_audios)
        self.aud_button.grid(row=1, column=0, padx=20, pady=10)
        color = self.devgray
        if self.settings['dev']['run']:
            color = self.devgreen
        self.dev_button = tk.Button(self.body_frame, image=color, border=0, highlightthickness=0, bg= self.bg_color, activebackground=self.bg_color, command=self.on_analytics)
        self.dev_button.grid(row=1, column=1, padx=20, pady=10)
        color = self.vidgray
        if self.settings['videos']['run']:
            color = self.vidgreen
        self.vid_button = tk.Button(self.body_frame, image=color, border=0, highlightthickness=0, bg= self.bg_color, activebackground=self.bg_color, command=self.on_videos)
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

        self.run_button = tk.Button(self.end_frame, text="Run", font=font, image=self.buttonimg, border=0, highlightthickness=0, bg=self.bg_color, activebackground=self.bg_color,compound=tk.CENTER, command=self.on_run)
        self.run_button.pack(side='left', padx=50)
        self.run_button2 = tk.Button(self.end_frame, text='Extensive run', font=font, image=self.buttonimg, border=0, highlightthickness=0, bg=self.bg_color, activebackground=self.bg_color,compound=tk.CENTER, command=self.on_extensive_run)
        self.run_button2.pack(side='left', padx=50)

        self.start_frame.pack(side="top")
        self.start_frame2.pack(side="top")
        self.body_frame.pack()
        self.end_frame.pack(side="bottom", pady=25)

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
        self.root.destroy()
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
        img_types = ['jpg', 'jpeg', 'png', 'gif', 'svg']
        doc_types = ['txt', 'py', 'java', 'php', 'pdf', 'md', 'gitignore', 'c']
        vid_types = ['mp4', 'avi', 'mpeg', 'mpg', 'wmv', 'mov', 'flv', 'swf', 'mkv', '3gp', 'webm', 'ogg']
        aud_types = ['mp3', 'aac', 'wma', 'wav', 'm4a']
        img_settings = {'run':True, 'img_types':img_types}
        doc_settings = {'run':True, 'doc_types':doc_types}
        vid_settings = {'run':True, 'vid_types':vid_types, 'format':'best'}
        aud_settings = {'run':True, 'aud_types':aud_types}
        dev_settings = {'run':True}
        settings = {'path':path, 'extensive':extensive,'images':img_settings, 'documents':doc_settings, 'videos':vid_settings, 'audios':aud_settings, 'dev':dev_settings}
        pickle.dump(settings, open('settings.sav', 'wb'))
        return settings


    def on_info(self):
        if self.info_on:
            self.info_button["image"] = self.infoOffImg
            self.info_on = False
            self.destroyToolTips()
        else:
            self.info_button["image"] = self.infoOnImg
            self.info_on = True
            self.createToolTips()

    def createToolTip(self, widget, text):
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
        return toolTip

    def createToolTips(self):
        self.toolTips = []
        self.info_toolTip.hidetip()
        text = "Deactivate to hide hover over help text"
        self.info_toolTip = self.createToolTip(self.info_button, text)
        self.toolTips.append(self.info_button)
        text = "The url of the page you want to download from goes in here..."
        self.createToolTip(self.siteEntry, text)
        self.toolTips.append(self.siteEntry)
        text = "Paste in url from clipboard"
        self.createToolTip(self.paste_button, text)
        self.toolTips.append(self.paste_button)
        text = "Empty url entry field"
        self.createToolTip(self.del_button, text)
        self.toolTips.append(self.del_button)
        text = "Creates files containing information about the supplied\nurl, the results of the run and some analytics data"
        self.createToolTip(self.dev_button, text)
        self.toolTips.append(self.dev_button)
        text = "This option will also try to extract the audio from the videos found in the url\nPlease note that you need to have FFmpeg installed in your machine if you want\nthe downloaded audio file to be converted to mp3"
        self.createToolTip(self.aud_button, text)
        self.toolTips.append(self.aud_button)
        text = "This option will also try to extract empeded video files found in the url\nPlease note that not all websites are supported"
        self.createToolTip(self.vid_button, text)
        self.toolTips.append(self.vid_button)
        text = "This mode uses either Firefox or Chrome browsers\nin your machine to fetch the source code of the url"
        self.createToolTip(self.run_button2, text)
        self.toolTips.append(self.run_button2)

    def destroyToolTips(self):
        for w in self.toolTips:
            w.unbind('<Enter>')
            w.unbind('<Leave>')
        self.info_toolTip.hidetip()
        text = "Activate to show hover over help text"
        self.info_toolTip = self.createToolTip(self.info_button, text)

    def on_extensive_run(self):
        self.on_run(extensive=True)

    def on_settings_menu(self):
        settings_GUI(self.settings_filepath, imgicon=self.imgicon)

    def on_open_download_folder(self):
        downloadpath = pickle.load(open(self.settings_filepath, 'rb'))["path"]
        _platform = sys.platform
        if _platform == "linux" or _platform == "linux2": # linux
            subprocess.Popen(["xdg-open", downloadpath])
        elif _platform == "darwin": # MAC OS X
            subprocess.Popen(["open", downloadpath])
        elif _platform == "win32" or _platform == "win64": # Windows
            os.startfile(downloadpath)

    def on_open_github(self):
        url = "https://github.com/ahmed91abbas/WeDi"
        webbrowser.open(url, new=0, autoraise=True)

    def on_run(self, extensive=False):
        current_settings = pickle.load(open(self.settings_filepath, 'rb'))
        self.settings['extensive'] = extensive
        site = self.siteEntry.get()
        if len(site) > 10 and site[:4] == 'http':
            self.settings["path"] = current_settings["path"]
            self.settings["documents"]["doc_types"] = current_settings["documents"]["doc_types"]
            self.settings["images"]["img_types"] = current_settings["images"]["img_types"]
            self.settings["audios"]["aud_types"] = current_settings["audios"]["aud_types"]
            self.settings["videos"]["vid_types"] = current_settings["videos"]["vid_types"]
            pickle.dump(self.settings, open('settings.sav', 'wb'))
            runGUI.runGUI(site, self.settings, imgicon=self.imgicon)
        else:
            print("Enter the webpage url!")

if __name__ == '__main__':
    settings_filepath = 'settings.sav'
    GUI(settings_filepath)
