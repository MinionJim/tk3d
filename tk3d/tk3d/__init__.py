from __future__ import division # To allow Python 2 float division

"""
A library for a 3D Tkinter Canvas (Python 3 only).
The library is pure-Python (so doesn't require installing) and requires the following modules that come with a standard installation:
    - tkinter
    - threading
    - os
    - sys
    - math
    - multiprocessing
    - time
    - traceback
    - tempfile

Optional additional libraries:
    PIL - This allows the screen to be saved as an image
          It does not come with a standard installation.
    ctypes - This is used to set the process dpi awareness (if called)
             It does come with a standard installation.
    opencv (cv2) - This allows the figure to be animated into a video.
                    It does not come with a standard installation.

Currently, you can create standard objects like lines, rectangles and cuboids.
On top of this, however, you can plot lines and wireframes like the following (where 'c' is the 3D canvas):
Line example:
y = array (-10, 4, 0.1)
x = sin (y * 2)
z = cos (y * 2)
c.plot (x, y, z)

Wireframe example:
x, z = wireframe (-3, 3, 0.2, -3, 3, 0.2)
y = cos (x * 2) + cos (z * 2)
c.plot_wireframe (x, y, z)


To create a 3D canvas, treat it like a tkinter frame (like the following):
c = Canvas3 (root)
c.pack (expand = True, fill = "both")

Please note: the place geometry manager is not supported

WARNING!!!
    Any script that calls must have the main code protected:
        if __name__ == "__main__":
            <your stuff>
    Otherwise the multiprocessing used to optimise the render will call multiple instances of your program.

    The master to the canvas is recommended to be either a Tk or Toplevel window (it was designed to work like this).
"""

import sys, math, warnings, os

if __name__ == "__main__": sys.path.append (os.path.split (os.path.abspath ("")) [0])

import tk3d.examples
from tk3d.coordinate_processor import *
from tk3d.export import export
from tk3d.inout import *

try:
    # Python 3
    from tkinter import *
except:
    # Python 2
    from Tkinter import *

try:
    import PIL.Image, PIL.ImageDraw
    SAVE_IMAGE = True
except:
    try:
        sys.path.append ("PIL.egg")
        import PIL.Image, PIL.ImageDraw
        SAVE_IMAGE = True
    except: SAVE_IMAGE = False

