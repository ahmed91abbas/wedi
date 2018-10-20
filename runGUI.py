import tkinter as tk
from tkinter import IntVar
import threading
import os
import sys
from PIL import Image, ImageTk

class runGUI:
    def __init__(self, site, settings):
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
        tk.Label(self.dFrame1, borderwidth= 2, relief='solid', text='Now downloading...', bg=self.bg_color, width=w1).pack(side='left')
        openfolder = IntVar()
        tk.Checkbutton(self.dFrame1, borderwidth= 2, relief='solid', text="Open download folder when done", variable=openfolder, width=w2).pack(side='right')

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
        self.barLabel = tk.Label(self.dFrame4, borderwidth= 2, relief='solid', text='baaaaaaaaaar', bg=self.bg_color, width=w12)
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
        docgray = tk.PhotoImage(file=os.path.join('textures', 'button.png'))
        docgreen = tk.PhotoImage(file=os.path.join('textures', 'docgreen.png'))
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

    def set_stopevent(self, value):
        self.stopevent = value

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

    def on_close(self):
        self.top.destroy()

    def mainloop(self):
        tk.mainloop()

if __name__ == '__main__':
    r = runGUI(None, None)
    r.cycleImages()
    r.mainloop()
