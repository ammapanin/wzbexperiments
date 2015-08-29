import Tkinter as tk

# Add dashes for uncertainty, etc
# Add straight line for p = 1
# Include dashes on lines
# Get arcs
# Add time bar arrow
# Add select pie highlighting

class SquarePie(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        self.config(bg = "pink")
        self.pack(fill = "both", expand = True)

        self.nsteps = 12
        self.amounts = (("C", "X"), ("C", "Y"))
        self.times = ((3, 6), (3, 9))
        
        self.pie = self.create_oval(4, 4, 60, 60)
        self.prospect = self.draw_prospect()
        self.amount_figs = self.draw_amounts()

        self.positions = {"h0": 10,
                          "slant_x": 50,
                          "end_offset": 50,
                          "nsteps": 12}
        
        self.bind("<Configure>", self.resize)

    def draw_prospect(self):
        lines = [self.create_line(0, 0, 1, 1) for i in range(0, 8)]
        return lines

    def draw_amounts(self):
        amounts = [self.create_text(0, 0, text = amt)
                   for stream in self.amounts
                   for amt in stream]
        return amounts
    
    def resize(self, event):
        h0 = self.positions["h0"]
        xslant = self.positions["slant_x"]
        end_offset = self.positions["end_offset"]
        nstep = self.positions["nsteps"]
        
        h = self.winfo_height()
        w = self.winfo_width()

        mid = h / 2
        pie_radius = mid - h0
    
        xpivot = h0 + 2 * pie_radius
        xstart = h0 + 2 * pie_radius + xslant
        xend = w - end_offset
        bar = xend - xstart
        bar_step = bar / nstep

        print bar_step
        yline1 = (h + 6 * h0) / 8
        yline2 = (7 * h - 6 * h0) / 8
        ylines = (yline1, yline2)
        
        xtimes = [xstart + t * bar_step
                  for stream in self.times
                  for t in stream]
      
        # self.positions = {"h0": h0,
        #                   "xstart": h0 + 2 * pie_radius + xslant,
        #                   "xend": w - end_offset,
        #                   "pie_x": h0,
        #                   "pie_y": h - h0,
        #                   "pie_center": (mid, mid),
        #                   "pie_radius": mid - h0,
        #                   "dimensions": (w, h)}

        self.coords(self.pie, h0, h0, h - h0, h - h0)
        self.update_prospect(xpivot, xstart, xend, xtimes,
                             mid, yline1, yline2)
        self.update_amounts(xtimes, ylines)

    def update_prospect(self, xpivot, xstart, xend, xtimes, y0, y1, y2):
        xt11, xt12, xt21, xt22 = xtimes
        l1, l2, l3, l4, l5, l6, l7, l8 = self.prospect

        self.coords(l1, xpivot, y0, xstart, y1)
        self.coords(l2, xstart, y1, xt11, y1)
        self.coords(l3, xt11, y1, xt12, y1)
        self.coords(l4, xt12, y1, xend, y1)
        
        self.coords(l5, xpivot, y0, xstart, y2)
        self.coords(l6, xstart, y2, xt21, y2)
        self.coords(l7, xt21, y2, xt22, y2)
        self.coords(l8, xt22, y2, xend, y2)
        return None
    
    def update_amounts(self, xtimes, ylines):
        c1, x1, c2, x2 = self.amount_figs
        xt11, xt12, xt21, xt22 = xtimes
        yline1, yline2 = ylines
        
        self.coords(c1, xt11, yline1)
        self.coords(x1, xt12, yline1)
        self.coords(c2, xt21, yline2)
        self.coords(x2, xt22, yline2)
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