class Canvas3 (Frame, object):

    """
The main canvas for 3D objects.
It can be used simply to draw your own 3D objects, or, can be used to plot lines / wireframes.

The following methods can be used to draw objects:
    create_axis
    create_cuboid
    create_line
    create_rectangle
    create_text
    plot
    plot_wireframe

The following methods can be used to change the current view:
    view_angle
    view_offset
    recentre

Other methods:
    delete
    demo

Classes:
    canvas_object
    """

    angle = [0, 0, 0]
    add = [0, 0, 5]
    sensitivity = 25
    accelerate = 1.2

    def __init__ (self, *args, **kw):
        """
The following arguments (on top of the standard tkinter frame & canvas keywords) are accepted:
    axes -         If set to true, the axes are drawn in the top-right-hand corner of the canvas.
                   This can be useful to show the orientation of the object without having axes in the main part (potentially obstructing the view).
                   Default true.
    bind_mouse -   If set to true, the canvas will have bindings to repond to user clicks, drags, etc.
                   Default true.
    bind_keys -    If set to true, the master to the widget will have bindings to allow the canvas to repond to key strokes.
                   Default true.
    menu_bar -     If set to true, a menu wil be added to the master (if possible) to help manipulate the canvas.
                   Default true.
        """
        
        try: self.axis = kw.pop ("axes")
        except: self.axis = True
        if not isinstance (self.axis, bool): raise Exception ("Wrong type given for the 'axes' keyword.\nExpected bool got '%s'" % type (self.axis).__name__)

        try: menu_bar = kw.pop ("menu_bar")
        except: menu_bar = True
        if not isinstance (menu_bar, bool): raise Exception ("Wrong type given for the 'menu_bar' keyword.\nExpected bool got '%s'" % type (self.axis).__name__)

        try: bind_mouse = kw.pop ("bind_mouse")
        except: bind_mouse = True
        if not isinstance (bind_mouse, bool): raise Exception ("Wrong type given for the 'bind_mouse' keyword.\nExpected bool got '%s'" % type (self.axis).__name__)

        try: bind_keys = kw.pop ("bind_keys")
        except: bind_keys = True
        if not isinstance (bind_keys, bool): raise Exception ("Wrong type given for the 'bind_keys' keyword.\nExpected bool got '%s'" % type (self.axis).__name__)

        self.sup = super (type (self), self)
        self.sup.__init__ (*args)
        
        self.c = Canvas (self, **kw)

        self.coords, self.corresponding = [], []

        if menu_bar:

            m = Menu (self)
            
            file = Menu (self, tearoff = False)
            sh = save_handeller (self)
            file.add_command (command = sh.open, label = "Open (Ctrl+O)")
            file.add_command (command = sh.save, label = "Save (Ctrl+S)")
            file.add_command (command = sh.saveas, label = "Save As (Ctrl+Alt+S)")
            if SAVE_IMAGE:
                file.add_separator ()
                file.add_command (command = lambda: export (self), label = "Export (Ctrl-E)")
            file.add_separator ()
            file.add_command (command = self.master.destroy, label = "Exit")
            m.add_cascade (menu = file, label = "File")

            view = Menu (self, tearoff = False)
            view.add_command (command = lambda: self.__zoom (0), label = "Zoom in (+)")
            view.add_command (command = lambda: self.__zoom (1), label = "Zoom out (-)")
            view.add_command (command = self.__auto_zoom, label = "Auto-zoom (Ctrl-A)")
            view.add_separator ()
            view.add_command (command = self.__reset_angle, label = "Reset angle")
            view.add_command (command = lambda: self.__fine_angle (self), label = "Fine angle")
            view.add_separator ()
            view.add_command (command = self.__reset_offset, label = "Reset offset")
            view.add_command (command = lambda: self.__fine_offset (self), label = "Fine offset")
            view.add_separator ()
            view.add_command (command = self.recentre, label = "Recentre (Ctrl-R)")
            view.add_separator ()
            view.add_command (command = self.__toggle_fullscreen, label = "Fullscreen (F11)")
            m.add_cascade (menu = view, label = "View")
            
            try: self.master.config (menu = m)
            except: warnings.warn ("Unable to add menu-bar.")

        if bind_mouse:
            self.c.bind ("<Configure>", lambda event: self.__redraw ())
            self.c.bind ("<Button-1>", lambda event: self.__rotate (True, event))
            self.c.bind ("<Button1-Motion>", lambda event: self.__rotate (False, event))
            self.c.bind ("<Button-3>", lambda event: self.__drag (True, event))
            self.c.bind ("<Button3-Motion>", lambda event: self.__drag (False, event))
            self.c.bind ("<MouseWheel>", self.__zoom)

        if bind_keys:
            #self.master.bind ("<+>", lambda event: self.__zoom (0))
            self.master.bind ("<plus>", lambda event: self.__zoom (0))
            self.master.bind ("<minus>", lambda event: self.__zoom (1))
            self.master.bind ("<Control-s>", lambda event: sh.save ())
            self.master.bind ("<Control-o>", lambda event: sh.open ())
            self.master.bind ("<Control-Alt-s>", lambda event: sh.saveas ())
            self.master.bind ("<Escape>", lambda event: self.__toggle_fullscreen (True))
            self.master.bind ("<Control-e>", lambda event: export (self))
            self.master.bind ("<F11>", lambda event: self.__toggle_fullscreen ())
            self.master.bind ("<Control-a>", lambda event: self.__auto_zoom ())
            self.master.bind ("<Control-r>", lambda event: self.recentre ())
            self.master.bind ("<w>", lambda event: self.__rotate_keys (0))
            self.master.bind ("<a>", lambda event: self.__rotate_keys (1))
            self.master.bind ("<s>", lambda event: self.__rotate_keys (2))
            self.master.bind ("<d>", lambda event: self.__rotate_keys (3))
            self.master.bind ("<Up>", lambda event: self.__offset_keys (0))
            self.master.bind ("<Left>", lambda event: self.__offset_keys (1))
            self.master.bind ("<Down>", lambda event: self.__offset_keys (2))
            self.master.bind ("<Right>", lambda event: self.__offset_keys (3))

    def create_line (self, *coords):
        """
Add a line to the canvas. It takes 6 coordinates as start and end points:
create_line (x1, y1, z1, x2, y2, z2)
        """
        if len (coords) != 6: raise Exception ("Wrong number of coordinates provided. Expected 6, got %s." % len (coords))
        self.coords.append ((0, coords, None))
        self.__redraw ()
        return self.canvas_object (self, 0)

    def create_rectangle (self, *coords):
        """
Add a rectangle to the canvas. It takes 6 coordinates as opposite corners:
create_rectangle (x1, y1, z1, x2, y2, z2)

If there is a change in just two dimentions, it will be drawn as a standard rectangle between these points.
However, if there is a change in 3 dimentions, one pair of sides will be the change in the y-axis and the other will be the change in the x- and z-axes.
        """
        if len (coords) != 6: raise Exception ("Wrong number of coordinates provided. Expected 6, got %s." % len (coords))
        self.coords.append ((1, coords, None))
        self.__redraw ()
        return self.canvas_object (self, 1)

    def create_cuboid (self, *coords):
        """
Add a cuboid to the canvas. It takes 6 coordinates as opposite corners:
create_cuboid (x1, y1, z1, x2, y2, z2)
        """
        if len (coords) != 6: raise Exception ("Wrong number of coordinates provided. Expected 6, got %s." % len (coords))
        self.coords.append ((2, coords, None))
        self.__redraw ()
        return self.canvas_object (self, 2)

    def create_text (self, *coords, **kw):
        """
Add some text to the canvas. It takes 3 coordinates and the text is taken as a keyword:
create_text (x, y, z, text = t)
        """
        if len (coords) != 3: raise Exception ("Wrong number of coordinates provided. Expected 3, got %s." % len (coords))
        try: text = kw.pop ("text")
        except: text = ""
        self.coords.append ((3, coords, (text,)))
        self.__redraw ()
        return self.canvas_object (self, 3)

    def plot (self, *coords):
        """
Plot a line on the canvas. It takes 3 arrays containing the x, y and z positions:
plot (x_array, y_array, z_array)

For how to use an array, see the class help.
        """
        if len (coords) != 3: raise Exception ("Wrong number of coordinates provided. Expected 3, got %s." % len (coords))
        self.coords.append ((4, coords, None))
        self.__redraw ()
        return self.canvas_object (self, 4)

    def plot_wireframe (self, *coords, **kw):
        """
Plot a wireframe on the canvas. It takes 3 wireframe arrays containing the x, y and z positions:
plot_wireframe (x_wireframe, y_wireframe, z_wireframe)
        """
        if len (coords) != 3: raise Exception ("Wrong number of coordinates provided. Expected 3, got %s." % len (coords))
        try: step = kw.pop ("step")
        except: step = 1
        self.coords.append ((5, coords, step))
        self.__redraw ()
        return self.canvas_object (self, 5)

    def create_axes (self, length):
        """
Add axes to the the canvas. It takes just the length of the axis as they are centred at (0, 0, 0):
create_axes (length)
        """
        self.coords.append ((6, length, None))
        self.__redraw ()
        return self.canvas_object (self, 6)

    def delete (self, canvas_object):
        """
Delete a canvas object. For example:
line = c.create_line (0, 0, 0, 1, 1, 1)
c.delete (line)

Alternatively, use the canvas object's destroy method:
line = c.create_line (0, 0, 0, 1, 1, 1)
line.destroy ()
        """
        ind = len ([i for i in self.corresponding [ : canvas_object.id - 1] if i])
        self.corresponding [canvas_object.id - 1] = False
        del self.coords [ind]
        self.__redraw ()

    def view_angle (self, x, y, z, angle_type = "r"):
        """
Set the view angle for the canvas. It takes the x, y and z view angles and the angle type:
view_angle (0, 90, 0, 'd')

The angle type should either be 'r' (for radians - default) or 'd' (for degrees).
        """
        if angle_type != "r" and angle_type != "d": raise Exception ("Unknown angle type given. Expected 'r' or 'd', got '%s'." % angle_type)
        if angle_type == "d": self.angle = (math.radians (x), math.radians (y), math.radians (z))
        else: self.angle = (x, y, z)
        self.__redraw ()

    def view_offset (self, x, y):
        """
Set the view x-y offset. It takes the new x and y offset:
view_offset (1, 1)
        """
        self.add [0], self.add [1] = x, y
        self.__redraw ()

    def recentre (self):
        """
Recentre the canvas by resetting the view angle and offset. This takes no arguments:
recentre ()
        """
        self.angle, self.add = (0, 0, 0), [0, 0, self.add [2]]
        self.__redraw ()

    def demo (self = None):
        """
A demonstration of the 3D canvas using a plotted wireframe. This takes no arguments:
demo ()
        """
        tk3d.examples.wireframe ()
        #tk3d.examples.helix ()

    class canvas_object:

        """
The class returned when an object is created.
It contains a unique ID used when deleting the object.
To delete the object, either call the canvas' delete method or this class' destroy method.
        """

        def __init__ (self, master, type_):
            master.corresponding.append (True)
            self.master, self.type, self.id = master, ["line", "rectangle", "cuboid", "text", "plot", "wireframe", "axis"] [type_], len (master.corresponding)

        def destroy (self): self.master.delete (self)

        def __str__ (self): return "A 3D Canvas %s with ID %s" % (self.type, self.id)
        def __repr__ (self): return str (self)

    class __fine_angle (Toplevel, object):

        def __init__ (self, m):
            super (type (self), self).__init__ ()
            self.focus_force ()
            self.grab_set ()
            self.resizable (False, False)
            self.m = m
            self.create_widgets ()

        def create_widgets (self):
            self.x, self.y, self.z = IntVar (value = math.degrees (self.m.angle [0]) % 360), IntVar (value = math.degrees (self.m.angle [1]) % 360), IntVar (value = math.degrees (self.m.angle [2]) % 360)
            Label (self, text = "Set rotation:", font = ("times", 15)).grid (row = 0, column = 0, columnspan = 2)
            Label (self, text = "X:").grid (row = 1, column = 0)
            Scale (self, orient = "horizontal", length = 500, from_ = 0, to = 360, resolution = 2, variable = self.x).grid (row = 1, column = 1)
            Label (self, text = "Y:").grid (row = 2, column = 0)
            Scale (self, orient = "horizontal", length = 500, from_ = 0, to = 360, resolution = 2, variable = self.y).grid (row = 2, column = 1)
            Label (self, text = "Z:").grid (row = 3, column = 0)
            Scale (self, orient = "horizontal", length = 500, from_ = 0, to = 360, resolution = 2, variable = self.z).grid (row = 3, column = 1)
            self.x.trace ("w", lambda a, b, c: self.redraw ())
            self.y.trace ("w", lambda a, b, c: self.redraw ())
            self.z.trace ("w", lambda a, b, c: self.redraw ())

        def redraw (self):
            self.m.angle = (math.radians (self.x.get ()), math.radians (self.y.get ()), math.radians (self.z.get ()))
            process_co (self.m, True, self.m.c.winfo_width (), self.m.c.winfo_height (), self.m.c.cget ("bg"))

    class __fine_offset (Toplevel, object):

        def __init__ (self, m):
            super (type (self), self).__init__ ()
            self.focus_force ()
            self.grab_set ()
            self.resizable (False, False)
            self.m = m
            self.create_widgets ()

        def create_widgets (self):
            self.x, self.y = DoubleVar (value = round (self.m.add [0], 1)), DoubleVar (value = round (self.m.add [1], 1))
            Label (self, text = "Set offset:", font = ("times", 15)).grid (row = 0, column = 0, columnspan = 2)
            Label (self, text = "X:").grid (row = 1, column = 0)
            Scale (self, orient = "horizontal", length = 500, from_ = -10, to = 10, resolution = 0.1, variable = self.x).grid (row = 1, column = 1)
            Label (self, text = "Y:").grid (row = 2, column = 0)
            Scale (self, orient = "horizontal", length = 500, from_ = -10, to = 10, resolution = 0.1, variable = self.y).grid (row = 2, column = 1)
            self.x.trace ("w", lambda a, b, c: self.redraw ())
            self.y.trace ("w", lambda a, b, c: self.redraw ())

        def redraw (self):
            self.m.add = (self.x.get (), self.y.get (), self.m.add [2])
            process_co (self.m, True, self.m.c.winfo_width (), self.m.c.winfo_height (), self.m.c.cget ("bg"))

    def __redraw (self):
        # This is the internal method to redraw / refresh the canvas when required
        process_co (self, True, self.c.winfo_width (), self.c.winfo_height (), self.c.cget ("bg"))
        self.update ()

    def __rotate (self, start, event):
        # This is the internal method to control view rotation with mouse movement
        if start: self.rorig = (event.x, event.y, self.angle [0], self.angle [1], self.angle [2])
        else:
            height = self.c.winfo_height ()
            x_val = (self.rorig [1] - event.y) / height
            if x_val >= 0: x_mul = 1
            else: x_mul = -1
            x_val = abs (x_val) ** self.accelerate * x_mul / 5 * self.sensitivity
            y_val = (self.rorig [0] - event.x) / height
            if y_val >= 0: y_mul = 1
            else: y_mul = -1
            y_val = abs (y_val) ** self.accelerate * y_mul / 5 * self.sensitivity + self.rorig [3]
            z_val = math.sin (y_val) * x_val + self.rorig [4]
            x_val = math.cos (y_val) * x_val + self.rorig [2]
            self.angle = (x_val, y_val, z_val)
            self.rorig = (event.x, event.y, self.angle [0], self.angle [1], self.angle [2])
            self.__redraw ()

    def __rotate_keys (self, mode):
        if mode == 0: self.angle = (math.cos (self.angle [1]) * math.radians (5) + self.angle [0], self.angle [1], math.sin (self.angle [1]) * math.radians (5) + self.angle [2])
        elif mode == 1: self.angle = (self.angle [0], math.radians (5) + self.angle [1], self.angle [2])
        elif mode == 2: self.angle = (math.cos (self.angle [1]) * math.radians (-5) + self.angle [0], self.angle [1], math.sin (self.angle [1]) * math.radians (-5) + self.angle [2])
        else: self.angle = (self.angle [0], math.radians (-5) + self.angle [1], self.angle [2])
        self.__redraw ()

    def __drag (self, start, event):
        # This is the internal method to control view offset with mouse movement
        if start: self.orig = (event.x, event.y, self.add [0], self.add [1])
        else:
            height = self.c.winfo_height ()
            self.add = ((event.x - self.orig [0]) / height / 5 * self.sensitivity + self.orig [2], (self.orig [1] - event.y) / height / 5 * self.sensitivity + self.orig [3], self.add [2])
            self.__redraw ()

    def __offset_keys (self, mode):
        if mode == 0: self.add = (self.add [0], self.add [1] + 0.5, self.add [2])
        elif mode == 1: self.add = (self.add [0] - 0.5, self.add [1], self.add [2])
        elif mode == 2: self.add = (self.add [0], self.add [1] - 0.5, self.add [2])
        else: self.add = (self.add [0] + 0.5, self.add [1], self.add [2])
        self.__redraw ()

    def __zoom (self, event):
        # This is the internal method to control zoom with the mouse wheel
        if event == 0: z = 1
        elif event == 1: z = -1
        else: z = event.delta / 120
        self.add = (self.add [0], self.add [1], self.add [2] - z)
        self.__redraw ()

    def __auto_zoom (self):
        # This is the internal method to control the auto-zoom function
        self.add = (self.add [0], self.add [1], process_co (self, False, self.c.winfo_width (), self.c.winfo_height ()).get ())
        self.__redraw ()

    def __reset_angle (self):
        # This is an internal method to set the view angle to (0, 0, 0)
        self.angle = (0, 0, 0)
        self.__redraw ()

    def __reset_offset (self):
        # This is the internal method to set the view offset to (0, 0, z)
        # as z is the zoom and is left unaffected
        self.add = (0, 0, self.add [2])
        self.__redraw ()

    def __toggle_fullscreen (self, mode = False):
        # This is the internal method to toggle the fullscreen (inc. handelling the escape key)
        cur_full = self.master.attributes ("-fullscreen")
        if cur_full: self.master.attributes ("-fullscreen", False)
        elif not mode: self.master.attributes ("-fullscreen", True)

    # The geometry managers
    def pack (self, *args, **kw):
        self.sup.pack (*args, **kw)
        self.c.pack (expand = True, fill = "both")
    def grid (self, *args, **kw):
        self.sup.grid (*args, **kw)
        self.grid_rowconfigure (0, weight = 1)
        self.grid_columnconfigure (0, weight = 1)
        self.c.grid (row = 0, column = 0, columnspan = 3, sticky = "nsew")
    def place (self, *args, **kw):
        """
Not supported.
        """
        raise AttributeError ("The place geometry manager is not supported.")

