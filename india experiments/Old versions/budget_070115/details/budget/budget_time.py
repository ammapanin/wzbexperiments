# Code for time treatment of budget allocation problem
# Last updated: 28 January 2015

import Tkinter as tk
import tkFont
import random
import time

import os
from budget_methods import budgetSetup, budgetMethods




class TimeScreen(budgetMethods, budgetSetup):

    def __init__(self, master, dims, n_questions, q_index, sp_screen, texts, base):
        self.treatment = "time"
        self.setup_treatment(master, n_questions, dims, q_index, texts, base)

        self.make_additional_frames()
        self.sp_screen = sp_screen

        self.draw_budgetline()
        self.show_prices()

        self.initialise_time_configs(dims)
        self.env_img = self.get_budget_pic("envelope")

        self.time_bar = self.draw_time_bar(self.timebar_frame)

        self.time_line, self.time_envs \
        = self.draw_timeline(self.timeline_frame)



    def initialise_time_configs(self, dims):
        self.time_length = dims['width'] * float(2) / 3
        self.lab_offset = dims['width'] / 30
        self.slant_offset = self.lab_offset * 2
        offset = self.lab_offset + self.slant_offset

        months = (0, 3, 6)
        month_names = ["Tomorrow"] \
                      + ["{} mths".format(month) for month in months[1:]]

        nm = len(month_names) - 1
        tx = self.time_length / nm

        self.months = dict([(m[0], {"pos": offset + i * tx,
                                    "name": m[1]})
                            for i, m in enumerate(zip(months, month_names))])
        coin_size = int(round(tx / 20))
        return coin_size


    def make_additional_frames(self):
        self.timeline_frame = tk.Frame(self.choice_graphics_frame)
        self.timebar_frame = tk.Frame(self.choice_graphics_frame)

        self.timeline_frame.pack(fill = "x", 
                                 expand = True)

        self.timebar_frame.pack(fill = "both", 
                                expand = True)

        return None



    def draw_time_bar(self, master):

        barframe = tk.Frame(master)
        barframe.pack(side = "bottom",
                      fill = "both",
                      expand = True,
                      anchor = "w")

        monthfont = tkFont.Font(size = 20, weight = "bold")

        lx0 = self.lab_offset + self.slant_offset
        barheight = 90

        by = 25
        byt = by + self.lab_offset
        bx1 = lx0

        bar = tk.Canvas(master,
                        width = self.time_length + 50,
                        height = barheight)
        bar.pack(fill = 'both', expand = 'yes')

        bar.create_line(0, by,
                        lx0 + self.time_length + self.lab_offset + 50, by,
                        width = 30, arrow = 'last',
                        fill = 'dark grey',
                        arrowshape = (10, 12, 8))

        self.bar_months = dict([(month_idx,
                                 bar.create_text(month['pos'], byt,
                                                 text = month['name'],
                                                 font = monthfont,
                                                 tags = "monthlab",
                                                 fill = "grey"))
                                for month_idx, month in self.months.items()])

        return bar


    def draw_timeline(self, master):
        timeframe = tk.Frame(master)
        timeframe.pack(side = "top",
                       anchor = "w",
                       fill = "both",
                       expand = True)

        # Default configurations; note reversal for cols
        t1, t2 = times = (0, 0)
        time_cols = [self.payoff_dic[side]['time_col']
                     for side in ('x2', 'x1')]
        amt1, amt2 = (77, 77)
        amts = (amt1, amt2)

        #### Getting the drawing formats
        # lx - line; tx - line end; ax - amounts,

        lx = self.slant_offset
        lx0 = self.lab_offset + self.slant_offset

        tx0, tx1 = [self.months[t]["pos"] - self.lab_offset for t in times]

        ly = 50

        ax0, ax1 = [self.months[t]["pos"] for t in times]
        ay0, ay1 = ly, ly * 3

        amtfont = tkFont.Font(size = '16')
        probfont = tkFont.Font(size = '13')

        self.tx0, self.ly = tx0, ly

        ### Actual timeline
        # draw lines, envelopes, env_frames

        time_line = tk.Canvas(timeframe, height = 75)
        time_line.pack(fill = "both",
                       expand = True,
                       anchor = "center")

        time_line.create_line(0, ly,
                              lx0 + self.time_length + self.lab_offset + 50, ly,
                              width = 2,
                              fill = 'black',
                              dash = (4, 4),
                              arrow = "last")

        # Reverse envelopes because canvas creates windows in reverse order
        
        tlabs = [tk.Label(time_line,
                          image = self.env_img,
                          text = "{}{}".format("Rs ", amt),
                          font = amtfont,
                          compound = tk.CENTER,
                          bg = col)
                 for amt, col in zip(amts, (time_cols[1], time_cols[0]))]
        
        for lab in tlabs:
            lab.image = self.env_img 

        tl_frame_formats = [(ax0, ly, tlabs[0]), (ax1, ly, tlabs[1])]
        tenvs = [time_line.create_window(x, y,
                                         window = lab,
                                         tag = "timetext")
                 for x, y, lab in tl_frame_formats]

        return time_line, tlabs


    # def get_configs(self, config):
    #     sides = ("x1", "x2")

    #     c1, c2 = [self.payoff_dic[side][config]
    #               for side in sides]

    #     return c1, c2


    def update_times(self, times):

        tx0, ly = self.tx0, self.ly

        time_cols = [self.payoff_dic[side]['time_col']
                     for side in ('x1', 'x2')]
      
        linetags = ("t1", "t2")
        y_pos = (ly, ly)

        time_pos = [self.months[t]["pos"] for t in times]
        time_names = [self.months[t]["name"] for t in times]
        envs = self.time_line.find_withtag("timetext")

        [self.time_line.coords(env, tx_new, ty)
         for env, tx_new, ty in zip(envs, time_pos, y_pos)]

        [self.time_bar.itemconfig(mth, fill = "gray")
         for mth in self.bar_months.values()]

        months = [self.bar_months.get(t) for t in times]
        [self.time_bar.itemconfig(mth, fill = col)
         for mth, col in zip(months, time_cols)]

        return None


def full_program():
    print os.getcwd()
    root = tk.Tk()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.attributes("-fullscreen", True)
    dims = {'width':w, 'height':h}
    root.title("Time treatment")
    bob = portfolioChoice_time(root, 20, dims)
    root.mainloop()
    return bob

if __name__ == "__main__":
    brabra = full_program()
    print "Time running...ASP"


