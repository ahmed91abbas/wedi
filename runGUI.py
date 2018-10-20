import tkinter as tk
import threading
import os
import sys

class runGUI:
    def __init__(self):
        self.stopevent = False
        self.top = tk.Toplevel()
        self.top.title("Run status")
        self.top.wm_protocol("WM_DELETE_WINDOW", self.on_close)

        # docgray = tk.PhotoImage(file=os.path.join('textures', 'docgray.png'))
        # docgreen = tk.PhotoImage(file=os.path.join('textures', 'docgreen.png'))
        # imggray = tk.PhotoImage(file=os.path.join('textures', 'imggray.png'))
        # imggreen = tk.PhotoImage(file=os.path.join('textures', 'imggreen.png'))
        # audgray = tk.PhotoImage(file=os.path.join('textures', 'audgray.png'))
        # audgreen = tk.PhotoImage(file=os.path.join('textures', 'audgreen.png'))
        # devgray = tk.PhotoImage(file=os.path.join('textures', 'devgray.png'))
        # devgreen = tk.PhotoImage(file=os.path.join('textures', 'devgreen.png'))
        # vidgray = tk.PhotoImage(file=os.path.join('textures', 'vidgray.png'))
        # vidgreen = tk.PhotoImage(file=os.path.join('textures', 'vidgreen.png'))

        # self.imgIndex = 0
        # self.images = [docgray, docgreen, imggray, imggreen, audgray, audgreen, devgray, devgreen, vidgray, vidgreen]

        # self.canvas = tk.Label(self.top)
        # self.canvas.pack()

    def set_stopevent(self, value):
        self.stopevent = value

    # def nextImg(self):
    #     self.imgIndex = self.imgIndex + 1
    #     if self.imgIndex == len(self.images):
    #         self.imgIndex = 0
    #     return self.images[self.imgIndex]

    # def cycleImages(self):
    #     img = self.nextImg()
    #     self.canvas.config(image=img)
    #     if not self.stopevent:
    #         self.top.after(1000, self.cycleImages)

    def on_close(self):
        self.top.destroy()

    def mainloop(self):
        tk.mainloop()

if __name__ == '__main__':
    r = runGUI()
    #r.cycleImages()
    r.mainloop()