class array (list):

    """
This is a single dimention list modified to allow for easy use of mathematical funcation.
For example:
array ([0, 1, 2]) + 1 # would return an array of [1, 2, 3]

This can be used a canvas plot like:
y = array (-4, 4, 0.1)
x, z = sin (y), cos (y)
c.plot (x, y, z)

The arguments taken can be:
    0 - creates a blank array
    1 - create an array of this argument
        e.g. array ([0, 1, 2, 3, 4]) would create an array of [0, 1, 2, 3, 4]
    3 - create an array with these being range arguments (start, end & step)
        e.g. array (0, 0.5, 0.1) would create an array of [0, 0.1, 0.2, 0.3, 0.4, 0.5]
    other - creates an array of these arguments
        e.g array (0, 1, 2, 3, 4) would create an array of [0, 1, 2, 3, 4]
    """

    def __init__ (self, *args):
        init = super ().__init__
        if len (args) == 0: init ()
        elif len (args) == 1: init (args [0])
        elif len (args) == 3: init ([i * args [2] for i in range (int (args [0] / args [2] + 1), int (args [1] / args [2] + 1))])
        else: init (args)

    # Handle trig. functions
    def sin (self): return array ([math.sin (i) for i in self])
    def cos (self): return array ([math.cos (i) for i in self])
    def radians (self): return array ([math.radians (i) for i in self])

    # Support numerical operators
    def __add__ (self, value): return array ([i + value for i in self])
    def __radd__ (self, value): return array ([i + value for i in self])
    def __abs__ (self): return array ([abs (i) for i in self])
    def __floordiv__ (self, value): return array ([i // value for i in self])
    def __rfloordiv__ (self, value): return array ([value // i for i in self])
    def __mod__ (self, value): return array ([i % value for i in self])
    def __rmod__ (self, value): return array ([value % i for i in self])
    def __mul__ (self, value): return array ([i * value for i in self])
    def __rmul__ (self, value): return array ([value * i for i in self])
    def __neg__ (self): return array ([-i for i in self])
    def __pos__ (self): return array ([+i for i in self])
    def __pow__ (self, value): return array ([i ** value for i in self])
    def __rpow__ (self, value): return array ([value ** i for i in self])
    def __sub__ (self, value): return array ([i - value for i in self])
    def __rsub__ (self, value): return array ([value - i for i in self])
    def __truediv__ (self, value): return array ([i / value for i in self])
    def __rtruediv__ (self, value): return array ([value / i for i in self])

    # Support numerical in-place operators
    def __iadd__ (self, value):
        self = array ([i + value for i in self])
        return self
    def __ifloordiv__ (self, value):
        self = array ([i // value for i in self])
        return self
    def __imod__ (self, value):
        self = array ([i % value for i in self])
        return self
    def __imul__ (self, value):
        self = array ([i * value for i in self])
        return self
    def __ipow__ (self, value):
        self = array ([i ** value for i in self])
        return self
    def __isub__ (self, value):
        self = array ([i - value for i in self])
        return self
    def __itruediv__ (self, value):
        self = array ([i / value for i in self])
        return self

class wf:

    """
The class used to create wireframes.
To initiate this class, please use the 'wireframe' method:
x, y = wireframe (start_1, end_1, step_1, start_2, end_2, step_2)

Similar to that of the 'array' class, the arguments given are to create a list with numbers in that range.
    """

    def __init__ (self, mode, *args):
        if len (args) == 1: self.l = list (args [0])
        elif len (args) == 3: self.l = [i * args [2] for i in range (int (args [0] / args [2] + 1), int (args [1] / args [2] + 1))]
        self.mode = mode

    # Handle trig. stuff
    def sin (self): return wf (self.mode, ([[math.sin (j) for j in i] for i in self.l] if self.mode == 2 else [math.sin (i) for i in self.l]))
    def cos (self): return wf (self.mode, ([[math.cos (j) for j in i] for i in self.l] if self.mode == 2 else [math.cos (i) for i in self.l]))
    def radians (self): return wf (self.mode, ([[math.radians (j) for j in i] for i in self.l] if self.mode == 2 else [math.radians (i) for i in self.l]))

    # Handle general stuff
    def __repr__ (self): return str (self.l)
    def __str__ (self): return str (self.l)
    def __len__ (self): return len (self.l)
    def __iter__ (self):
        for i in self.l: yield i
    def __getitem__ (self, index): return self.l [index]

    # Handle math stuff
    def __add__ (self, other):
        sm = self.mode
        if isinstance (other, wf):
            om = other.mode
            if sm == 0:
                if om == 0: return wf (0, self.l + list (other))
                elif om == 1: return wf (2, [[i + j for j in other] for i in self])
            elif sm == 1:
                if om == 0: return wf (2, [[i + j for j in self] for i in other])
                elif om == 1: return wf (1, self.l + list (other))
            else:
                if om == 2: return wf (2, self.l + list (other))
        elif sm == 0: return wf (0, [i + other for i in self])
        elif sm == 1: return wf (1, [i + other for i in self])
        else: return wf (2, [[j + other for j in i] for i in self])
    def __radd__ (self, other): return self.__add__ (other)
    def __sub__ (self, other):
        sm = self.mode
        if isinstance (other, wf):
            om = other.mode
            if sm == 0:
                if om == 1: return wf (2, [[i - j for j in other] for i in self])
            elif sm == 1:
                if om == 0: return wf (2, [[i - j for j in self] for i in other])
        elif sm == 0: return wf (0, [i - other for i in self])
        elif sm == 1: return wf (1, [i - other for i in self])
        else: return wf (2, [[j - other for j in i] for i in self])
    def __rsub__ (self, other):
        sm = self.mode
        if isinstance (other, wf):
            om = other.mode
            if sm == 0:
                if om == 1: return wf (2, [[j - i for j in other] for i in self])
            elif sm == 1:
                if om == 0: return wf (2, [[j - i for j in self] for i in other])
        elif sm == 0: return wf (0, [other - i for i in self])
        elif sm == 1: return wf (1, [other - i for i in self])
        else: return wf (2, [[other - j for j in i] for i in self])
    def __mul__ (self, other):
        sm = self.mode
        if isinstance (other, wf):
            om = other.mode
            if sm == 0:
                if om == 1: return wf (2, [[i * j for j in other] for i in self])
            elif sm == 1:
                if om == 0: return wf (2, [[i * j for j in self] for i in other])
        elif sm == 0: return wf (0, [i * other for i in self])
        elif sm == 1: return wf (1, [i * other for i in self])
        else: return wf (2, [[j * other for j in i] for i in self])
    def __rmul__ (self, other): return self.__mul__ (other)
    def __pow__ (self, other):
        sm = self.mode
        if isinstance (other, wf):
            om = other.mode
            if sm == 0:
                if om == 1: return wf (2, [[i ** j for j in other] for i in self])
            elif sm == 1:
                if om == 0: return wf (2, [[i ** j for j in self] for i in other])
        elif sm == 0: return wf (0, [i ** other for i in self])
        elif sm == 1: return wf (1, [i ** other for i in self])
        else: return wf (2, [[j ** other for j in i] for i in self])
    def __rpow__ (self, other):
        sm = self.mode
        if isinstance (other, wf):
            om = other.mode
            if sm == 0:
                if om == 1: return wf (2, [[j ** i for j in other] for i in self])
            elif sm == 1:
                if om == 0: return wf (2, [[j ** i for j in self] for i in other])
        elif sm == 0: return wf (0, [other ** i for i in self])
        elif sm == 1: return wf (1, [other ** i for i in self])
        else: return wf (2, [[other ** j for j in i] for i in self])

def sin (a):
    """
Perform the sine of the numbers (if provided a 'wf' or 'array').
If anthing else if given, 'math.sin' will be called on it.
    """
    if isinstance (a, array) or isinstance (a, wf): return a.sin ()
    else: return math.sin (a)
def cos (a):
    """
Perform the cosine of the numbers (if provided a 'wf' or 'array').
If anthing else if given, 'math.cos' will be called on it.
    """
    if isinstance (a, array) or isinstance (a, wf): return a.cos ()
    else: return math.cos (a)
def radians (a):
    """
Turn the numbers (if provided a 'wf' or 'array') from degrees into radians.
If anthing else if given, 'math.radians' will be called on it.
    """
    if isinstance (a, array) or isinstance (a, wf): return a.radians ()
    else: return math.radians (a)
def wireframe (start_1, end_1, step_1, start_2, end_2, step_2):
    """
Please see the help for the 'wf' class.
    """
    return wf (0, start_1, end_1, step_1), wf (1, start_2, end_2, step_2)
def dpi_awareness ():
    """
An easy way of calling:
ctypes.windll.shcore.SetProcessDpiAwareness (1)

Please note: This is only applicable for Windows. No effect will occur on other systems.

Put simply, on high DPI monitors, it allows for sharper graphics (good for precision work).
For technical information on it, please see:
https://docs.microsoft.com/en-us/windows/desktop/hidpi/high-dpi-desktop-application-development-on-windows
    """
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness (1)
    except:
        try:
            import warnings
            warnings.warn ("Unable to set DPI awareness.")
        except: pass

if __name__ == "__main__": Canvas3.demo ()
