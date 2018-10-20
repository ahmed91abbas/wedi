import tkinter as tk
from tkinter import IntVar
import threading
import os
import sys
from PIL import Image, ImageTk
from WeDi import services

class runGUI:
    def __init__(self, site, settings):
        self.createGUI()
        self.cycleImages()
        t = threading.Thread(target=self.run_services, args=(site, settings, ))
        t.daemon = True
        t.start()
        self.mainloop()

    def run_services(self, site, settings):
        services(site, settings, self)

    def createGUI(self):
        self.stopevent = False
        self.top = tk.Toplevel()
        self.top.title("Run status")
        self.top.wm_protocol("WM_DELETE_WINDOW", self.on_close)

        self.bg_color = '#e6e6ff'

        self.downloadingFrame = tk.Frame(self.top, bg=self.bg_color)
        self.listFrame = tk.Frame(self.top, bg=self.bg_color)

        self.dFrame1 = tk.Frame(self.downloadingFrame, bg=self.bg_color)
        self.dFrame2 = tk.Frame(self.downloadingFrame, bg=self.bg_color)
        self.dFrame3 = tk.Frame(self.downloadingFrame, bg=self.bg_color)
        self.dFrame4 = tk.Frame(self.downloadingFrame, bg=self.bg_color)

        self.dFrame1.pack()
        self.dFrame2.pack()
        self.dFrame3.pack()
        self.dFrame4.pack()

        self.lFrame1 = tk.Frame(self.listFrame, bg=self.bg_color)
        self.lFrame2 = tk.Frame(self.listFrame, bg=self.bg_color)
        self.lFrame3 = tk.Frame(self.listFrame, bg=self.bg_color)

        self.lFrame1.pack(side='left')
        self.lFrame2.pack(side='left')
        self.lFrame3.pack(side='left')


        width = 110
        #downloadingFrame children
        w2 = int(width / 3)
        w1 = width - w2
        self.actionLabel = tk.Label(self.dFrame1, text='Now downloading...', bg=self.bg_color, width=w1)
        self.actionLabel.pack(side='left')
        openfolder = IntVar()
        tk.Checkbutton(self.dFrame1, text="Open download folder when done", variable=openfolder, width=w2).pack(side='right')

        self.urlLabel = tk.Label(self.dFrame2, borderwidth= 2, relief='solid', text='URL goes here', bg=self.bg_color, width=width)
        self.urlLabel.pack(side='left')

        w1 = int(width/2)
        w2 = int(w1/3)
        w3 = w2
        w4 = width - w1 - w2 - w3
        tk.Label(self.dFrame3, borderwidth= 2, relief='solid', text='Progress', bg=self.bg_color, width=w1+1).pack(side='left')
        tk.Label(self.dFrame3, borderwidth= 2, relief='solid', text='ETA', bg=self.bg_color, width=w2).pack(side='left')
        tk.Label(self.dFrame3, borderwidth= 2, relief='solid', text='Speed', bg=self.bg_color, width=w3).pack(side='left')
        tk.Label(self.dFrame3, borderwidth= 2, relief='solid', text='Total size', bg=self.bg_color, width=w4).pack(side='left')

        w11 = int(w1/3)
        w12 = w1 - w11
        self.percLabel = tk.Label(self.dFrame4, borderwidth= 2, relief='solid', text='00.00%', bg=self.bg_color, width=w11)
        self.percLabel.pack(side='left')
        self.barLabel = tk.Label(self.dFrame4, borderwidth= 2, relief='solid', text='=============', bg=self.bg_color, width=w12)
        self.barLabel.pack(side='left')
        self.etaLabel = tk.Label(self.dFrame4, borderwidth= 2, relief='solid', text='ETA', bg=self.bg_color, width=w2)
        self.etaLabel.pack(side='left')
        self.speedLabel = tk.Label(self.dFrame4, borderwidth= 2, relief='solid', text='Speed', bg=self.bg_color, width=w3)
        self.speedLabel.pack(side='left')
        self.sizeLabel = tk.Label(self.dFrame4, borderwidth= 2, relief='solid', text='Total size', bg=self.bg_color, width=w4)
        self.sizeLabel.pack(side='left')

        #listFrame children
        wimg = int(width/3.5)
        wlist = width - 2*wimg
        hlist = int(width/4)
        self.leftAnimationLabel = tk.Label(self.lFrame1, bg=self.bg_color)
        self.leftAnimationLabel.pack(side='left')
        self.listLabel = tk.Label(self.lFrame2, text='list goes here', width=wlist, height=hlist)
        self.listLabel.pack(side='left')
        self.rightAnimationLabel = tk.Label(self.lFrame3, bg=self.bg_color)
        self.rightAnimationLabel.pack(side='left')

        def openimg(path):
            width = int(wimg*7)
            height = int(hlist*7)
            image = Image.open(path)
            image = image.resize((width, height), Image.ANTIALIAS)
            return ImageTk.PhotoImage(image)

        docgray = openimg(os.path.join('textures', 'docgray.png'))
        docgreen = openimg(os.path.join('textures', 'docgreen.png'))
        imggray = openimg(os.path.join('textures', 'imggray.png'))
        imggreen = openimg(os.path.join('textures', 'imggreen.png'))
        audgray = openimg(os.path.join('textures', 'audgray.png'))
        audgreen = openimg(os.path.join('textures', 'audgreen.png'))
        devgray = openimg(os.path.join('textures', 'devgray.png'))
        devgreen = openimg(os.path.join('textures', 'devgreen.png'))
        vidgray = openimg(os.path.join('textures', 'vidgray.png'))
        vidgreen = openimg(os.path.join('textures', 'vidgreen.png'))
        self.imgIndex = 0
        self.images = [docgray, docgreen, imggray, imggreen, audgray, audgreen, devgray, devgreen, vidgray, vidgreen]

        self.downloadingFrame.pack(side='top')
        self.listFrame.pack(side='bottom')

    def set_stopevent(self):
        self.stopevent = True

    def nextImg(self):
        self.imgIndex = self.imgIndex + 1
        if self.imgIndex == len(self.images):
            self.imgIndex = 0
        return self.images[self.imgIndex]

    def cycleImages(self):
        img = self.nextImg()
        self.leftAnimationLabel.config(image=img)
        self.rightAnimationLabel.config(image=img)
        if not self.stopevent:
            self.top.after(1000, self.cycleImages)

    def update_values(self, url='',dl='', perc='', size='', eta='', speed='', action='Now downloading...'):
        self.urlLabel['text'] = url
        self.percLabel['text'] = perc
        self.sizeLabel['text'] = size
        self.etaLabel['text'] = eta
        self.speedLabel['text'] = speed
        self.actionLabel['text'] = action

    def on_close(self):
        self.top.destroy()

    def mainloop(self):
        tk.mainloop()

if __name__ == '__main__':
    site = 'https://www.youtube.com/watch?v=zmr2I8caF0c' #small
    site = 'https://www.stackoverflow.com/'
    site = 'http://cs.lth.se/edan20/'
    path = "."
    img_types = ['jpg', 'jpeg', 'png', 'gif']
    doc_types = ['py', 'txt', 'java', 'php', 'pdf', 'md', 'gitignore', 'c']
    vid_types = ['mp4', 'avi', 'mpeg', 'mpg', 'wmv', 'mov', 'flv', 'swf', 'mkv', '3gp', 'webm', 'ogg']
    aud_types = ['mp3', 'aac', 'wma', 'wav', 'm4a']
    img_settings = {'run':False, 'img_types':img_types}
    doc_settings = {'run':True, 'doc_types':doc_types}
    vid_settings = {'run':False, 'vid_types':vid_types, 'format':'best'}
    aud_settings = {'run':False, 'aud_types':aud_types}
    dev_settings = {'run':False}
    settings = {'path':path, 'openfolder':False, 'images':img_settings, 'documents':doc_settings, 'videos':vid_settings, 'audios':aud_settings, 'dev':dev_settings}
    runGUI(site, settings)
