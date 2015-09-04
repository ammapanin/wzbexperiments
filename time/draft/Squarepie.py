import Tkinter as tk
import tkFont
import os
import csv
import itertools

class SquarePie(tk.Canvas):
    def __init__(self, master, pie_configs):
        tk.Canvas.__init__(self, master)
        self.config(bg = "ivory2", 
                    highlightcolor = "green4",
                    highlightthickness = 5)
        self.pack(fill = "both", expand = True, anchor = "w")

        self.pie_colour = pie_configs.get("colour")
        self.prospect_tag = pie_configs.get("prospect_id")
        self.prob = pie_configs.get("prob")
        self.amounts = ((0, 100), (20, 500))
        self.choice_pie = pie_configs.get("choice_pie")

        self.pie = self.draw_pie()
        self.prospect = self.draw_prospect()
        self.amount_ids = self.draw_amounts()
        
        self.ypositions = {"h0": 10}
        self.bind("<Configure>", self.resize)

    def update_choice(self, choice):
        self.itemconfig(self.choice_id, text = choice)

    def update_stimuli(self, prob, amounts):
        self.update_probability(prob)     
        self.resize("event")
        self.update_amounts(amounts)
        return None

    def draw_pie(self):
        pfont = tkFont.Font(size = 12)
        pie = self.create_oval(4, 4, 60, 60)
        arc = self.create_arc(4, 4, 60, 60, 
                              extent = 270, 
                              fill = self.pie_colour)
        prob_text = self.create_text(4, 4, 
                                     text = "", 
                                     fill = self.pie_colour,
                                     font = pfont)
        return {"pie": pie, "arc": arc, "prob": prob_text} 

    def draw_prospect(self):
        lines = [self.create_line(0, 0, 1, 1, dash = (2, 2)) 
                 for i in range(0, 8)]
        self.risky_ids = lines[2:]
        return lines

    def draw_amounts(self):
        amtfont = tkFont.Font(size = 25)
        choicefont = tkFont.Font(size = 28)
        amounts = [self.create_text(0, 0, 
                                    text = amt, font = amtfont)
                   for stream in self.amounts
                   for amt in stream]
        if self.choice_pie == True:
            self.itemconfig(amounts[0], 
                            font = choicefont, 
                            fill  = "dark green",
                            tags = ("choice",))
            [self.itemconfig(s, font = amtfont) for s in amounts[1:]]
        self.choice_id  = amounts[0]
        self.risky_ids.extend(amounts[2:])
        return amounts
    
    def resize(self, event):
        h = self.winfo_height()
        h0 = self.ypositions["h0"]

        mid = h / 2
        pie_radius = mid - h0
        xpivot = h0 + 2 * pie_radius
    
        yline1 = (h + 6 * h0) / 8
        yline2 = (7 * h - 6 * h0) / 8
        ylines = (yline1, yline2)
    
        self.ypositions.update({"mid": mid, "ylines": ylines})
        xtags = ("xstart", "xend", "xtimes")
        xvalues = [PieScreen.xypositions.get(tag) for tag in xtags] 
        (xstart, xend, xtimes) = xvalues
    
        self.resize_pie(h0, h)
        xtimes_p = xtimes.get(self.prospect_tag)
        self.update_prospect(xpivot, xstart, xend, xtimes_p,
                             mid, yline1, yline2)

    def update_probability(self, prob):
        self.prob = prob
        pie, arc, ptext = [self.pie.get(tag) for tag in ("pie", "arc", "prob")]
        self.itemconfigure(arc, extent = 360 * prob - 0.000000001)
        self.itemconfigure(ptext, text = "{}%".format(int(prob * 100)))
        if prob == 1:
            self.resize("event")

    def resize_pie(self, h0, h):
        pie, arc, ptext = [self.pie.get(tag) for tag in ("pie", "arc", "prob")]
        [self.coords(i, h0, h0, h - h0, h - h0) for i in (pie, arc)]
        self.coords(ptext, h - h0 * 2, h0 * 3)

    def update_certainty(self, xpivot, xend, xtimes, y1):
        xt11, xt12, xt21, xt22 = xtimes
        l1, l2, l3, l4, l5, l6, l7, l8 = self.prospect
        a1, a2, a3, a4 = self.amount_ids

        self.coords(l1, xpivot, y1, xt11, y1)
        self.coords(l2, xt11, y1, xend, y1)
        [self.itemconfig(i, state = "hidden")
         for i in self.risky_ids]
        
    def update_prospect(self, xpivot, xstart, xend, xtimes, y0, y1, y2):
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
        resize = resize_dic.get(self.prob == 1)

        resize["line_func"](*resize["line_args"])
        resize["amt_func"](*resize["amt_args"])
        return None
    
    def resize_certain_lines(self, xpos, ypos, xtimes):
        xpivot, xend = xpos
        y1 = ypos
        xt11, xt12, xt21, xt22 = xtimes
        l1, l2, l3, l4, l5, l6, l7, l8 = self.prospect
                
        self.coords(l1, xpivot, y1, xt11, y1)
        self.coords(l2, xt11, y1, xend, y1)
        [self.itemconfig(i, state = "hidden") for i in self.risky_ids]
        return None

    def resize_risky_lines(self, xpos, ypos, xtimes):
        xpivot, xstart, xend = xpos
        y0, y1, y2 = ypos
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

        [self.itemconfig(i, state = "normal") for i in self.risky_ids]
        return None

    def update_amounts(self, amounts):
        state_dic = {True: "hidden", False: "normal"}
        states = [state_dic.get(a == "na") for a in amounts]
        [self.itemconfig(i, text = amt, state = s) 
         for i, amt, s in zip(self.amount_ids, amounts, states)]

    def resize_certain_amounts(self, xtimes, ylines):
        c1, x1, c2, x2 = self.amount_ids
        xt11, xt12, xt21, xt22 = xtimes
        yline = ylines
        
        self.coords(c1, xt11, yline)
        self.coords(x1, xt12, yline)
        
    def resize_risky_amounts(self, xtimes, ylines):
        c1, x1, c2, x2 = self.amount_ids
        xt11, xt12, xt21, xt22 = xtimes
        yline1, yline2 = ylines
        
        self.coords(c1, xt11, yline1)
        self.coords(x1, xt12, yline1)
        self.coords(c2, xt21, yline2)
        self.coords(x2, xt22, yline2)
        return None

