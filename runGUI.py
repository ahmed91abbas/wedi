try:
    import tkinter as tk
    from tkinter.ttk import Progressbar
except ImportError:
    import Tkinter as tk
    from Tkinter.ttk import Progressbar
import mttkinter as mttkinter
import threading
import subprocess, os, sys
from PIL import Image, ImageTk
from wedi import services
import math

class runGUI:
    def __init__(self, site, settings):
        self.downloaded = {}
        self.error = False
        self.createGUI()
        self.cycleImages()
        self.services = services(site, settings, self)
        threading.Thread(target=self.run_services).start()
        self.mainloop()

    def run_services(self):
        self.services.run()

    def createGUI(self):
        self.stopevent = False
        self.bg_color = '#e6e6ff'
        font = ('calibri', 13)
        self.top = tk.Toplevel(bg=self.bg_color)
        self.top.title("Run status")
        self.top.wm_protocol("WM_DELETE_WINDOW", self.on_close)
        self.top.resizable(False, False)

        self.downloadingFrame = tk.Frame(self.top, bg=self.bg_color)
        self.listFrame = tk.Frame(self.top, bg=self.bg_color)

        self.downloadingFrame.pack()
        self.listFrame.pack()

        pady = 10
        padx = 10
        self.dFrame1 = tk.Frame(self.downloadingFrame, bg=self.bg_color)
        self.dFrame2 = tk.Frame(self.downloadingFrame, bg=self.bg_color)
        self.dFrame3 = tk.Frame(self.downloadingFrame, bg=self.bg_color)

        self.dFrame1.pack(pady=pady, padx=padx)
        self.dFrame2.pack(pady=pady, padx=padx)
        self.dFrame3.pack(pady=pady, padx=padx)

        self.dFrame3_1 = tk.Frame(self.dFrame3, bg=self.bg_color)
        self.dFrame3_2 = tk.Frame(self.dFrame3, bg=self.bg_color)
        self.dFrame3_3 = tk.Frame(self.dFrame3, bg=self.bg_color)
        self.dFrame3_4 = tk.Frame(self.dFrame3, bg=self.bg_color)
        self.dFrame3_5 = tk.Frame(self.dFrame3, bg=self.bg_color)

        self.dFrame3_1.pack(side='left')
        self.dFrame3_2.pack(side='left')
        self.dFrame3_3.pack(side='left')
        self.dFrame3_4.pack(side='left')
        self.dFrame3_5.pack(side='left')

        self.dFrame3_1_1 = tk.Frame(self.dFrame3_1, bg=self.bg_color)
        self.dFrame3_1_2 = tk.Frame(self.dFrame3_1, bg=self.bg_color)

        self.dFrame3_1_1.pack()
        self.dFrame3_1_2.pack()

        self.lFrame1 = tk.Frame(self.listFrame, bg=self.bg_color)
        self.lFrame2 = tk.Frame(self.listFrame, bg=self.bg_color)
        self.lFrame3 = tk.Frame(self.listFrame, bg=self.bg_color)

        self.lFrame1.pack(side='left', pady=pady)
        self.lFrame2.pack(side='left', pady=pady)
        self.lFrame3.pack(side='left',pady=pady)


        width = 110
        #downloadingFrame children
        file = os.path.join('textures', 'a.png')
        img = ImageTk.PhotoImage(Image.open(file))
        l = tk.Label(self.dFrame1, image=img, bg=self.bg_color)
        l.photo=img
        l.pack(side='left')
        self.actionLabel = tk.Label(self.dFrame1, text='Now downloading...', bg=self.bg_color, font=('calibri', 13))
        self.actionLabel.pack(side='left')
        file = os.path.join('textures', 'b.png')
        img = ImageTk.PhotoImage(Image.open(file))
        l = tk.Label(self.dFrame1, image=img, bg=self.bg_color)
        l.photo=img
        l.pack(side='left')

        self.urlLabel = tk.Label(self.dFrame2, borderwidth= 3, relief='groove', bg=self.bg_color, width=width, anchor='w')
        self.urlLabel.pack()

        w1 = int(width/3)
        w11 = int(w1/2)
        w12 = w1 - w11
        w2 = int((width-w1)/4)
        w3 = w4 = w2
        w5 = width - w1 - w2 - w3 -w4
        tk.Label(self.dFrame3_1_1, borderwidth= 0, relief='solid', text='Progress:', bg=self.bg_color, width=w11, anchor='w').pack(side='left')
        self.percLabel = tk.Label(self.dFrame3_1_1, borderwidth= 0, relief='solid', text='00.0%', bg=self.bg_color, width=w12, anchor='e')
        self.percLabel.pack(side='right')
        tk.Label(self.dFrame3_2, borderwidth= 0, relief='solid', text='Time left', bg=self.bg_color, width=w2).pack()
        tk.Label(self.dFrame3_3, borderwidth= 0, relief='solid', text='Speed', bg=self.bg_color, width=w3).pack()
        tk.Label(self.dFrame3_4, borderwidth= 0, relief='solid', text='Downloaded', bg=self.bg_color, width=w4).pack()
        tk.Label(self.dFrame3_5, borderwidth= 0, relief='solid', text='Total size', bg=self.bg_color, width=w5).pack()

        w1 = math.floor(w1*7.17) #convert width to progress length
        self.progress = tk.IntVar()
        Progressbar(self.dFrame3_1_2, orient=tk.HORIZONTAL, length=w1, mode='determinate', variable=self.progress).pack(side='left')
        self.timeLeftLabel = tk.Label(self.dFrame3_2, borderwidth= 0, relief='solid', text='0 Seconds', bg=self.bg_color, width=w2)
        self.timeLeftLabel.pack()
        self.speedLabel = tk.Label(self.dFrame3_3, borderwidth= 0, relief='solid', text='0.0 KB/s', bg=self.bg_color, width=w3)
        self.speedLabel.pack()
        self.downloadedLabel = tk.Label(self.dFrame3_4, borderwidth= 0, relief='solid', text='0.0 KB', bg=self.bg_color, width=w4)
        self.downloadedLabel.pack()
        self.sizeLabel = tk.Label(self.dFrame3_5, borderwidth= 0, relief='solid', text='0.0 KB', bg=self.bg_color, width=w5)
        self.sizeLabel.pack()

        #listFrame children
        wlist = int(width/2.5)
        wimg = width - 2*wlist
        hlist = int(width/5)
        tk.Label(self.lFrame1, text='List of urls to download:', font=font, bg=self.bg_color).pack()
        scrollbar = tk.Scrollbar(self.lFrame1)
        scrollbar.pack(side='right', fill=tk.Y)
        self.urlslistbox = tk.Listbox(self.lFrame1, width=wlist, height=hlist)
        self.urlslistbox.pack()
        self.urlslistbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.urlslistbox.yview)
        self.openfolderLabel = tk.Label(self.lFrame2, text='Open download folder', font=font, bg=self.bg_color)#pack on complete
        self.openfolderButton = tk.Button(self.lFrame2, bg=self.bg_color,
            activebackground=self.bg_color, command=self.openDownloadPath)#pack on complete
        self.animationLabel = tk.Label(self.lFrame2, bg=self.bg_color)
        self.animationLabel.pack()
        tk.Label(self.lFrame3, text='List of downloaded files:', font=font, bg=self.bg_color).pack()
        scrollbar = tk.Scrollbar(self.lFrame3)
        scrollbar.pack(side='right', fill=tk.Y)
        self.listbox = tk.Listbox(self.lFrame3, width=wlist, height=hlist)
        self.listbox.pack()
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.bind('<Double-Button-1>', self.mouse_click)
        self.listbox.bind('<Return>', self.mouse_click)
        scrollbar.config(command=self.listbox.yview)

        self.load_animation(wimg, hlist)

    def load_animation(self, width, height):
        self.images = []
        self.imgIndex = 0
        width = int(width*7.17) +50
        height = width*2
        path = os.path.join('textures', 'animation')
        files = [os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        files = sorted(files)
        for file in files:
            image = Image.open(file)
            image = image.resize((width, height), Image.ANTIALIAS)
            self.images.append(ImageTk.PhotoImage(image))
        self.animationLabel.config(image=self.images[0])
        #load the image for completed
        file = os.path.join('textures', 'completed.png')
        self.completedImg = ImageTk.PhotoImage(Image.open(file))
        #load the image for error
        file = os.path.join('textures', 'error.png')
        self.errorImg = ImageTk.PhotoImage(Image.open(file))

    def set_stopevent(self, files=0, size=0, time=0):
        self.stopevent = True
        #Change the download frames with info frames
        #convert size into string
        if size > 10**6:
            size_str = str(round(size/10**6, 2)) + ' MB'
        else:
            size_str = str(round(size/10**3, 2)) + ' KB'
        #convert time into string
        if time > 3600:
            time_str = str(round(time / 3600, 2)) + ' Hours'
        elif time > 60:
            time_str = str(round(time / 60, 2)) + ' Minutes'
        else:
            time_str = str(round(time,1)) + ' Seconds'
        for frame in self.dFrame3.winfo_children():
            for label in frame.winfo_children():
                label.destroy()
        tk.Label(self.dFrame3_1, text='Run time', bg=self.bg_color).pack()
        tk.Label(self.dFrame3_1, text=time_str, bg=self.bg_color).pack()
        tk.Label(self.dFrame3_3, text='Total download size', bg=self.bg_color).pack()
        tk.Label(self.dFrame3_3, text=size_str, bg=self.bg_color).pack()
        tk.Label(self.dFrame3_5, text='File count', bg=self.bg_color).pack()
        tk.Label(self.dFrame3_5, text=str(files), bg=self.bg_color).pack()
        self.urlLabel['anchor'] = 'center'

    def nextImg(self):
        self.imgIndex = self.imgIndex + 1
        if self.imgIndex == len(self.images):
            self.imgIndex = 0
        return self.images[self.imgIndex]

    def cycleImages(self):
        img = self.nextImg()
        self.animationLabel.config(image=img)
        if not self.stopevent:
            self.top.after(170, self.cycleImages)
        elif self.error:
            self.animationLabel.config(image=self.errorImg)
        else:
            #self.downloadingFrame.pack_forget()
            self.animationLabel.pack_forget()
            self.openfolderButton.pack()
            self.openfolderLabel.pack()
            self.openfolderButton.config(image=self.completedImg)

    def update_values(self, url='',dl='0.0', perc='', size='0.0', eta='', speed='', action='Now downloading...'):
        dl = float(dl)
        size = float(size)
        if size != 0:
            self.progress.set(int(dl*100/size))
        if size > 10**6:
            size_str = str(round(size/10**6, 2)) + ' MB'
        else:
            size_str = str(round(size/10**3, 2)) + ' KB'
        if dl > 10**6:
            dl_str = str(round(dl/10**6, 2)) + ' MB'
        else:
            dl_str = str(round(dl/10**3, 2)) + ' KB'
        self.urlLabel['text'] = url
        self.percLabel['text'] = perc
        self.sizeLabel['text'] = size_str
        self.downloadedLabel['text'] = dl_str
        self.timeLeftLabel['text'] = eta
        self.speedLabel['text'] = speed
        self.actionLabel['text'] = action

    def update_action(self, text):
        self.actionLabel['text'] = text

    def add_to_list(self, path, replace=False):
        name = os.path.basename(path)
        self.downloaded[name] = path
        if replace:
            self.listbox.delete(tk.END)
        self.listbox.insert(tk.END, name)

    def add_to_urls(self, urls):
        for url in urls:
            self.urlslistbox.insert(tk.END, url)

    def remove_from_urls(self, url):
        self.urlslistbox.delete(0)

    def mouse_click(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        name = w.get(index)
        try:
            path = self.downloaded[name]
            if sys.platform.startswith('darwin'):
                 subprocess.call(('open', path))
            elif os.name == 'nt': # For Windows
                os.startfile(path)
            elif os.name == 'posix': # For Linux, Mac, etc.
                subprocess.call(('xdg-open', path))
        except:
            pass

    def openDownloadPath(self):
        self.services.open_path()

    def show_error(self, msg):
        self.error = True
        self.set_stopevent()
        self.actionLabel['text'] = msg

    def on_close(self):
        self.top.destroy()

    def mainloop(self):
        tk.mainloop()

if __name__ == '__main__':
    site = 'https://www.stackoverflow.com/'
    site = 'http://cs.lth.se/edan20/'
    site = 'https://www.youtube.com/watch?v=zmr2I8caF0c' #small
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
    runGUI(site, settings)
