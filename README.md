# tk3d
## Description
This a library for a 3D Tkinter Canvas (Python 3 only).

Inpiration came from matplotlib's 3D functionaloty and I wanted to create something like that which would run on a standard installation without needing to be installed itself.

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
- PIL - This allows the screen to be saved as an image
- ctypes - This is used to set the process dpi awareness (if called)
- open-cv (cv2) - This allows the figure to be animated into a video

## Notes and warnings:
Please read these before proceeding. There isn't many of them but they are important to note.
 - Due to subprocessing being used, in a Windows OS, please protect your code like the following:
    if __name__ == "__main__":
        <your stuff>
   If this is not used, multiple instances of your program will be created.
 - The place geometry manager is not supported.
 - The master to the canvas is recommended to be either a Tk or Toplevel window.
   This is because a menu is created by default to help usage of the canvas.

## Functionality
Currently, the following methods are available to create objects:

- create_axes
- create_cuboid
- create_line
- create_rectangle
- create_text
- plot
- plot_wireframe

### create_axes
Add axes to the the canvas. It takes just the length of the axis as they are centred at (0, 0, 0):

    create_axes (length)

### create_cuboid
Add a cuboid to the canvas. It takes 6 coordinates as opposite corners:

    create_cuboid (x1, y1, z1, x2, y2, z2)

### create_line
Add a line to the canvas. It takes 6 coordinates as start and end points:

    create_line (x1, y1, z1, x2, y2, z2)

### create_rectangle
Add a rectangle to the canvas. It takes 6 coordinates as opposite corners:

    create_rectangle (x1, y1, z1, x2, y2, z2)

If there is a change in just two dimentions, it will be drawn as a standard rectangle between these points.
However, if there is a change in 3 dimentions, one pair of sides will be the change in the y-axis and the other will be the change in the x- and z-axes.

### create_text
Add some text to the canvas. It takes 3 coordinates and the text is taken as a keyword:

    create_text (x, y, z, text = t)

### plot
Plot a line on the canvas. It takes 3 arrays containing the x, y and z positions:

    plot (x_array, y_array, z_array)

For how to use an array, see the class help.

### plot_wireframe
Plot a wireframe on the canvas. It takes 3 wireframe arrays containing the x, y and z positions:

    plot_wireframe (x_wireframe, y_wireframe, z_wireframe)

## Examples
You can use the plot and wireframe functions like the following (where 'c' is the 3D canvas).
### Line example:
    y = array (-10, 4, 0.1)
    x = sin (y * 2)
    z = cos (y * 2)
    c.plot (x, y, z)

### Wireframe example:
    x, z = wireframe (-3, 3, 0.2, -3, 3, 0.2)
    y = cos (x * 2) + cos (z * 2)
    c.plot_wireframe (x, y, z)

### Initialisation:
To create a 3D canvas, treat it like a tkinter frame (like the following):
    c = Canvas3 (root)
    c.pack (expand = True, fill = "both")