class PieScreen(tk.Canvas):
    xypositions = {"nsteps": 12,
                   "xend_offset": 60,
                   "bar_start_offset": 55, 
                   "bar_end_offset": 60, 
                   "pie_y_scale": float(7) / 20,
                   "pie_slant": 30,
                   "graphic_offset": 50,
                   "ystart_offset": 20,
                   "yend_offset": 20,
                   "xstart_offset": 10}

    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        self.config(highlightthickness = 0)
        self.pack(fill = "both", expand = True)

        self.pies, self.pie_windows = self.add_pies()
        self.timeline = self.draw_timeline()

        self.bind("<Configure>", self.resize)
        self.times = {0: (3, 6, 3, 9), 1: (3, 6, 3, 12)}
        self.selected = tk.IntVar()
        self.set_bindings()

    def set_bindings(self):
        [self.bind_all(key, self.select_pie)
         for key in ("<Up>", "<Down>")]

    def update_question(self, stimulus):
        tags = ("p1", "p2", "t1", "t2")
        p1, p2, t1, t2 = [float(stimulus.get(t))
                          for t in tags]
        amt_tags = (("c11", "x12", "c11","y12"), 
                    ("c21", "x22", "c22", "y22"))
        amounts = [[stimulus.get(at)
                    for at in amt_tag] 
                   for amt_tag in amt_tags]
        ttuple = (t1, t2, t1, t2)
        self.times = {0: ttuple, 1: ttuple}
        self.set_xyvalues()

        pie_details = zip(self.pies, (p1, p2), amounts)
        [pie.update_stimuli(prob, amts) for pie, prob, amts in pie_details]
        self.update_timeline()

    def select_pie(self, event):
        svar = self.selected.get()
        svar_new = abs(svar - 1)
        self.selected.set(svar_new)
        self.pies[svar_new].focus_set()
        return None

    def add_pies(self):
        pie_configs = [{"colour": "red",
                        "prob": 0.5,
                        "prospect_id" : 0,
                        "choice_pie": True},
                       {"colour": "blue",
                        "prob": 0.8,
                        "prospect_id" : 1}]
        pies = [SquarePie(self, pc) 
                for pc in pie_configs]
        windows = [self.create_window(0, 0, anchor = a, window = p)
                   for a, p in zip(("nw", "sw"), pies)]
        return pies, windows

    def draw_timeline(self):
        month_fonts = tkFont.Font(size = 15)
        timeline = self.create_line(10, 400, 560, 400,
                                    width = 60,
                                    arrow = "last",
                                    arrowshape = [15, 40, 20],
                                    fill = "gray")
        m0 = "Tomorrow"
        month_nrs = range(0, 15, 3)
        month_names = [m0] + [str(m) + " months" for m in month_nrs[1:]]
        months = [self.create_text(0, 0, 
                                   text = txt, font = month_fonts) 
                  for txt in month_names]
        timeline_obj =  {"timeline": timeline, 
                         "months": dict(zip(month_nrs, months))}
        return timeline_obj

    def update_timeline(self):
        normal_month = tkFont.Font(size = 15)
        bold_month = tkFont.Font(size = 15, weight = "bold")
        months = [t for stream in self.times.values() for t in stream]
        month_ids = self.timeline.get("months")
        [self.itemconfig(i, font = normal_month) for i in month_ids.values()]
        for m in months:
            self.itemconfig(month_ids[m], font = bold_month)

    def resize_timeline(self, x0, x1, xtimes, mtimes, y):
        (x11, x12, x13, x14), (x21, x22, x23, x24) =  xtimes.values()
        timeline, ovals = [self.timeline.get(i) 
                           for i in ("timeline", "ovals")]
        self.coords(timeline, x0, y, x1, y)
        months = zip(self.timeline.get("months").values(), mtimes)
        [self.coords(m, mx, y) for m, mx in months]

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

