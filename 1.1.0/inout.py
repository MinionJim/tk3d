import tk3d
from tk3d.coordinate_processor import *

try:
    # Python 3
    import tkinter.filedialog as filedialog
except:
    # Python 2
    import tkFileDialog as filedialog

class save_handeller:

    def __init__ (self, master): self.m, self.file = master, None

    def save (self):
        formed = []
        for create, coords, k in self.m.coords:
            if create in [0, 1, 2]: formed.append ("\n".join ([str (create), "\t".join ([str (i) for i in coords])]))
            elif create == 3: formed.append ("\n".join ([str (create), "\t".join ([str (i) for i in coords]), k [0]]))
            elif create == 4: formed.append ("\n".join ([str (create), "\t\t".join (["\t".join ([str (j) for j in i]) for i in coords])]))
            elif create == 5: formed.append ("\n".join ([str (create), "\t\t".join (["\t".join ([str (i.mode)] + [" ".join ([str (k) for k in j]) if isinstance (j, list) else str (j) for j in i]) for i in coords]), str (k)]))
            elif create == 6: formed.append ("\n".join ([str (create), str (coords)]))
        formed.append ("\n".join (["\t".join ([str (j) for j in i]) for i in [self.m.add, self.m.angle]]))
        formed = "\n\n\n".join (formed)
        if not self.file:
            f = filedialog.asksaveasfilename (initialfile = "Figure", defaultextension = "*.pypt3", filetypes = (("Python 3D plot file", "*.pypt3"),))
            if f: self.file = f
        if self.file:
            with open (self.file, "w") as f: f.write (formed)

    def saveas (self):
        f = filedialog.asksaveasfilename (initialfile = "Figure", defaultextension = "*.pypt3", filetypes = (("Python 3D plot file", "*.pypt3"),))
        if f: self.file = f
        if self.file: self.save ()

    def open (self):
        f = filedialog.askopenfilename (defaultextension = "*.pypt3", filetypes = (("Python 3D plot file", "*.pypt3"),))
        if f:
            self.file = f
            with open (self.file) as f: formed = [i.split ("\n") for i in f.read ().split ("\n\n\n")]
            self.m.add, self.m.angle = [float (i) for i in formed [-1] [0].split ("\t")], [float (i) for i in formed [-1] [1].split ("\t")]
            proc = []
            for i in formed [ : -1]:
                i [0] = int (i [0])
                if i [0] in [0, 1, 2]: proc.append ([i [0], [float (j) for j in i [1].split ("\t")], None])
                elif i [0] == 3: proc.append ([i [0], [float (j) for j in i [1].split ("\t")], (i [2],)])
                elif i [0] == 4: proc.append ([i [0], [[float (k) for k in j.split ("\t")] for j in i [1].split ("\t\t")], None])
                elif i [0] == 5: proc.append ([i [0], [tk3d.wf (int (j.split ("\t") [0]), [[float (l) for l in k.split (" ")] if int (j.split ("\t") [0]) == 2 else float (k) for k in j.split ("\t") [1 : ]]) for j in i [1].split ("\t\t")], int (i [2])])
                elif i [0] == 6: proc.append ([i [0], float (i [1]), None])
            self.m.coords = proc
            process_co (self.m, True, self.m.c.winfo_width (), self.m.c.winfo_height (), self.m.c.cget ("bg"))
