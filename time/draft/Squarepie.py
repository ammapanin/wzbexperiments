import Tkinter as tk

class SquarePie(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        self.config(bg = "pink")
        self.pack(fill = "both", expand = True)
        self.pie = self.create_oval(4, 4, 60, 60)
        self.prospect = self.draw_prospect()

        self.bind("<Configure>", self.resize)

    def resize(self, event):
        self.h0 = x0 = 10

        h = self.winfo_height()
        w = self.winfo_width()

        mid = h / 2
        self.origin = (mid , mid)        
        self.pie_radius = mid - x0
        self.height = h
        self.width = w
        self.coords(self.pie, x0, x0, h - x0, h - x0)
        new_prospect = self.calculate_prospect()
        self.update_prospect(*new_prospect)

    def draw_prospect(self):
        lines = [self.create_line(0, 0, 1, 1) for i in range(0, 4)]
        return lines

    def calculate_prospect(self):
        x0, y0 = self.origin
        xstart = x0 + self.pie_radius
        xslant = 50
        xslant_0 = xstart + xslant
        xend = self.width - xslant 
        yline1 = (self.height - 2 + 2 * self.h0) / 4
        yline2 = (3 * self.height - 2 * self.h0) / 4
        return xstart, xslant_0, xend, y0, yline1, yline2

    def update_prospect(self, x0, x1, x2, y0, y1, y2):
        l1, l2, l3, l4 = self.prospect
        self.coords(l1, x0, y0, x1, y1)
        self.coords(l2, x1, y1, x2, y1)
        self.coords(l3, x0, y0, x1, y2)
        self.coords(l4, x1, y2, x2, y2)
        return None

class Prospect(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        self.config(bg = "salmon")
        self.pack(fill = "both", expand = True)
        self.bind("<Configure>", self.resize)

    def add_pie(self):
        self.abjure = abjure = SquarePie(self)
        self.create_window(10, 10, anchor = "nw", window = abjure)
        return abjure

    def resize(self, event):
        h = self.winfo_height()
        w = self.winfo_width()
        self.abjure.config(width = w, height = h / 3)

def test_class():
    root = tk.Tk()
    abrogate = Prospect(root)
    return abrogate


y = test_class()

bob = y.add_pie()

"""
bilk - cheat
abrogate - repeal
abjure - solemnly renounce
"""
