# -*- coding: utf-8 -*-

# Risk and time - experiments round 2.
# Created: sometime early 2016, Last updated: 3.11.16

import Tkinter as tk
import tkFont
import tkMessageBox
import os
import csv
import itertools
import random

class SquarePie(tk.Canvas):
    def __init__(self, master, pie_configs):
        """pie_configs defined in PieScreen.add_pies()
        """
        tk.Canvas.__init__(self, master)
        self.config(bg = "ivory2",
                    highlightcolor = "green4",
                    highlightthickness = 5)
        self.pack(fill = "both", expand = True, anchor = "w")

        self.pie_colour = pie_configs.get("colour")
        self.prospect_tag = pie_configs.get("prospect_id")
        self.commodity = pie_configs.get("commodity")
        self.prob = tk.IntVar()
        self.prob.set(pie_configs.get("prob") * 100)

        self.states = ("normal", "normal", "normal", "normal")
        self.choice_pie = pie_configs.get("choice_pie")
        prob_type = pie_configs.get("prob_type")
        self.draw_display(prob_type)

    def draw_display(self, prob_type):
        """Draws all aspects of a single prospect display
        Args: prob_type (string) -- probability either pie or circles
        """
        self.prob_display = prob_type

        if prob_type == "pie":
            self.pie = self.draw_pie()
        elif prob_type == "circles":
            self.circles, self.ptext = self.draw_circles(4, 5)

        self.prospect = self.draw_prospect()
        self.amount_ids = self.draw_amounts()
        self.timelines = self.draw_timelines()
        self.ypositions = {"h0": 20}
        self.bind("<Configure>", self.resize)
        return None

    def select_pie(self, event):
        PieScreen.class_selected.set(self.prospect_tag)

    def update_choice(self, choice):
        """Changes the amount displayed in the choice of the pie

        self.choice_id is the canvas id of the choice to be updated
        """
        choice = self.format_amounts(choice)
        self.itemconfig(self.choice_id,
                        text = self.amt_text.format(choice))

    def update_stimuli(self, prob, amounts, elicit):
        self.elicit = elicit
        self.update_probability(prob)
        self.resize("event")
        self.update_amounts(amounts)

        if self.elicit == "prob":
            self.itemconfig(self.amount_ids[0],
                            fill = "black")
        else:
            if self.choice_pie == True:
                self.itemconfig(self.amount_ids[0],
                                state = "normal",
                                fill = "dark green")
            else:
                pass
        return None

    def resize(self, event):
        h = self.winfo_height()
        h0 = self.ypositions["h0"]

        mid = h / 2
        pie_radius = mid - h0

        if self.prob_display == "pie":
            xpivot = h0 + 2 * pie_radius
            self.resize_pie(h0, h)
        elif self.prob_display == "circles":
            #self.adjust_balls()
            xpivot = h0 + self.xmax + 40

        yline1 = (h + 6 * h0) / 8
        yline2 = (7 * h - 6 * h0) / 8
        ylines = (yline1, yline2)

        self.ypositions.update({"mid": mid, "ylines": ylines})
        xtags = ("xstart", "xend", "xtimes")
        xvalues = [PieScreen.xypositions.get(tag) for tag in xtags]

        (xstart, xend, xtimes) = xvalues
        xtimes_p = xtimes.get(self.prospect_tag)
        self.update_prospect(xpivot, xstart, xend, xtimes_p,
                             mid, yline1, yline2)
        self.update_timebox(h, xtimes_p, xstart, xend)

    def adjust_balls(self):
        xc0, yc0, xc1, yc1 = self.bbox("circle")
        xnew = xc1 + 10
        new_ptext_coords = ((xnew, yc0 + 3), 
                            (xnew, yc1 - 3))
        pconfig = zip(self.ptext, new_ptext_coords)
        [self.coords(pi, x, y) for pi, (x, y) in pconfig]
        
    def resize_pie(self, h0, h):
        pie, arc, ptext = [self.pie.get(tag) 
                           for tag in ("pie", "arc", "prob")]
        [self.coords(i, h0, h0, h - h0, h - h0) for i in (pie, arc)]
        pie_dims = [(h - h0 * 1, h0 * 2), (h - h0 * 1, h0 * 9)]
        [self.coords(p, x, y) for p, (x, y) in zip(ptext, pie_dims)]

    def update_certainty(self, xpivot, xend, xtimes, y1):
        xt11, xt12, xt21, xt22 = xtimes
        l1, l2, l3, l4, l5, l6, l7, l8 = self.prospect
        a1, a2, a3, a4 = self.amount_ids

        self.coords(l1, xpivot, y1, xt11, y1)
        self.coords(l2, xt11, y1, xend, y1)
        [self.itemconfig(i, state = "hidden")
         for i in self.risky_ids]

    def update_prospect(self, xpivot, xstart, xend, xtimes, y0, y1, y2):
        """Redraws the prospect arm depending on wether the prospect is
        risky or certain.

        -resize (tuple): either "certain" or "risky"
            determined by wether the probability of the prospect is 100 or 0.

        Also show or hide the lower arm (?)
        """
        certain = (self.resize_certain_lines,
                   ((xpivot, xend), y0, xtimes),
                   self.resize_certain_amounts,
                   (xtimes, y0))

        risky = (self.resize_risky_lines,
                 ((xpivot, xstart, xend), (y0, y1, y2), xtimes),
                 self.resize_risky_amounts,
                 (xtimes, (y1, y2)))

        labs = ("line_func", "line_args", "amt_func", "amt_args")
        bools = True, False
        fdics = [dict(zip(labs, dic)) for dic in (certain, risky)]
        resize_dic = {bprob: fdic for bprob, fdic in zip(bools, fdics)}

        resize = resize_dic.get(self.prob.get() == 100)

        resize["line_func"](*resize["line_args"])
        resize["amt_func"](*resize["amt_args"])

        if self.elicit == "prob":
            p_int = self.prob.get()
            states = self.toggle_amount_certainty(p_int)
        else:
            states = self.states

        time_states = zip(self.timelines, states)
        amt_states = zip(self.amount_ids, states)
        new_states = time_states + amt_states
        [self.itemconfig(i, state = s) for i, s in new_states]
        return None

    def toggle_amount_certainty(self, prob):
        c1, x, c2, y = self.states
        if prob == 100:
            states = (c1, x, "hidden", y)
        else:
            states = (c1, x, c2, y)
        return states

    def update_timebox(self, height, xtimes, xstart, xend):
        xspace = (xend - xstart) / 5
        xpad = xspace / 3

        [self.coords(i, x - xpad, 0, x + xpad, height)
         for i, x in zip(self.timelines, xtimes)]

        # Because I do not like the boxes
        [self.itemconfig(i, state = "hidden") for i in self.timelines]


    def trim_xtimes(self, xtimes, trim = (10,) * 4):
        """Make the lines a bit shorter so that they do not 
           collide with the text
        """
        xtrim = trim
        xtimes_trim = zip(xtimes, xtrim)
        xtimes = [x - c for x, c in xtimes_trim]
        return xtimes

    def resize_certain_lines(self, xpos, ypos, xtimes):
        xtimes = self.trim_xtimes(xtimes)
        xpivot, xend = xpos
        y1 = ypos
        xt11, xt12, xt21, xt22 = xtimes

        x_normal = [xt for xt, st in zip(xtimes, self.states) if st == "normal"]
        max_x = max(x_normal)
        l1, l2, l3, l4, l5, l6, l7, l8 = self.prospect

        self.coords(l1, xpivot, y1, xt11, y1)
        self.coords(l2, xt11, y1, max_x, y1)
        [self.itemconfig(i, state = "hidden") for i in self.risky_ids]
        return None

    def resize_risky_lines(self, xpos, ypos, xtimes):
        xpivot, xstart, xend = xpos
        y0, y1, y2 = ypos
        xt11, xt12, xt21, xt22 = self.trim_xtimes(xtimes)
        l1, l2, l3, l4, l5, l6, l7, l8 = self.prospect

        self.coords(l1, xpivot, y0, xstart, y1)
        self.coords(l2, xstart, y1, xt11, y1)
        self.coords(l3, xt11, y1, xt12, y1)
        #self.coords(l4, xt12, y1, xend, y1)

        self.coords(l5, xpivot, y0, xstart, y2)
        self.coords(l6, xstart, y2, xt21, y2)
        self.coords(l7, xt21, y2, xt22, y2)
        #self.coords(l8, xt22, y2, xend, y2)
        [self.itemconfig(i, state = "normal") for i in self.risky_ids]
        return None

    def show_and_texts(self):
        """Determines wether the and texts are shown

        First all are hidden, then various conditions are checked
        """
        [self.itemconfig(a, state = "hidden") for a in self.and_texts]

        s0, s1, s2, s3 = self.states
        a0, a1 = self.and_texts

        if s0 == s1 == "normal" and self.elicit == "amt":
            self.itemconfig(a0, state = "normal")

        if s2 == s3 == "normal":
            self.itemconfig(a1, state = "normal")
        return None

    def hide_na_amounts(self, amounts):
        state_dic = {True: "hidden", False: "normal"}
        self.states = [state_dic.get(a.lower() == "na") for a in amounts]
        [self.itemconfig(i, state = s)
         for i, s in zip(self.amount_ids, self.states)]

    def update_amounts(self, amounts):
        self.hide_na_amounts(amounts)
        self.show_and_texts()

        amounts = [self.format_amounts(amt) for amt in amounts]
        [self.itemconfig(i, text = self.amt_text.format(amt))
         for i, amt in zip(self.amount_ids, amounts)]
        return None

    def resize_certain_amounts(self, xtimes, ylines):
        c1, x1, c2, x2 = self.amount_ids
        xt11, xt12, xt21, xt22 = xtimes
        xand = (xt11 + xt12) / 2 + 8
        yline = ylines
        self.coords(c1, xt11, yline)
        self.coords(x1, xt12, yline)
        self.coords(self.and_texts[0], xand, yline)

    def resize_risky_amounts(self, xtimes, ylines):
        c1, x1, c2, x2 = self.amount_ids
        xt11, xt12, xt21, xt22 = xtimes
        xand = (xt11 + xt12) / 2
        yline1, yline2 = ylines

        self.coords(c1, xt11, yline1)
        self.coords(x1, xt12, yline1)
        self.coords(c2, xt21, yline2)
        self.coords(x2, xt22, yline2)
        [self.coords(a, xand, yline)
         for a, yline in zip(self.and_texts, ylines)]
        return None

    def draw_circles(self, nx, ny):
        """Draw the circles representing probabilities
        """
        space = 8
        xstart = 8
        ystart = 20
        xwidth = ywidth = 15
        xdist = ydist = xwidth + space

        x1 = range(xstart, (nx * xdist), xdist)
        x2 = [i + xwidth for i in x1]
        y1 = range(ystart, (ny * ydist), ydist)
        y2 = [i + ywidth for i in y1]
        self.xmax = x2[-1]
        yy = zip(y1, y2)

        xy_list = [zip(x1, itertools.cycle((y11,)), 
                       x2, itertools.cycle((y22,)))
                   for y11, y22 in yy]
        xy = [c for clist in xy_list for c in clist]

        circles = [self.create_oval(a, b, c, d, tag = "circle") 
                   for a, b, c, d in xy]

        qcol = "dark goldenrod"
        pfont = tkFont.Font(size = 15)
        
        px = self.xmax + 70
        pcoords = ((px, 45), (px, 150))
        prob_texts = [self.create_text(x, y,
                                      text = "",
                                      fill = self.pie_colour,
                                      font = pfont)
                      for x, y in pcoords]
        self.itemconfig(prob_texts[1], fill = qcol)

        def update_probability_circles(p):
            p = int(p * 1)
            
            p_fill = int(20 * float(p * 1) / 100)
            p_lower = 20 - p_fill
            probs = (p_fill, p_lower)

            [self.itemconfig(i, fill = self.pie_colour) 
             for i in circles[0: p_fill]]
            
            [self.itemconfig(i, fill = qcol) 
             for i in circles[p_fill:]]

            [self.itemconfigure(i, text = "{} tokens".format(p))
             for i, p in zip(prob_texts, probs)]
            self.resize("event")
            return None

        self.update_probability = update_probability_circles
        return circles, prob_texts

    def draw_probtext(self):
        tfont = tkFont.Font(size = 20, weight = "bold")
        text = self.create_text(self.xmax + 45, 45,
                                text = "50%",
                                fill = self.pie_colour,
                                font = tfont)
        return text

    def draw_pie(self):
        pfont = tkFont.Font(size = 20)
        self.pfont = pfont
        self.xmax = 55
        pie = self.create_oval(4, 4, 55, 55)
        arc = self.create_arc(4, 4, 55, 55,
                              extent = 270,
                              fill = self.pie_colour)
        prob_texts = [self.create_text(4, 4,
                                      text = "",
                                      fill = self.pie_colour,
                                      font = pfont)
                      for i in (0, 1)]
        self.itemconfig(prob_texts[1], fill = "dark gray")

        def update_probability_pies(prob):
            try:
                p_int = int(prob)
                p_lower = 100 - p_int
                pie_extent = 360 * float(prob) / 100 - 0.000000001
                self.prob.set(prob)
            except:
                p_int = "---"
                p_lower = "---"
                pie_extent = 0
            probs = (p_int, p_lower)

            self.itemconfigure(arc, extent = pie_extent)
            [self.itemconfigure(i, text = "{}%".format(p))
             for i, p in zip(prob_texts, probs)]
            self.resize("event")
            return None

        self.update_probability = update_probability_pies
        return {"pie": pie, "arc": arc, "prob": prob_texts}

    def draw_prospect(self):
        lines = [self.create_line(0, 0, 1, 1, dash = (2, 2))
                 for i in range(0, 8)]
        self.risky_ids = lines[2:]
        return lines

    def draw_timelines(self):
        lines = [self.create_rectangle(300, 0, 300, 20,
                                       fill = "light yellow",
                                       width = 0,
                                       state = "hidden")
                 for i in (0, 3)]
        [self.lower(i) for i in lines]
        return lines

    def format_amounts(self, amt):
        """To be used in places where the amount will be a string
        """
        try:
            int_amt = int(amt)
            if int_amt < 1000:
                amt = amt
            elif int_amt > 1000 and int_amt < 2000:
                amt_dec = float(amt) / 1000
                amt = "{}K".format(amt_dec)
        except:
            pass

        if str(amt) == "1000":
            amt = "1K"
        if str(amt) == "2000":
            amt = "2K"
        return amt

    def draw_amounts(self):
        """Create the text objects that will contain the amounts
        Returns: amount ids
        Called by: self.draw_display
        """

        if self.commodity == "tea":
            amtfont = tkFont.Font(size = 23)
        else:
            amtfont = tkFont.Font(size = 30)
        choicefont = tkFont.Font(size = 30)
        self.amtfont = amtfont
        self.choicefont = choicefont

        euro =  u'\u20AC'.encode("utf8")
        rupees = "Rs"
        tea = "g TEA"

        commodity_dic = {"money": rupees, "tea": tea}
        commodity = commodity_dic.get(self.commodity)

        self.amt_text = "{}" + commodity


        self.elicit_amt_font = {"font": choicefont,
                                "fill": "dark green"}

        amounts = [self.create_text(0, 0,
                                    text = ("{}" + euro).format(7),
                                    font = amtfont,
                                    anchor = "w") for x in range(0, 4)]
        self.and_texts = [self.create_text(0, 0,
                                           text = "AND",
                                           font = amtfont,
                                           anchor = "w")
                          for i in (0, 1)]

        if self.choice_pie == True:
            self.itemconfig(amounts[0],
                            font = choicefont,
                            fill  = "dark green",
                            tags = ("choice",))
            [self.itemconfig(s, font = amtfont) for s in amounts[1:]]
        self.choice_id  = amounts[0]
        return amounts


