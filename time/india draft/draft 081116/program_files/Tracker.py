#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk
import tkFont

class GradualTracker(tk.Canvas):
    def __init__(self, master, tracker_configs):
        """Create the tracker, called once for each new question

        Args:
        tracker_configs (dic) - a dictionary with keys
            elicit: (string) "amt" or "prob"
            minmax: (ints) tuple containing minimum and maximum amounts
            stimuli_step: (int) step of the interval
        """
        tk.Canvas.__init__(self, master)
        self.side = "horizontal"
        side_dic = {"horizontal": (1150, 100),
                      "vertical": (100, 900)}
        tracker_configs.update({"window":
                                side_dic.get(self.side)})
        self.stimuli_step = tracker_configs.get("stimuli_step")
        self.create_tracker(tracker_configs)
        self.pack(side = "left", fill = "y", expand = True)
        self.commodity = tracker_configs.get("commodity")

    def update_choice(self, choice, current):
        """Changes the position of one tracker rectangle, and slider

        Args:
        choice - (int) 0 or 1
        current - (int) amount under current consideration

        tvar is the var on the scale
        tracker vars control the rectangles
        """
        tmax, tmin = self.minmax
        tval = tmin + (tmax - current)
        self.tvar.set(tval)
        track_dic = dict(enumerate(self.lvars))
        tracker = track_dic.get(choice)
        tracker.set(current)

        return None

    def set_dimensions(self, tracker_configs):
        self.tmax, self.tmin = tmax, tmin = tracker_configs.get("minmax")
        w, h = tracker_configs.get("window")
        self.elicit = tracker_configs.get("elicit")
        side_dic = {"horizontal":  w - 70,
                    "vertical": h - 20}
        self.gauge = abs(tmax - tmin)
        self.minmax = tmax, tmin
        self.config(width = w, height = h)
        self.length = side_dic.get(self.side)
        return self.length

    def create_tracker(self, dims):
        xstart = 30
        tracker_width = 15
        slider_space = 20
        scale_width = tracker_width + slider_space - 7
        length = self.set_dimensions(dims)
        tmax, tmin = dims.get("minmax")

        if self.side == "horizontal":
            x1 = xstart
            x2 = xstart + length
            ya1 = xstart + 15
            ya2 = ya1 + tracker_width
            yb1 = ya2 + scale_width
            yb2 = yb1 + tracker_width
            xy = [(x1, ya1, x2, ya2), (x1, yb1, x2, yb2)]
            xslider = x1
            yslider = ya1 + slider_space
            xamt = x1
            yamt = ya1 - 15
            anchorxy = ((xstart - 15, yslider),
                        (x2 + 15, yslider))

        elif self.side == "vertical":
            xa1 = xstart
            xa2 = xstart + tracker_width
            y1 = xstart
            y2 = xstart + length
            xb1 = xa2 + scale_width
            xb2 = xb1 + tracker_width
            xy = [(xa1, y1, xa2, y2), (xb1, y1, xb2, y2)]
            xslider = xa2 + slider_space - 15
            yslider = y1
            xamt = xb2 + 8
            yamt = y1

        self.xy = xy
        self.draw_amount(xamt, yamt, anchorxy, (tmax, tmin))
        self.lvars = self.draw_lines(xy)
        self.slider = self.draw_slider((xslider, yslider),
                                       length,
                                       (tmin, tmax))

    def spring_back(self):
        """Take slider back to a certain point
        """
        self.tvar.set(self.xval)
        for xlines in self.confirm_idx:
            [self.itemconfig(xi, fill = "", outline = "") for xi in xlines]
        [self.itemconfig(i, fill = "black")
         for i in self.amounts]

    def confirmation_fill(self, last_choice):
        """Setup the tracker for the confirmations.
        """
        self.xval = self.tvar.get()
        val = self.tmin + (self.tmax - self.xval)
        direction = abs(1 - last_choice)
        [self.itemconfig(i, fill = "gray20")
         for i in self.amounts]
        self.itemconfig(self.amounts[direction], state = "hidden")
        x1, xstar, y1, y2, dist = self.set_fill_params(self.xy[0],
                                                    val,
                                                    fill_up = direction,
                                                    set_xstar = True)
        xpairs = [(x, y1, xstar, y2) for x, y1, x2, y2 in self.xy]
        self.confirm_idx = [[self.create_rectangle(x1, y1, x2, y2,
                                                   fill = "", outline = "")
                            for x1, y1, x2, y2 in self.xy] for i in (0, 1)]

        f = self.make_fill_func(var = self.tvar,
                                fill_up = True,
                                xpair = xpairs,
                                fillcol = ("red", "blue"),
                                amt_id = None,
                                fill_type = "confirm")
        self.tvar.trace("w", f)
        self.slider.config(state = "normal")
        return None

    def set_fill_params(self, xpair, val, fill_up, set_xstar = False):
        """Figure out the parameters to fill rectangles
        """
        x1, y1, x2, y2 = xpair
        scale_unit = float(self.length) / (self.gauge + self.stimuli_step)
        tmax, tmin = self.minmax

        amounts = range(self.tmin, self.tmax + self.stimuli_step)
        amounts.reverse()
        idx_dic = dict([(amt, idx) for idx, amt in enumerate(amounts, 1)])

        idx_dic[tmax] = 0.5
        if fill_up == False:
            val = min(self.tmax, val + self.stimuli_step)
        idx = idx_dic.get(val)

        dist = idx * scale_unit
        if set_xstar == True:
            x2 = x1 + dist
        return x1, x2, y1, y2, dist

    def make_fill_func(self, var, fill_up, xpair, fillcol, amt_id,
                       fill_type = "normal"):
        """Create functions to be tracked by variables
        """
        def fill_rectangle(name, index, mode):
            val = var.get()
            default_col = "gray"
            x1, x2, y1, y2, dist = self.set_fill_params(xpair, val, fill_up)

            if self.side == "horizontal":
                end = x1 + self.length
                new_idx = x1 + dist
                new_xypair_A = (x1, y1, new_idx, y2)
                new_xypair_B = (new_idx, y1, end, y2)
                xamt = new_idx

            if fill_up == True:
                colA = fillcol
                colB = default_col
            else:
                colA = default_col
                colB = fillcol

            col = new_xypair_A + (colA,)
            gray = new_xypair_B + (colB,)
            [self.create_rectangle(x1, y1, x2, y2,
                                   fill = f, outline = f, )
             for x1, y1, x2, y2, f in (col, gray)]
            self.coords(amt_id, xamt, self.amt_y)
            self.update_amount(amt_id)
            return None

        def fill_confirm(name, index, mode):
            def get_params(xp, fill_up):
                val = self.tmin + self.tmax - var.get()

                x1, xstar, y1, y2, dist = self.set_fill_params(xp, val, fill_up)
                end = x1 + self.length
                new_idx = x1 + dist

                if fill_up == True:
                    xcol_begin = min(xstar, new_idx)
                    xcol_end = max(xstar, new_idx)
                    xbase_begin = max(xstar, new_idx)
                    xbase_end = end
                    if new_idx < xstar:
                        base_col = fillcol[0]
                    else:
                        base_col = "gray"
                    new_xypairA = (xcol_begin, y1, xcol_end, y2, fillcol[0])
                    new_xypairB = (xbase_begin, y1, xbase_end, y2, base_col)
                    col = fillcol[0]
                else:
                    xcol_begin = min(new_idx, xstar)
                    xcol_end = max(xstar, new_idx)
                    xbase_begin = x1
                    xbase_end = min(new_idx, xstar)
                    if new_idx < xstar:
                        base_col = fillcol[1]
                    else:
                        base_col = "gray"
                    new_idx = min(xstar, new_idx)
                    new_xypairB = (xbase_begin, y1, xbase_end, y2, base_col)
                    new_xypairA = (xcol_begin, y1, xcol_end, y2, fillcol[1])
                    col = fillcol[1]
                return (new_xypairB, new_xypairA), col

            confirm_attribs = zip(xpair, (True, False), self.confirm_idx)
            for xp, fill_up, idx in confirm_attribs:
                new_xypairs, colour  = get_params(xp, fill_up)
                [self.coords(xi, a1, b1, a2, b2)
                 for xi, (a1, b1, a2, b2, col) in zip(idx, new_xypairs)]

                [self.itemconfig(xi,
                                 fill = "gray",
                                 outline = col,
                                 state = s)
                 for xi, (col, s) in zip(idx, (("gray", "normal"),
                                               (colour, "normal")))]
            return None

        if fill_type == "normal":
            fill_func = fill_rectangle
        elif fill_type == "confirm":
            fill_func = fill_confirm
        return fill_func

    def update_amount(self, amt_id):
        """Configure the tracker text according to the unit
        """
        amt_dic = {"euro": "\xe2\x82\xac",
                   "money": "Rs",
                   "tea": "g TEA"}
        amt = amt_dic.get(self.commodity)
        
        symbol_dic = {"prob": "%",
                      "amt": amt}

        value = '{}' + symbol_dic.get(self.elicit)
        current = float(self.tvar.get())
        slider_amt = int(self.tmin + (self.tmax - current))
        self.itemconfig(amt_id, 
                        text = value.format(slider_amt), 
                        state = "normal")
        return None

    def draw_amount(self, x, y, anchorxy, minmax):
        amt_font = tkFont.Font(size = 14, weight = "bold")
        anchor_font = tkFont.Font(size = 15)
        self.amt_y = y
        self.amounts = [self.create_text(x, y,
                                        anchor = a,
                                        text = 100,
                                         state = "hidden",
                                        font = amt_font)
                        for a in ("e", "w")]
        anchors = [self.create_text(xa, ya, text = ti, font = anchor_font)
                   for (xa, ya), ti in zip(anchorxy, minmax)]
