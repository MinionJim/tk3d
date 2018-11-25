import tk3d as pl
try:
    # Python 3
    from tkinter import *
except:
    # Python 2
    from Tkinter import *

def __example (mode):
    root = Tk ()
    root.title ("Example")
    root.focus_force ()

    c = pl.Canvas3 (root, bg = "white")
    c.pack (expand = True, fill = "both")

    if mode == 0:
        s1, s2 = 0.2, 1
        x, z = pl.wireframe (-3, 3, s1, -3, 3, s1)
        y = pl.cos (x * 3) + pl.cos (z * 3)
        c.plot_wireframe (x, y, z, step = s2)
    elif mode == 1:
        y = pl.array (-10, 5, 0.1)
        x, z = pl.sin (y * 2), pl.cos (y * 2)
        c.plot (x, y, z)
    elif mode == 2: c.create_cuboid (-1, -1, -1, 1, 1, 1)
    elif mode == 3: c.create_axes (5)
    elif mode == 4:
        del1 = c.create_line (1, 0, 0, 0, 1, 1)
        keep1 = c.create_line (0, 1, 0, 1, 0, 1)
        del2 = c.create_line (0, 0, 1, 1, 1, 0)

        keep2 = c.create_axes (5)

        del1.destroy ()
        del2.destroy ()

    root.mainloop ()

def wireframe (): __example (0)
def helix (): __example (1)
def cuboid (): __example (2)
def axes (): __example (3)
def delete (): __example (4)
