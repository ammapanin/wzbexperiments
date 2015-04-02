# Methods for the budget class
# Last updated: 28 January 2015

import Tkinter as tk
import tkFont
import os
import random
import decimal
import tkMessageBox
from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv
import time


class budgetSetup():
    def __init__(self):
        pass

    def setup_treatment(self, master, n_questions, dims, q_index, texts, base):
        self.root = dims["root"]
        self.texts = texts
        self.main_master = master
        self.mainframe = tk.Frame(master)
        self.make_frames(self.mainframe)

        self.qtext = q_index["index"]
        self.qinfo_lab = q_index["info"]
        self.indextext = q_index["text"]
        self.qindex = False
        self.n_base = 2
        self.dims = dims
        self.BASE = base

        pfilespath = os.path.dirname(base)
        self.dataPATH = os.path.join(os.path.dirname(pfilespath),
                                     "data",
                                     "budget")

        self.n_questions = n_questions
        self.arrow = u"\u2192".encode("utf-8")
        self.other_treatment = ""
        self.treatment_order = ""
        self.ind_data = dict()

        self.j = tk.IntVar()
        self.j.set(0)

        self.start_time = time.time()
        self.certaincol = "dark green"

        self.time_treatments = [(0, 3), (3, 6)]
        random.shuffle(self.time_treatments)
        self.times_t2, self.times_t1 = self.time_treatments


        self.payoff_dic = {'x1': {'price': 1,
                                  'coln': 0,
                                  'col': "royal blue",
                                  'time_col': "dark green",
                                  'sticky': "left",
                                  'time': 0,
                                  'relief': "flat"},
                           'x2': {'price': 8,
                                  'coln': 11,
                                  'col': "midnight blue",
                                  'time_col': "light sea green",
                                  'sticky': "right",
                                  'time': 0,
                                  'relief': "flat"}}

        self.prices = plist = self.get_prices()

        if self.treatment == "time":
            p1 = tuple(plist)
            random.shuffle(plist)
            p2 = tuple(plist)
            self.prices = list(p1 + p2)

        self.n_questions = len(self.prices)

        self.p0 = [(0, (0.5, 1)), (0, (0.5, 2.5))]
        self.p1 = list(enumerate(self.prices,1))

        self.prices = iter(self.p0 + self.p1)


        bt_font = tkFont.Font(size = 15)
        self.next_bt = tk.Button(self.bottom_frame,
                                 text = "OK",
                                 command = self.go_next,
                                 font = bt_font)
        self.next_bt.pack(side = "right", anchor = "center")

        self.q_dic = dict([(q, {"p1":"", "p2":"",
                                "n1":"", "n2":"",
                                "t1":"", "t2":"",
                                "a1":"", "a2": ""})
                           for q in range(1, self.n_questions + 1)])


    def data_todic(self):
        q = self.qindex

        n2 = self.scale.get()
        n1 = 100 - n2

        p1, p2 = self.qprices
        t1, t2 = self.qtimes

        a1, a2 = p1 * n1, p2 * n2

        cols = ("pL", "pR",
                "nL", "nR",
                "tL", "tR",
                "aL", "aR",
                "timing", "start_n2")
        data = (p1, p2,
                n1, n2,
                t1, t2,
                a1, a2,
                self.timing, self.start_n2)

        q_dat = dict([(i, j) for i, j in zip(cols, data)])
        q_dat.update(self.ind_data)
        self.q_dic.update({q:q_dat})

        return None

    def write_data(self):
        data_tuples = self.q_dic.items()

        identifiers = ("taluk", "village", "wzbid",
                       "interviewed_check", "interviewed_name")
        id_tags = [self.treatment] + [self.ind_data.get(idx)
                                      for idx in identifiers]
        fname = "{}_{}_{}_{}.csv".format(*id_tags)
        fpath = os.path.join(self.dataPATH, fname)


        cols = ["wzbid", "innterviewed_check", "interviewed_name",
                "pL", "pR", "nL", "nR",
                "tL", "tR", "aL", "aR", "timing", "start_n2"]
        colnames = ["qid"] + cols

        data = [[q] + [dic.get(tag) for tag in cols]
                for q, dic in data_tuples]

        with open(fpath, "w") as dfile:

            dwrite = csv.writer(dfile)

            [dwrite.writerow(row)
             for row in [colnames] + data]

        print "Data written to ", fname
        return None


    def go_next(self):
        self.end_time = time.time()

        self.timing = round(self.end_time - self.start_time)
        old_qindex = self.qindex

        if self.qindex:
            self.data_todic()


        try:
            question = self.prices.next()
            self.qindex = question[0]
            self.qprices = question[1]

            if old_qindex == 0 and self.qindex > 0:
                tkMessageBox.showinfo("Real money at stake!",
                                      ("Those were the practice questions."
                                       "\nYou will now start a section of the experiment"
                                       " where one of your decisions will determine"
                                       " your real final payout. Please pay close attention "
                                       "to the choices you make."))

            if self.qindex == 0:
                self.qtext.config(text = "Practice")
                self.qinfo_lab.pack(side = "bottom")
            elif self.qindex > 0:
                self.qinfo_lab.pack_forget()
                i = self.j.get()
                i += 1
                self.j.set(i)

                self.qtext.config(text = \
                                  self.indextext.format(self.j.get()))

            if self.qindex > self.n_questions/2:
                self.qtimes = (self.times_t2)
            else:
                self.qtimes = self.times_t1

            self.start_n2 = start = random.choice(range(0, 100))
            self.scale.set(start)
            self.update_times(self.qtimes)
            self.update_prices(self.qprices)
            self.update_allocation("event")
            self.start_time = time.time()


        except StopIteration:
            self.write_data()
            self.mainframe.pack_forget()

            if self.treatment_order == 1:
                self.switch_treatments()
            else:
                self.next_bt.pack_forget()
                self.other_treatment.next_bt.pack_forget()
                self.sp_screen.pack(expand = True, fill = "both")
                self.qtext.config(text = "Payment")
                print "Fertig"

        return None

    def switch_treatments(self):
        self.other_treatment.j.set(self.j.get())
        self.treatment = self.other_treatment.treatment

        tm = self.other_treatment.treatment

        t1 = self.other_treatment.times_t1
        t2 = self.other_treatment.times_t2

        if tm == "time":
            treattext = self.texts[tm].format(tm.upper(),
                                              t1[0], t1[1], t2[0], t2[1])
        else:
            treattext = self.texts[tm].format(tm.upper())
        self.qtext.config(text = treattext)

        bt_font = tkFont.Font(size = 20)
        self.continue_bt = tk.Button(self.main_master,
                                     text = "OK",
                                     command = self.restart_treatments,
                                     font = bt_font)
        self.continue_bt.pack(side = "right", anchor = "center")

        return None

    def restart_treatments(self):
        self.continue_bt.pack_forget()
        self.other_treatment.mainframe.pack(expand = True,
                                            anchor = "center",
                                            side = "bottom",
                                            fill = "y")
        self.qtext.config(text = self.indextext.format(self.j.get()))
        self.other_treatment.go_next()
        self.next_bt.config(command = self.other_treatment.go_next)

    def get_prices(self):
        prices = list()
        while len(prices) < self.n_questions:
            while True:
                ev = random.choice(range(50, 450, 10))
                (p1, p2) = self.draw_random_prices(ev)
                if (p1, p2) not in prices:
                    break
            prices.append((p1, p2))

        return prices

    def draw_random_prices(self, ev):
        min_p = 50
        max_p = 1000

        while True:
            prices = range(min_p, max_p, 50)
            p1_0 = prices.pop(prices.index(random.choice(prices)))
            p1_1 = decimal.Decimal(p1_0)
            p2_0 = (decimal.Decimal(2 * ev * 100) / 50) - p1_1

            p1 = p1_1 / 100
            p2 = self.rounding(p2_0) / 100

            if p1 != p2 and p2 > float(min_p)/100 and p2 < 10:
                break

        if self.treatment == "time":
            final_p1 = min(p1, p2)
            final_p2 = max(p1, p2)

        else:
            prices = [p1, p2]
            random.shuffle(prices)
            final_p1, final_p2 = prices
        return final_p1, final_p2

    def rounding(self, x, base = 50):
        return int(base * round(float(x)/base))


    def fix_amount(self, event):
        self.scale.set(self.nr_fixed)
        return None

    def show_enumerator_notes(self):
        label = tk.Label(self.mainframe, text = "Please add your comments")
        self.choiceframe.pack_forget()
        self.enum_notes = tk.Text(self.mainframe)
        label.pack()
        self.enum_notes.pack()
        self.pay_bt.config(command = self.get_enumerator_notes)
        return None

    def get_enumerator_notes(self):
        note = self.enum_notes.get(tk.SEL_FIRST, tk.SEL_LAST)
        with open ("enumerator_notes.csv", "a") as outfile:
            outfile.writeline(note)