#        self.tvar.trace("w", update_amount)
        return None

    def draw_lines(self, xy_pairs):
        for x1, y1, x2, y2 in xy_pairs:
            self.create_rectangle(x1, y1, x2, y2,
                                  fill = "gray", outline = "gray")

        line_vars = [tk.IntVar(self) for i in (0, 1)]
        fill_up = (True, False)
        fill_cols = ("red", "blue")
        fill_vals = zip(line_vars, self.amounts, fill_up, xy_pairs, fill_cols)
        fill_funcs = [self.make_fill_func(var, up, xpair, col, amt_id)
                      for var, amt_id, up, xpair, col in fill_vals]
        [v.trace("w", fill) for v, fill in zip(line_vars, fill_funcs)]
        return line_vars

    def draw_slider(self, window, slider_length, minmax):
        self.tvar = tk.IntVar()
        xs, ys = window
        smin, smax = minmax

        scale = tk.Scale(self,
                         from_ = smin,#self.stimuli_step,
                         to = smax,
                         resolution = self.stimuli_step,
                         length = slider_length,
                         showvalue = False,
                         variable = self.tvar,
                         orient = self.side,
                         state = "disabled")
        wi = self.create_window(xs, ys,
                                anchor = "nw",
                                window = scale)
        return scale



class ButtonTracker(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master, fill = "purple")
    def draw_buttons(self):
        pass

def trial():
    root  = tk.Tk()
    tracker_configs = {"elicit": "prob",
                       "minmax": (60, 38),
                       "stimuli_step": 1}
    bob = GradualTracker(root, tracker_configs)
    return bob


#k = trial()