class PieScreen(tk.Canvas):
    xypositions = {"nsteps": 12,
                   "xend_offset": 5,
                   "bar_start_offset": 30,
                   "bar_end_offset": 70,
                   "pie_y_scale": float(7) / 20,
                   "pie_slant": 30,
                   "graphic_offset": 10,
                   "ystart_offset": 40,
                   "yend_offset": 20,
                   "xstart_offset": 10}

    def __init__(self, master, prob_type, commodity):
        tk.Canvas.__init__(self, master)
        self.config(highlightthickness = 0)
        self.pack(fill = "both", expand = True, anchor = "w")

        self.prob_type = prob_type
        self.commodity = commodity
        self.pies, self.pie_windows = self.add_pies()
        self.timeline = self.draw_timeline()

        self.bind("<Configure>", self.resize)
        self.times = {0: (3, 6, 3, 9), 1: (3, 6, 3, 12)}

        self.__class__.class_selected = tk.IntVar(self)
        self.selected =  self.__class__.class_selected
        self.selected.set(777)
        self.selected.trace("w", self.select_pie)
        self.elicit = "prob"

    def set_bindings(self, on):
        select_keys = ("<Up>", "<Down>")
        click = "<Button-1>"
        s_funcs = (self.select_up, self.select_down)

        if on == True:
            [self.bind_all(key, f)
             for key, f in zip(select_keys, s_funcs)]
            [pie.bind(click, pie.select_pie) for pie in self.pies]

        elif on == False:
            [self.unbind_all(key) for key in select_keys]
            [pie.unbind(click) for pie in self.pies]

    def update_question(self, stimulus, real):
        tags = ("p1", "p2", "t11", "t12", "t21", "t22", "qidx")
        try:
            p1, p2, t11, t12, t21, t22, qidx = [float(stimulus.get(t))
                                                for t in tags]
            p1, p2 = [p * 100 for p in (p1, p2)]

        except:
            print stimulus
        [pie.prob.set(p) for pie, p in zip(self.pies, (p1, p2))]

        if self.elicit == "prob":
            p1 = float(random.choice(range(0, 101))) / 100

        amt_tags = (("c11", "x12", "c12","y12"),
                    ("c21", "x22", "c22", "y22"))
        amounts = [[stimulus.get(at)
                    for at in amt_tag]
                   for amt_tag in amt_tags]

        ttuple_1 = (t11, t12, t11, t12)
        ttuple_2 = (t21, t22, t21, t22)

        if t11 != t21:
            self.month_cols = ["red"] * 4 +  ["blue"] * 4
        else:
            self.month_cols = ["black"] * 8
        self.times = {0: ttuple_1, 1: ttuple_2}
        self.set_xyvalues()


        pie_details = zip(self.pies, (p1, p2), amounts)
        [pie.update_stimuli(prob, amts, self.elicit)
         for pie, prob, amts in pie_details]

        self.update_timeline()
        if real == True:
            self.set_bindings(on = True)
        else:
            self.set_bindings(on = False)

    def end_question(self):
        self.selected.set(777)
        self.set_bindings(False)
        return None

    def select_pie(self, name, index, mode):
        pie = self.__class__.class_selected.get()
        if pie in (0, 1):
            self.pies[pie].focus_set()
        else:
            self.deselect_pies()
            pass

    def select_up(self, event):
        self.__class__.class_selected.set(0)

    def select_down(self, event):
        self.__class__.class_selected.set(1)

    def deselect_pies(self):
        self.selected.set(777)
        self.focus_set()

    def add_pies(self):
        """Makes the pie according to certain configurations.

           choice_pie (Bool): whether the pie is the one to be chosen
        """
        pie_configs = [{"colour": "red",
                        "prob": 0.5,
                        "prospect_id" : 0,
                        "choice_pie": True,
                        "prob_type": self.prob_type,
                        "commodity": self.commodity},
                       {"colour": "blue",
                        "prob": 0.8,
                        "prospect_id" : 1,
                        "prob_type": self.prob_type,
                        "commodity": self.commodity}]

        pies = [SquarePie(self, pc)
                for pc in pie_configs]
        windows = [self.create_window(0, 0, anchor = a, window = p)
                   for a, p in zip(("nw", "sw"), pies)]
        pie_select = "State whether you prefer the red or the blue option"

        info_font = tkFont.Font(size = 15)
        x, y = [self.__class__.xypositions.get(offset) for offset in
                ("xstart_offset", "ystart_offset")]
        self.create_text(x, y, text = pie_select,
                         anchor = "sw", font = info_font)
        return pies, windows

    def draw_timeline(self):
        """Creates the grey arrow timeline
        month_nrs (list) - list of the months to be displayed
        """
        month_fonts = tkFont.Font(size = 20)
        timeline = self.create_line(10, 10, 10, 10,
                                    width = 60,
                                    arrow = "last",
                                    arrowshape = [15, 40, 20],
                                    fill = "gray")
        m0 = "Tmrw"
        month_nrs = [0,0.5, 1, 2, 3, 4, 6, 9, 11, 11.5, 12]
        month_names = [m0] + [str(m) + "m" for m in month_nrs[1:]]
        months = [self.create_text(0, 0,
                                   text = ".", font = month_fonts)
                  for txt in month_names]
        month_names_txt = [self.create_text(0, 0,
                                            text = txt, font = month_fonts)
                           for txt in month_names]

        month_txts = dict(zip(month_nrs,
                              zip(months, month_names_txt)))
        # months = [self.create_text(0, 0,
        #                            text = txt, font = month_fonts)

        timeline_obj =  {"timeline": timeline,
                         "months2": month_txts,
                         "months": dict(zip(month_nrs, months))}
        return timeline_obj

    def update_timeline(self):
        normal_month = tkFont.Font(size = 12)
        bold_month = tkFont.Font(size = 12, weight = "bold")
        bold_dot = tkFont.Font(size = 25, weight = "bold")

        months = [t for stream in self.times.values() for t in stream]
        month_ids = self.timeline.get("months2")
        month_ids_tup = month_ids.values()

        for month_tup in month_ids_tup:
            dot, txt =  month_tup
            self.itemconfig(txt, state = "hidden",
                            font = normal_month, fill = "gray50")
            self.itemconfig(dot, font = normal_month, fill = "gray50")

        for m, mc in zip(months, self.month_cols):
            dot, txt =  month_ids[m]
            self.itemconfig(txt, state = "normal",
                            font = bold_month, fill = mc)
            self.itemconfig(dot, font = bold_dot, fill = mc)

    def resize_timeline(self, x0, x1, xtimes, mtimes, y):
        (x11, x12, x13, x14), (x21, x22, x23, x24) =  xtimes.values()

        timeline, ovals = [self.timeline.get(i)
                           for i in ("timeline", "ovals")]
        self.coords(timeline, x0, y, x1, y)

        months = zip(self.timeline.get("months2").values(), mtimes)
        for month_tup, mx in months:
            dot, txt =  month_tup
            self.coords(dot, mx, y - 10)
            self.coords(txt, mx, y + 12)

    def set_xyvalues(self):
        w = self.winfo_width()
        h = self.winfo_height()

        xtags = ("nsteps", "xstart", "xend_offset",
                 "bar_start_offset", "bar_end_offset",
                 "pie_y_scale", "pie_slant", "graphic_offset",
                 "ystart_offset", "xstart_offset", "yend_offset")
        xvalues = [self.__class__.xypositions.get(tag)
                   for tag in xtags]
        (nsteps, xstart, xend_offset,
         bar_start_offset, bar_end_offset,
         pie_y_scale, pie_slant, graphic_offset,
         ystart_offset, xstart_offset, yend_offset) = xvalues

        graphic_width = w - graphic_offset
        pie_height = h * pie_y_scale
        pie_width = pie_height

        xstart = pie_width + pie_slant
        xend = w - xend_offset
        xbarstart = xstart + bar_start_offset
        xbarend = xend - bar_end_offset

        bar = xbarend - xbarstart
        bar_step = bar / nsteps
        time_tags = ("x11", "x12", "x21", "x22")

        xtimes = dict([(prospect, [xbarstart + tm * bar_step
                                   for tm in stream])
                       for prospect, stream in self.times.items()])
        mtimes = [xbarstart + tm * bar_step for tm in
                  self.timeline.get("months").keys()]

        xypositions = {"pie_height": pie_height,
                       "graphic_width": graphic_width,
                       "xstart": xstart,
                       "xend": xend,
                       "xbarstart": xbarstart,
                       "xbarend": xbarend,
                       "xtimes": xtimes,
                       "mtimes": mtimes,
                       "bar_height": h / 2,
                       "window_top": (xstart_offset, ystart_offset),
                       "window_bottom": (xstart_offset, h - yend_offset)}

        self.__class__.xypositions.update(xypositions)
        return None

    def resize(self, event):
        self.set_xyvalues()
        xtags = ("pie_height", "graphic_width",
                 "xstart", "xend", "xtimes", "xstart_offset",
                 "bar_height", "window_top", "window_bottom",
                 "mtimes")
        xvalues = [self.__class__.xypositions.get(tag) for tag in xtags]
        (pie_height, graphic_width,
         xstart, xend, xtimes, xstart_offset, bar_height,
         window_top, window_bottom, mtimes) = xvalues

        window_coords = zip(self.pie_windows, (window_top, window_bottom))
        [self.coords(i, *w_coords)
         for i, w_coords in window_coords]

        [pie.config(width = graphic_width, height = pie_height)
         for pie in self.pies]
        timeline = self.timeline.get("timeline")
        mtimes = [m + xstart_offset for m in mtimes]
        self.resize_timeline(xstart_offset + xstart,
                             xend, xtimes, mtimes, bar_height)