class budgetMethods():

    def __init__(self):
        pass

    def set_base(self):
        base = os.path.dirname(__file__)
        return base

    def make_frames(self, master):
        self.top_frame = tk.Frame(master)
        self.bottom_frame = tk.Frame(master)

        self.prices_mainframe = tk.Frame(self.top_frame)
        self.budget_frame = tk.Frame(self.top_frame)
        self.choice_graphics_frame = tk.Frame(master = self.bottom_frame)

        self.bottom_frame.pack(expand = True,
                               fill = "x",
                               pady = 2,
                               anchor = "s",
                               side = "bottom")

        self.prices_mainframe.pack(fill = "both",
                                   expand = True,
                                   pady = 3)

        self.budget_frame.pack(fill = "both",
                               expand = True,
                               pady = 3)

        if self.treatment == "time":
            y_padding = 50,
            fill_direction = "x"
        elif self.treatment == "risk":
            y_padding = 20,
            fill_direction = "y"

        self.top_frame.pack(expand = True,
                            fill = "both",
                            pady = y_padding,
                            anchor = "n",
                            side = "top")

        self.choice_graphics_frame.pack(side = "left",
                                        expand = True,
                                        fill = fill_direction,
                                        pady = 20)

        self.prices_canvas = tk.Canvas(self.prices_mainframe,
                                       height = 120)

        self.prices_canvas.pack(fill = "x",
                                expand = True)


    def show_prices(self):
        self.price_objects = [self.draw_price(self.prices_mainframe, i)
                              for i in ('x1','x2')]
        price_positions = [(0, 0), (950, 0)]

        [self.prices_canvas.create_window(pos[0], pos[1],
                                          window = p,
                                          anchor = "nw")
         for p, pos in zip(self.price_objects,
                           price_positions)]
        return None

    def draw_price(self, master, side):
        pt = 200
        pc = pt / 2
        pl_x, pl_y =  pc + 5, 10 + pc / 2

        col = self.payoff_dic[side]["col"]
        ptext = self.payoff_dic[side]["price"]

        pfont = tkFont.Font(size = 25,
                            weight = "bold")

        price = tk.Canvas(master,
                          height = pt,
                          width = 300)

        price.create_text(pl_x + 50, pl_y,
                          text = "{} Rs {}".format(self.arrow, ptext),
                          activefill = "green",
                          font = pfont,
                          tag = "pricelab")

        price.create_oval(20, 20, pc, pc, fill = col)

        price.pack(side = "top")

        return price


    def draw_balls(self, master):
        balls = tk.Canvas(master, height = 50)

        x_coords = zip(range(5, 1205, 24),
                       range(27, 1227, 24))

        [balls.create_oval(x[0], 22, x[1], 44, fill = "blue", tag = tag)
         for tag, x in enumerate(x_coords, 1)]

        balls.pack(fill = "x", expand = True, anchor = "w")

        return balls

    def scale_balls(self):
        scaledfont = tkFont.Font(size = 15)
        [c.scale("all", 0, 0, 0.5, 0.5)
         for c in self.price_objects]
        [c.itemconfig("pricelab", font = scaledfont)
         for c in self.price_objects]

        self.prices_canvas.config(height = 70)
        return None

    def draw_budgetline(self):
        self.slider_frame = tk.Frame(self.budget_frame)
        self.slider_frame.pack(fill = "x",
                               expand = True)

        self.balls = self.draw_balls(self.slider_frame)

        self.scale = tk.Scale(self.slider_frame,
                              from_ = 0,
                              to_ = 100,
                              resolution = 2,
                              length = 1205,
                              command = self.update_allocation,
                              orient = "horizontal",
                              showvalue = False,
                              takefocus = True)
        self.scale.pack(side = "bottom",
                        anchor = "w" )
        return None


    def colour_balls(self, nr):
        col1, col2 = [self.payoff_dic[side]['col']
                      for side in ('x1', 'x2')]

        [self.balls.itemconfig(n, fill = col2)
         for n in range(1, nr + 1)]

        [self.balls.itemconfig(n, fill = col1)
         for n in range(nr + 1, 51)]

        return None


    def update_allocation(self, event):
        p1, p2 = self.qprices
        nr = self.scale.get()

        amts = ((100 - nr) * p1, nr * p2)
        amts = ["Rs {}".format(int(amt)) for amt in amts]

        self.colour_balls(nr / self.n_base)

        if self.treatment == "time":
            [env.config(text = amt)
             for env, amt in zip(self.time_envs, amts)]

        elif self.treatment == "risk":
            self.lottery.update_envelopes(amts, self.prob)

    def get_configs(self, config):
        sides = ("x1", "x2")
        c1, c2 = [self.payoff_dic[side][config]
                  for side in sides]
        return c1, c2


    def update_prices(self, prices):
        ptexts = ["{} Rs {}".format(self.arrow, int(self.n_base * price))
                  for price in prices]

        p = [pcanvas.find_withtag("pricelab")
             for pcanvas in self.price_objects]

        self.price_objects[0].itemconfig(p[0], text = ptexts[0])
        self.price_objects[1].itemconfig(p[1], text = ptexts[1])

        return None


    def get_budget_pic(self, image):
        pic_path = os.path.join(self.BASE,
                                "pictures",
                                image + ".gif")
        env_img = tk.PhotoImage(file = pic_path)
        return env_img