class ChoiceScreen(tk.Frame):
    def __init__(self, master, stimuli):
        tk.Frame.__init__(self, master)
        self.pack(side = "top", fill = "both", expand = True)
        self.pie_frame, btframes, self.title, self.edit = self.make_frames()
        self.bt_frame, confirm_frame = btframes
        self.pie = PieScreen(self.pie_frame)
        self.buttons = dict()
        self.choice = 0
        self.bind_all("<Return>", self.make_selection)
        self.stimuli, self.nquestions = stimuli
        self.confirm_bt = self.confirm_button(confirm_frame)
        self.start_question()
        
    def make_frames(self):
        title_frame, body = [tk.Frame(self) for i in range(0, 2)]
        f1, f2 = [tk.Frame(body) for i in range(0, 2)]
        title_frame.pack(side = "top", fill = "x")
        body.pack(side = "top", fill = "both", expand = True)
        f1.pack(side = "left",
                fill = "both", 
                expand = True) 
        f2.pack(side = "left",
                fill = "both")
        f2.config(highlightthickness = 3)

        b1, b2 = [tk.Frame(f2) for i in (0, 1)]
        b1.pack(side = "top", fill = "both", expand = True)
        b2.pack(side = "top", fill = "y")
        
        titlefont = tkFont.Font(size = 25, weight = "bold")
        editfont = tkFont.Font(size = 28, weight = "bold")
        title, edit_text = [tk.Label(title_frame,
                                     text = "") for i in (0, 1)]
        edit_text.config(text = "Please confirm your choices", 
                         fg = "dark green", font = editfont)
        title.config(font = titlefont)
        title.pack(side = "left")
        return f1, (b1, b2), title, edit_text

    def update_question(self, stimuli):
        qidx, stimuli = stimuli 
        choice_range = range(0, int(stimuli.get("x22")) + 20, 20)
        self.title.config(text = "Question {} of {}".format(qidx, 
                                                            self.nquestions))
        self.edit.pack_forget()
        self.pie.focus_set()
        self.choice_range = iter(choice_range)
        #self.choice = self.choice_range.next()
        bts = self.new_buttons(choice_range)
        self.buttons[qidx] = bts
        self.current_bts = bts
        self.pie.update_question(stimuli)
        self.steps = choice_range
        mmin, mmax = (min(choice_range), max(choice_range))
        self.checked = [mmin, mmax]
        [self.current_bts.get(amt).get("var").set(i)
         for amt, i in zip((mmin, mmax), (1, 0))]
        self.c0 = 40
        self.pie.pies[0].update_choice(self.c0)
        

    def confirm_button(self, frame):
        bt = tk.Button(frame, text = "Confirm", 
                       command = self.start_question)
        return bt
    
    def new_buttons(self, stimuli):
        btframe = self.bt_frame.children.get("buttons")
        if btframe != None:
            btframe.destroy()
        bts = self.draw_buttons(stimuli)
        return bts

    def draw_buttons(self, choices):
        btframe = tk.Frame(self.bt_frame, name = "buttons")
        labs = [tk.Label(btframe, text = txt) for txt in ("Rot", "Blau")] 
        lab_grids = zip(labs, ((0, 1), (0, 2)))
        [lab.grid(row = i, column = j) for lab, (i, j) in lab_grids]
        btframe.pack(side = "left", fill = "both", expand = True)
        
        n = len(choices)
        btvars = [tk.IntVar(self) for i in choices]
        [b.set(600) for b in btvars]
        btinfo = zip(choices, btvars)
        
        choice_labs = [tk.Label(btframe, text = c) for c in choices]
        [c.grid(row = i, column = 0, sticky = "w")
         for i, c in enumerate(choice_labs, 1)]

        def grid_xy(n):
            i = 0
            x = 1
            while i < n:
                if i % 2 == 0:
                    yield {"row":x, "column": 1}
                else:
                    yield {"row":x, "column": 2}
                    x += 1
                i += 1

        grids = grid_xy(n * 2)
        bts = {n : {"bts": [tk.Radiobutton(btframe, 
                                           value = i, variable = v) 
                            for i in (0, 1)],
                    "var": v}
               for n, v in btinfo}
        sorted_bts = [bts[n].get("bts") for n in sorted(bts)]
        bts_objects = itertools.chain(*sorted_bts)
        bts_grid = itertools.izip(bts_objects, grids)
        [b.grid(**xy) for b, xy in bts_grid]                                  
        return bts

    def update_choice(self, choice):
        self.c0 = choice
        self.pie.pies[0].update_choice(choice)

    def make_selection(self, event):
        choice = self.pie.selected.get()
        cnext = self.pingpong(choice)
        if cnext != False:
            self.update_choice(cnext)
        else:
            self.end_question()
        return None
        
    def end_question(self):
        self.edit.pack(side = "right")
        self.bt_frame.focus_set()
        self.confirm_bt.pack()
        
    def start_question(self):
        self.confirm_bt.pack_forget()
        try:
            self.update_question(self.stimuli.next())
        except StopIteration:
            print "Experiment over"

    def pingpong(self, choice):
        cdic = {1: (min(self.checked), self.c0),
                0: (self.c0, max(self.checked))} 
        min_c, max_c = cdic.get(choice)
        go_next = self.fill(min_c, max_c, choice)
        
        if go_next == True:
            cnext = self.get_next()
            self.c0 = cnext
            print "cnext", cnext
        elif go_next == False:
            cnext = False
        return cnext

    def fill(self, mmin, mmax, choice):
        print mmin, mmax
        fill_check = range(mmin, mmax + 20, 20)
        bts = [self.current_bts.get(c) for c in fill_check]
        [bt.get("var").set(choice) for bt in bts]
        print fill_check
        self.checked.extend(fill_check)
        checked_set = set(self.checked)
        self.checked = list(checked_set)
        return len(checked_set) != len(self.steps)

    def get_next(self):
        cmin = max([i for i, c in enumerate(self.steps) 
                    if (c in self.checked and c < self.c0)])
        cmax = min([i for i, c in enumerate(self.steps) 
                    if (c in self.checked and c > self.c0)])
        print "idx", cmin, cmax

        irange = range(cmin, cmax)        
        idiff = float(cmax - cmin) / 2

        if len(irange) == 3:
            iplus = int(idiff)
        else:
            iplus = int(round(idiff))
        idx = cmin + iplus
        print cmin, iplus
        amt = self.steps[idx]
        
        return amt

    def end_pingpong(self):
        print "End"




spath = '/Users/aserwaahWZB/Projects/GUI Code/time/draft'
csvpath = os.path.join(os.getcwd(), "stimuli_test.csv")

def get_stimuli(path):
    stimulipath = path
    with open(stimulipath, "rb") as sfile:
        scsv = csv.reader(sfile)
        fnames = scsv.next()
        ldic = [dict(zip(fnames, line)) for line in scsv]
        lines = enumerate(ldic)
    return lines, len(ldic)

ss = get_stimuli(csvpath)

def test_class():
    root = tk.Tk()
    abrogate = ChoiceScreen(root, ss)
    return abrogate

y = test_class()

y.pie.pies[0].itemconfig(y.pie.pies[0].amount_ids[0], state = "normal")

"""
bilk - cheat
abrogate - repeal
abjure - solemnly renounce
rarefy - make less dense
repine - feel discontent
"""

