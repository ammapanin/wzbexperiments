#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk

class Tea(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        self.pack()
        self.ystart = 40
        self.yheight = 220
        self.xstart = 10
        
    def draw_new_tea(self, amt):
        self.delete("all")
        kg, g = self.get_amounts(amt)
        if kg != 0:
            tea_txt = "{}kg and {}g".format(kg, g * 100)
        else:
            tea_txt = "{}g".format(g * 100)
        self.create_text(150, 20, text = tea_txt)
        kg_idx, x_max = self.draw_kg(kg)
        self.draw_g(g, x_max)
        self.config(height = self.bbox("all")[3], 
                    width =  self.bbox("all")[2])
        return None

    def get_amounts(self, amt):
        base = 1000
        kg = amt / base
        g = amt % base / 100
        return kg, g

    def draw_kg(self, n):
        x_length = 120
        x_pad = 30
        x_dist = x_length + x_pad
        x_start = self.xstart
        y0 = self.ystart
        y1 = y0 + self.yheight

        def get_coords(x0):
            x1 = x0 + x_length
            return x0, y0, x1, y1

        if n == 0:
            return None, self.xstart
        else:
            x_list = [x_start + x_dist * i 
                      for i in range(n)]
            coords = [get_coords(x) for x in x_list]
            idx = [self.make_rectangle(*c, g = "kg") 
                   for c in coords]
            x_max = max([c[2] for c in coords])
            return idx, x_max
    
    def make_rectangle(self, x0, y0, x1, y1, g):
        tx = x0 + float(x1 - x0) / 2
        ty = y0 + float(y1 - y0) / 2
        tdic = {"kg": "1 KG", "g": "100g"}
        tea_text = "TEA\n{}".format(tdic.get(g))
        r = self.create_rectangle(x0, y0, x1, y1)
        t = self.create_text(tx, ty, text = tea_text)
        return r, t

    def draw_g(self, n, x):
        y0 = self.ystart
        y_length = 60
        y_pad = 20
        y_dist = y_length + y_pad

        x_start = x + 10
        x_pad = 10
        x_length = 40
        x_dist = x_length + x_pad

        n_rows = 1 + (n / 3) 
        y_list = [y0 + i * y_dist for i in range(n_rows)]
        y_coords = [(y, y + y_length) for y in y_list]
        n_cols = [3 for i in range(n / 3)] \
                 + [n % 3] * (n % 3 != 0)

        x_list = [x_start + i * x_dist for i in range(3)]
        x_coords = [(x, x + x_length) for x in x_list]

        coords = list()
        for row, n in enumerate(n_cols):
            y = y_coords[row]
            x_cols = x_coords[0:n]
            row_cds = [(x[0], y[0], x[1], y[1]) 
                       for x in x_cols]
            coords.extend(row_cds)

        [self.make_rectangle(*c, g = "g") for c in coords]
        return coords

              


#root = tk.Tk()
#x = Tea(root)
