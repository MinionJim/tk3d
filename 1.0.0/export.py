import traceback, threading, multiprocessing, time, os, tkinter.filedialog, math, tempfile
from tkinter import *

from tk3d.coordinate_processor import *

try:
    import PIL.Image, PIL.ImageDraw
    SAVE_IMAGE = True
except:
    try:
        sys.path.append ("PIL.egg")
        import PIL.Image, PIL.ImageDraw
        SAVE_IMAGE = True
    except: SAVE_IMAGE = False

try:
    import cv2
    SAVE_VIDEO = True
except: SAVE_VIDEO = False

class image_helper:
    mult = 1
    def __init__ (self, draw): self.draw = draw
    def line (self, coords, **kw): self.draw.line ([i * self.mult for i in coords], **kw)
    def text (self, coords, **kw): self.draw.text ([coords [i] * self.mult - self.draw.textsize (kw ["text"]) [i] / 2 for i in range (2)], **kw)
    def rectangle (self, coords, **kw): self.draw.rectangle ([i * self.mult for i in coords], **kw)

class render:

    add = [0, 0, 5]

    def __init__ (self, mode, q, l, width, height, bg, coords, axis, image_folder):
        try:
            self.coords, self.width, self.height, self.axis, self.bg = coords, width, height, axis, bg
            for i in range (int (90 / q) + 1):
                self.angle = [0, 0, 0]
                if mode // 2 == 2: self.angle [0], self.angle [2] = -math.radians (i * q * 2 + mode % 2 * 180), -math.radians (i * q * 2 + mode % 2 * 180)
                else: self.angle [mode // 2] = -math.radians (i * q * 2 + mode % 2 * 180)
                image = PIL.Image.new ("RGB", (width * image_helper.mult, height * image_helper.mult), bg)
                d = PIL.ImageDraw.Draw (image)
                self.draw = image_helper (d)
                process_co (self, True, self.width, self.height, self.bg, True)
                image.save (os.path.join (image_folder, "Frame %s.png" % self.form_num (str (int (i + 1 + mode * 90 / q)), 4)))
                perc = i / 90 * q
                l [mode] = perc
            l [mode] = 1
        except Exception as e: l [mode] = str (e)

    def form_num (self, num, length): return "0".join (["" for i in range (length - len (num) + 1)]) + num

class export (Toplevel):
    
    def __init__ (self, m):
        super ().__init__ ()
        self.grab_set ()
        self.focus_force ()
        self.resizable (False, False)
        self.m = m
        Label (self, text = "Save screen as:", font = ("times", 30)).grid (row = 0, column = 0, columnspan = 2)
        self.mode, self.quality = IntVar (value = 0), IntVar (value = 1)
        self.b1 = Radiobutton (self, text = "Still", font = ("times", 15), variable = self.mode, value = 0, command = self.mode_change)
        self.b1.grid (row = 1, column = 0)
        self.b2 = Radiobutton (self, text = "Animation", font = ("times", 15), variable = self.mode, value = 1, command = self.mode_change)
        self.b2.grid (row = 1, column = 1)
        Label (self, text = "Quality:", font = ("times", 30)).grid (row = 2, column = 0, columnspan = 2)
        self.b3 = Radiobutton (self, text = "Low", font = ("times", 15), variable = self.quality, value = 0)
        self.b3.grid (row = 3, column = 0)
        self.b4 = Radiobutton (self, text = "Medium", font = ("times", 15), variable = self.quality, value = 1)
        self.b4.grid (row = 3, column = 1)
        self.b5 = Radiobutton (self, text = "High", state = "disabled", font = ("times", 15), variable = self.quality, value = 2)
        self.b5.grid (row = 4, column = 0)
        self.b6 = Radiobutton (self, text = "Extreme", state = "disabled", font = ("times", 15), variable = self.quality, value = 3)
        self.b6.grid (row = 4, column = 1)
        self.b7 = Button (self, text = "Save", font = ("times", 15), command = lambda: threading.Thread (target = self.save).start ())
        self.b7.grid (row = 5, column = 0, columnspan = 2)
        self.user_info = Label (self, text = "", font = ("times", 15))
        self.user_info.grid (row = 6, column = 0, columnspan = 2)

    def mode_change (self):
        if self.mode.get ():
            for i in [self.b5, self.b6]: i.config (state = "normal")
        else:
            for i in [self.b5, self.b6]: i.config (state = "disabled")
            if self.quality.get () >= 2: self.quality.set (1)

    def save (self):
        if self.mode.get (): self.save_animation ()
        else: self.save_image ()

    def save_image (self):
        for i in [self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7]: i.config (state = "disabled")
        self.user_info.config (text = "Choosing file...")
        try:
            f = tkinter.filedialog.asksaveasfile (initialfile = "Figure", defaultextension = "*.png", filetypes = (("PNG image", "*.png"), ("JPEG image", "*.jpg"), ("GIF image", "*.gif"), ("PDF file", "*.pdf")))
            if f:
                self.user_info.config (text = "Saving file...")
                f.close ()
                self.__image_helper.mult = [1, 2] [self.quality.get ()]
                image = PIL.Image.new ("RGB", (self.m.c.winfo_width () * image_helper.mult, self.m.c.winfo_height () * self.__image_helper.mult), self.m.c.cget ("bg"))
                d = PIL.ImageDraw.Draw (image)
                self.draw, self.coords, self.angle, self.add, self.axis = image_helper (d), self.m.coords, self.m.angle, self.m.add, self.m.axis
                process_co (self, True, self.m.c.winfo_width (), self.m.c.winfo_height (), self.m.c.cget ("bg"), True)
                image.save (f.name)
                self.user_info.config (text = "Save successful.")
            else: self.user_info.config (text = "Save cancelled.")
        except:
            self.user_info.config (text = "An error occurred.")
            traceback.print_exception (*sys.exc_info ())
        for i in [self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7]: i.config (state = "normal")

    def save_animation (self):
        for i in [self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7]: i.config (state = "disabled")
        self.user_info.config (text = "Choosing file...")
        try:
            if SAVE_VIDEO: f = tkinter.filedialog.asksaveasfile (initialfile = "Figure", defaultextension = "*.mp4", filetypes = (("MP4 video", "*.mp4"), ("AVI video", "*.avi"), ("GIF image", "*.gif")))
            else: f = tkinter.filedialog.asksaveasfile (initialfile = "Figure", defaultextension = "*.gif", filetypes = (("GIF image", "*.gif"),))
            if f:
                self.user_info.config (text = "Preparing to render...")
                f.close ()

                with tempfile.TemporaryDirectory() as image_folder:

                    video_name = f.name

                    q = [4, 2, 1, 0.5] [self.quality.get ()]

                    # This is 3x quicker when using multiple processes than using a single process.

                    n = 6
                    l = multiprocessing.Manager ().list ([0 for i in range (n)])
                    p = [multiprocessing.Process (target = render, args = (i, q, l, self.m.c.winfo_width (), self.m.c.winfo_height (), self.m.c.cget ("bg"), self.m.coords, self.m.axis, image_folder)) for i in range (n)]
                    for i in p: i.start ()
                    while True:
                        time.sleep (0.1)
                        perc = sum (l) / n * 100
                        if self.quality.get () in [0, 1]: perc = int (perc)
                        else: perc = round (perc, 1)
                        self.user_info.config (text = "Rendering %s%s..." % (perc, "%"))
                        if l.count (1) == n: break

                    images = [img for img in os.listdir (image_folder) if img.endswith (".png")]

                    if f.name.split (".") [-1] == "gif":
                        self.user_info.config (text = "Collating and saving...")
                    
                        ims = [PIL.Image.open (os.path.join (image_folder, i)) for i in images]
                        
                        image = ims [0]
                        image.save (f.name, save_all = True, append_images = ims [1 : ], duration = q / 0.03)
                    else:
                        self.user_info.config (text = "Saving file...")
                        
                        frame = cv2.imread (os.path.join (image_folder, images [0]))
                        height, width, layers = frame.shape

                        video = cv2.VideoWriter (video_name, -1, 30 / q, (width, height))

                        for image in images: video.write (cv2.imread (os.path.join (image_folder, image)))

                        video.release ()

                    self.user_info.config (text = "Finishing up...")

                #self.user_info.config (text = "Cleaning files...")
                #shutil.rmtree (image_folder)
                
                self.user_info.config (text = "Save successful.")
            else: self.user_info.config (text = "Save cancelled.")
        except:
            self.user_info.config (text = "An error occurred.")
            traceback.print_exception (*sys.exc_info ())
        for i in [self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7]: i.config (state = "normal")

    def form_num (self, num, length): return "0".join (["" for i in range (length - len (num) + 1)]) + num
