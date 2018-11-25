from __future__ import division
import math

class process_co:

    def __init__ (self, sup, mode, width = None, height = None, bg = None, image = False):
        """
An internal method used to redraw / refresh what is being viewed.
It is called by various bindings to to allow for live movement.

The 'image' keyword is used by the 'save' button to force the method to write to an image rather than the internal canvas.
        """
        self.sup = sup
        if mode:
            self.width, self.height, self.bg = width, height, bg
            if image: line, text, rect = self.sup.draw.line, self.sup.draw.text, self.sup.draw.rectangle
            else:
                self.sup.c.delete ("all")
                line, text, rect = self.sup.c.create_line, self.sup.c.create_text, self.sup.c.create_rectangle
            for create, coords, kw in self.sup.coords:
                if create == 0:
                    coords = self.__process (*coords)
                    if coords: line (coords, fill = "black")
                elif create == 1:
                    x1, y1, z1, x2, y2, z2 = coords
                    if x1 == x2: form = ((x1, y1, z1, x1, y2, z1), (x1, y2, z1, x1, y2, z2), (x1, y2, z2, x1, y1, z2), (x1, y1, z1, x1, y1, z2))
                    elif y1 == y2: form = ((x1, y1, z1, x2, y1, z1), (x2, y1, z1, x2, y1, z2), (x2, y1, z2, x1, y1, z2), (x1, y1, z1, x1, y1, z2))
                    elif z1 == z2: form = ((x1, y1, z1, x1, y2, z1), (x1, y2, z1, x2, y2, z1), (x2, y2, z1, x2, y1, z1), (x1, y1, z1, x2, y1, z1))
                    else: form = ((x1, y1, z1, x1, y2, z1), (x1, y2, z1, x2, y2, z2), (x2, y2, z2, x2, y1, z2), (x1, y1, z1, x2, y1, z2))
                    coords = [self.__process (x3, y3, z3, x4, y4, z4) for x3, y3, z3, x4, y4, z4 in form]
                    coords = [i for i in coords if i]
                    for i in coords: line (i, fill = "black")
                elif create == 2:
                    x1, y1, z1, x2, y2, z2 = coords
                    co = [self.__process (x3, y3, z3, x4, y4, z4)
                            for x3, y3, z3, x4, y4, z4 in
                            ((x1, y1, z1, x2, y1, z1),
                             (x2, y2, z1, x1, y2, z1),
                             (x1, y1, z1, x2, y1, z1),
                             (x2, y1, z2, x1, y1, z2),
                             (x1, y1, z1, x1, y2, z1),
                             (x1, y2, z2, x1, y1, z2),
                             (x2, y1, z1, x2, y2, z1),
                             (x2, y2, z2, x2, y1, z2),
                             (x1, y2, z1, x2, y2, z1),
                             (x2, y2, z2, x1, y2, z2),
                             (x1, y1, z2, x2, y1, z2),
                             (x2, y2, z2, x1, y2, z2),
                             (x1, y1, z1, x1, y1, z2),
                             (x2, y1, z1, x2, y1, z2),
                             (x1, y2, z1, x1, y2, z2),
                             (x2, y2, z1, x2, y2, z2))]
                    co = [i for i in co if i]
                    for i in co: line (i, fill = "black")
                elif create == 3:
                    coords = self.__process (*coords)
                    if coords: text (coords, text = kw [0], fill = "black")
                elif create == 4:
                    for i in range (len (coords [0]) - 1):
                        co = self.__process (coords [0] [i], coords [1] [i], coords [2] [i], coords [0] [i + 1], coords [1] [i + 1], coords [2] [i + 1])
                        if co: line (co, fill = "black")
                elif create == 5:
                    modes = [i.mode for i in coords]
                    pos = [modes [0], modes [1], modes [2]]
                    l = len (coords [pos [0]])
                    for i in range (l - (l - 1) % kw - 1):
                        for j in range (0, len (coords [pos [1]]), kw):
                            pos2 = [(i, j, (i, j)) [pos [k]] for k in range (3)] + [(i + 1, j, (i + 1, j)) [pos [k]] for k in range (3)]
                            pos2 = [coords [k % 3] [pos2 [k] [0]] [pos2 [k] [1]] if isinstance (pos2 [k], tuple) else coords [k % 3] [pos2 [k]] for k in range (6)]
                            co = self.__process (*pos2)
                            if co: line (co, fill = "black")
                    l = len (coords [pos [1]])
                    for i in range (0, len (coords [pos [0]]), kw):
                        for j in range (l - (l - 1) % kw - 1):
                            pos2 = [(i, j, (i, j)) [pos [k]] for k in range (3)] + [(i, j + 1, (i, j + 1)) [pos [k]] for k in range (3)]
                            pos2 = [coords [k % 3] [pos2 [k] [0]] [pos2 [k] [1]] if isinstance (pos2 [k], tuple) else coords [k % 3] [pos2 [k]] for k in range (6)]
                            co = self.__process (*pos2)
                            if co: line (co, fill = "black")
                elif create == 6:
                    from_ = [0, 0, 0]
                    for i in range (3):
                        to = [0, 0, 0]
                        to [i] = coords
                        co = self.__process (from_ [0], from_ [1], from_ [2], to [0], to [1], to [2])
                        if co:
                            x1, y1, x2, y2 = co
                            text ((x2, y2), text = ["X", "Y", "Z"] [i], fill = "black")
                            if x1 != x2 or y1 != y2: line ((x1, y1, x2, y2), fill = "black")

            width, height = self.width, self.height
            if self.sup.axis:
                rect ((width - (height / 5), -1, width, height / 5), fill = self.bg, outline = "black")
                from_ = [width - height / 10, height / 10]
                for i in range (3):
                    co = [0, 0, 0]
                    co [i] = 1
                    to = self.__with_angle (*co)
                    to = [(to [0] / (to [2] + 1.5)) * height / 10 + width - height / 10, height / 10 - (to [1] / (to [2] + 1.5)) * height / 10]
                    line ((from_ [0], from_ [1], to [0], to [1]), fill = "black")
                    text (to, text = ["X", "Y", "Z"] [i], fill = "black")
        else:
            co = []
            for create, coords, kw in self.sup.coords:
                if create in [0, 1, 2, 3]: co.extend ([self.__with_angle (*coords [i : i + 3]) for i in range (0, len (coords), 3)])
                elif create == 4:
                    for i in range (len (coords [0]) - 1): co.extend ([self.__with_angle (coords [0] [i], coords [1] [i], coords [2] [i]), self.__with_angle (coords [0] [i + 1], coords [1] [i + 1], coords [2] [i + 1])])
                elif create == 5:
                    modes = [i.mode for i in coords]
                    pos = [modes [0], modes [1], modes [2]]
                    l = len (coords [pos [0]])
                    for i in range (l - (l - 1) % kw - 1):
                        for j in range (0, len (coords [pos [1]]), kw):
                            pos2 = [(i, j, (i, j)) [pos [k]] for k in range (3)] + [(i + 1, j, (i + 1, j)) [pos [k]] for k in range (3)]
                            pos2 = [coords [k % 3] [pos2 [k] [0]] [pos2 [k] [1]] if isinstance (pos2 [k], tuple) else coords [k % 3] [pos2 [k]] for k in range (6)]
                            co.extend ([self.__with_angle (*pos2 [i : i + 3]) for i in range (0, len (pos2), 3)])
                    l = len (coords [pos [1]])
                    for i in range (0, len (coords [pos [0]]), kw):
                        for j in range (l - (l - 1) % kw - 1):
                            pos2 = [(i, j, (i, j)) [pos [k]] for k in range (3)] + [(i, j + 1, (i, j + 1)) [pos [k]] for k in range (3)]
                            pos2 = [coords [k % 3] [pos2 [k] [0]] [pos2 [k] [1]] if isinstance (pos2 [k], tuple) else coords [k % 3] [pos2 [k]] for k in range (6)]
                            co.extend ([self.__with_angle (*pos2 [i : i + 3]) for i in range (0, len (pos2), 3)])
                elif create == 6:
                    co.append ((0, 0, 0))
                    for i in range (3):
                        to = [0, 0, 0]
                        to [i] = coords
                        co.append (self.__with_angle (*to))
            self.get_cache = max ([max ([abs (i [0] + self.sup.add [0]) * height / width - i [2], abs (i [1] + self.sup.add [1]) - i [2]]) for i in co])

    def get (self): return self.get_cache

    def __with_angle (self, x, y, z):
        # This is the internal method that applies angle to the 3d coordinates
        x1 = x
        y1 = y * math.cos (self.sup.angle [0]) - z * math.sin (self.sup.angle [0])
        z1 = y * math.sin (self.sup.angle [0]) + z * math.cos (self.sup.angle [0])

        x2 = x1 * math.cos (self.sup.angle [2]) - y1 * math.sin (self.sup.angle [2])
        y2 = x1 * math.sin (self.sup.angle [2]) + y1 * math.cos (self.sup.angle [2])
        z2 = z1
        
        x3 = z2 * math.sin (self.sup.angle [1]) + x2 * math.cos (self.sup.angle [1])
        y3 = y2
        z3 = z2 * math.cos (self.sup.angle [1]) - x2 * math.sin (self.sup.angle [1])
        return [x3, y3, z3]
    
    def __reduce (self, x, y, z):
        # This is the internal method that turns 3d coordinates into 2d coordinates
        return (x + self.sup.add [0]) / (z + self.sup.add [2]), (y + self.sup.add [1]) / (z + self.sup.add [2])

    def __for_tkinter (self, x, y):
        # This is the internal method that adjusts coordinates to the canvas size
        # and makes the bottom left-hand corner (0, 0) rather than the top left-hand corner
        hw, hh = self.width / 2, self.height / 2
        return x * hh + hw, hh - y * hh
    
    def __process (self, *coords):
        # This handles the process of turning raw coordinates into positions for the canvas
        # and prevents negative or zero values for z
        coords = [self.__with_angle (*coords [i : i + 3]) for i in range (0, len (coords), 3)]
        if len (coords) == 1:
            if coords [0] [2] + self.sup.add [2] <= 0: return ()
        elif len (coords) == 2:
            if coords [0] [2] + self.sup.add [2] <= 0 and coords [1] [2] + self.sup.add [2] <= 0: return ()
            elif coords [0] [2] + self.sup.add [2] <= 0:
                coords [0] [0] = (coords [1] [2] + self.sup.add [2]) / (coords [1] [2] - coords [0] [2]) * (coords [0] [0] - coords [1] [0]) + coords [1] [0]
                coords [0] [1] = (coords [1] [2] + self.sup.add [2]) / (coords [1] [2] - coords [0] [2]) * (coords [0] [1] - coords [1] [1]) + coords [1] [1]
                coords [0] [2] = 0.1 - self.sup.add [2]
            elif coords [1] [2] + self.sup.add [2] <= 0:
                coords [1] [0] = (coords [0] [2] + self.sup.add [2]) / (coords [0] [2] - coords [1] [2]) * (coords [1] [0] - coords [0] [0]) + coords [0] [0]
                coords [1] [1] = (coords [0] [2] + self.sup.add [2]) / (coords [0] [2] - coords [1] [2]) * (coords [1] [1] - coords [0] [1]) + coords [0] [1]
                coords [1] [2] = 0.1 - self.sup.add [2]
        return [j for i in coords for j in self.__for_tkinter (*self.__reduce (*i))]
