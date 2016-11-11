#!/usr/bin/python
# -*- coding: utf-8 -*-

### Code to produce the screen used in risk and time experiments
### Experiments run in Berlin (March 2016) and Bangalore (Nov 2016)
###
### Last updated: 3.11.16

import Tkinter as tk
import tkFont
import tkMessageBox
import os
import csv
import itertools
import random
import string
import datetime
from Squarepie import SquarePie, PieScreen
from Tracker import GradualTracker as Tracker
from payment import Payment

class ChoiceScreen(tk.Frame):
    def __init__(self, master, stimuli, mode, end_func, idvars,
                 prob_type, commodity):
        tk.Frame.__init__(self, master)
        self.order = 0
        self.main = master
        self.mode = mode
        self.commodity = commodity
        if end_func != False:
            self.end_experiment = end_func
        else:
            self.end_experiment = self.end_experiment_default

        self.c0 = tk.IntVar(self)
        self.c_1 = tk.IntVar(self)

        self.idvars = idvars
        self.stimuli_step = 10
        self.prob_type = prob_type
        self.stimuli_init = stimuli
        self.commodity = commodity


    def start(self):
        self.pack(side = "top", fill = "both", expand = True)
        self.pie_frame, btframes, self.title, self.edit = self.make_frames()
        self.bt_frame, confirm_frame = btframes
        self.pie = PieScreen(self.pie_frame, self.prob_type, self.commodity)
        self.buttons = dict()
        self.choice_data = dict()
        self.choice = 0
       # self.bind_all("<Return>", self.make_selection)
        self.stimuli, self.nquestions = self.stimuli_init
        self.stimuli_dic = dict()
        self.confirm_bts = self.confirm_button(confirm_frame)
        self.start_question()
        selection_events = ("<Double-Button-1>", "<Return>")
        [self.bind_all(key, self.make_selection) for key in selection_events]

        self.choice_record = {0:0, 1:100}

    def make_frames(self):
        """Create all the major frames for the display

        body frame contains 2-horizontal: pies and choicelists
        choicelist frame contains 2-vetical: buttons and confirm
        """
        pay, title_frame, body = [tk.Frame(self) for i in range(0, 3)]
        self.payment_frame = pay
        f1, f2 = [tk.Frame(body) for i in range(0, 2)]
        body.pack(side = "bottom", fill = "both", expand = True)
        title_frame.pack(side = "bottom", fill = "x")
        # Change here to change frame positioning of tracker
        f1.pack(side = "top",
                fill = "both",
                expand = True)
        f2.pack(side = "bottom",
                fill = "both")
        f2.config(highlightthickness = 3)

        b1, b2 = [tk.Frame(f2) for i in (0, 1)]
        b1.pack(side = "left", fill = "both", expand = True)
        b2.pack(side = "right", fill = "y")

        titlefont = tkFont.Font(size = 25, weight = "bold")
        title = tk.Label(title_frame, text = "")
        title.config(font = titlefont)
        title.pack(side = "left")

        edit_frame = tk.Frame(title_frame)
        self.make_edit_text(edit_frame)
        return f1, (b1, b2), title, edit_frame

    def make_edit_text(self, frame):
        editfont = tkFont.Font(size = 28, weight = "bold")
        edit_text = tk.Label(frame, text = "Please confirm your choices",
                             fg = "dark green", font = editfont)
        edit_canvas = tk.Canvas(frame, height = 40)
        hline = edit_canvas.create_line(0, 10, 60, 10)
        arrow = edit_canvas.create_line(60, 10, 60, 30, arrow = "last")

        def resize(event):
            cwidth = edit_canvas.winfo_reqwidth()
            edit_canvas.coords(hline, 0, 20, cwidth - 10, 20)
            edit_canvas.coords(arrow, cwidth - 10, 20, cwidth - 10, 40)
            return None

        edit_canvas.bind("<Configure>", resize)
        edit_text.pack(side = "left")
        edit_canvas.pack(side = "left", anchor = "s")
        return None

    def confirm_button(self, frame):
        bt = tk.Button(frame, text = "Confirm",
                       command = self.confirm_click)
        bt_change = tk.Button(frame, text = "Keep original")
        return bt, bt_change

    def make_scale(self, master, n_bts, bcol, choices):
        self.scale = scale = tk.Scale(master,
                                      from_ = min(choices),
                                      to = max(choices),
                                      resolution = self.stimuli_step,
                                      showvalue = False,
                                      state = "disabled")
        return scale

    def control_scale(self, event):
        val = self.mmin + self.mmax - self.tracker.tvar.get()
        c0, c1 = self.choice_record.values()
        if val >= c0:
            choice = 0
        elif val <= c1:
            choice = 1
        self.pie.selected.set(choice)
        if self.pie.elicit == "prob":
            self.pie.pies[0].update_probability(val)
        elif self.pie.elicit == "amt":
            self.pie.pies[0].update_choice(val)
        self.confirm_val = val
        self.confirm_val_max = self.confirm_val - self.stimuli_step

    def confirm_click(self, event = "event"):
        self.save_question()
        self.start_question()

    def draw_buttons(self, choices, qidx):
        # Currently just do not grid while I figure out the other tracker
        """Creates the buttons of a given question
        """

        btframe = tk.Frame(self.bt_frame, name = "buttons" + str(qidx))
        labs = [tk.Label(btframe, text = txt) for txt in ("Red", "Blue")]
        lab_grids = zip(labs, ((0, 1), (0, 3)))
        #[lab.grid(row = i, column = j) for lab, (i, j) in lab_grids]
        btframe.pack(side = "left", fill = "both", expand = True)
        tracker_configs = {"elicit": self.pie.elicit,
                           "minmax": (self.mmax, self.mmin),
                           "stimuli_step": self.stimuli_step}
        self.tracker = Tracker(btframe, tracker_configs)
        self.confirm_bts[1].config(command = self.tracker.spring_back)
        n = len(choices)
        btvars = [tk.IntVar(self) for i in choices]
        [b.set(600) for b in btvars]
        btinfo = zip(choices, btvars)

        choice_labs = [tk.Label(btframe, text = c) for c in choices]
        #[c.grid(row = i, column = 0, sticky = "w")
        # for i, c in enumerate(choice_labs, 1)]

        bts = {n : {"bts": [tk.Radiobutton(btframe,
                                           value = i, variable = v)
                            for i in (0, 1)],
                    "var": v}
               for n, v in btinfo}

        bt_funcs = [self.bt_autofill(bts, amt, var) for amt, var in btinfo]
        [v.trace("w", bfunc) for v, bfunc in zip(btvars, bt_funcs)]

        def grid_xy(n):
            i = 0
            x = 1
            while i < n:
                if i % 2 == 0:
                    yield {"row":x, "column": 1}
                else:
                    yield {"row":x, "column": 3}
                    x += 1
                i += 1

        grids = grid_xy(n * 2)
        sorted_bts = [bts[n].get("bts") for n in sorted(bts)]
        bts_objects = itertools.chain(*sorted_bts)
        bts_grid = itertools.izip(bts_objects, grids)
        #[b.grid(**xy) for b, xy in bts_grid]

        self.make_scale(btframe, len(bts), 2, choices)
        return bts

    def bt_autofill(self, current_bts, amt, var):
        amts = current_bts.keys()
        mina = min(amts)
        maxa = max(amts)

        def check_buttons(name, index, mode):
            choice = var.get()
            range_dic = {0: range(amt,
                                  maxa + self.stimuli_step,
                                  self.stimuli_step),
                         1: range(mina,
                                  amt,
                                  self.stimuli_step)}

            select_range = range_dic.get(choice)
            all_vars = [current_bts.get(a).get("var")
                        for a in amts if a in select_range]
            select_vars = [v for v in all_vars if v.get() != choice]
            [v.set(choice) for v in select_vars]
        return check_buttons

    def enable_buttons(self, on):
        bt_states = {True: "normal",
                     False: "disabled"}
        bt_state = bt_states.get(on, "normal")
        blists = [b.get("bts") for b in self.current_bts.values()]
        [[b.config(state = bt_state) for b in blist]
         for blist in blists]
        return None

    def update_question(self, stimuli, real = True):
        qidx, stimuli = stimuli
        elicit = stimuli.get("elicit")

        if elicit == "prob":
            self.stimuli_step = 5
        else:
            commodity_step_dic = {"tea": 100, "money": 20}
            self.stimuli_step = commodity_step_dic.get(self.commodity)

        self.pie.elicit = elicit
        self.qidx = qidx
        self.cl_idx = int(stimuli.get("qidx"))
        self.stimuli_dic.update({qidx: (qidx, stimuli)})
        choices = self.new_choices(stimuli)
        self.new_visuals(qidx, stimuli, real)
        if real == True:
            self.new_buttons(qidx, choices)
        else:
            pass
        return None

    def get_choice_range(self, stimuli):
        elicit = stimuli.get("elicit")
        if elicit == "prob":
            p2 = int(float(stimuli.get("p2")) * 100)
            choice_range = range(0, p2 + self.stimuli_step, self.stimuli_step)
        else:
            a1 = stimuli.get("c21")
            a2 = stimuli.get("x22")
            if a1.lower() == "na":
                a1 = stimuli.get("y22")
                if a1.lower() == "na":
                    a1 = 0

            if a1 > a2:
                min_a = int(a1)
                max_a = int(a1) + int(a2)
            else:
                min_a = min(int(a1), int(a2))
                max_a = max(int(a1), int(a2))

            choice_range = range(min_a,
                                 (max_a + self.stimuli_step),
                                 self.stimuli_step)
            pass
        return choice_range

    def new_choices(self, stimuli):
        choice_range = self.get_choice_range(stimuli)
        self.start = start = random.choice(choice_range)
        self.choice_range = iter(choice_range)
        self.c0.set(start)
        self.c_1.set(start)
        self.current_stimuli = stimuli
        self.steps = choice_range
        self.mmin, self.mmax = (min(choice_range),
                                max(choice_range))
        self.checked = []
        return choice_range

    def new_buttons(self, qidx, stimuli):
        btframe = self.bt_frame.children.get("buttons" + str(qidx-1))
        if btframe != None:
            btframe.pack_forget()
        bts = self.draw_buttons(stimuli, qidx)
        self.buttons[qidx] = bts
        self.current_bts = bts
        self.enable_buttons(on = False)
        return None

    def new_visuals(self, qidx, stimuli, real):
        if self.mode == "practice":
            qtext = "Practice question {} of {}".format(qidx,
                                                        self.nquestions)
        else:
            qtext = "Question {} of {} for '{}'".format(qidx,
                                                        self.nquestions,
                                                        self.commodity)

        if real == False:
            qtext = "Choice summary: " + qtext
        self.title.config(text = qtext)
        self.edit.pack_forget()
        self.pie.update_question(stimuli, real)
        self.pie.focus_set()
        if self.pie.elicit == "prob":
            self.pie.pies[0].update_probability(self.c0.get())
        else:
            self.pie.pies[0].update_choice(self.c0.get())

    def start_question(self):
        try:
            self.enable_buttons(on = False)
            self.unbind("<Double-Button-1>")
            self.bind_all("<Double-Button-1>", self.make_selection)
            confirmed_choices = dict([(amt, b.get("var").get())
                                      for amt, b in self.current_bts.items()])
            #[self.current_choices[a].append(c)
            #for a, c in confirmed_choices.items()]
        except AttributeError as e:
            ## This most likely means it did not find current_bts, which is 
            ## created after that first question
            pass
        [bt.pack_forget() for bt in self.confirm_bts]
        try:
            self.update_question(self.stimuli.next())
        except StopIteration:
            self.end_iteration()

    def end_iteration(self):
        """Basic clean-up functions once the question iterator is exhausted

        'end_experiment' is either defined by end_experiment_default, or in
            the initiation of the Choicescreen
        """
        if self.mode == "practice":
            pass
        else:
            self.write_data()
        self.remove_functionality()
        self.pack_forget()
        self.end_experiment()
        return None


    def update_choice(self, new_choice = False):
        """Changes probability or amount of first pie during pingpong.
        """
        if new_choice == False:
            pass
        else:
            self.c0.set(new_choice)
        choice = self.c0.get()
        if self.pie.elicit == "prob":
            self.pie.pies[0].update_probability(choice)
        else:
            self.pie.pies[0].update_choice(choice)
        self.pie.deselect_pies()
        return None

    def make_selection(self, event):
        """Controls whether a selection as been made
            Event bindings toggle whether a choice is highlighted
            As soon as a choice is highlighted, pie.selected will change
        Args:
            event (key binding): <Return>, "<Double-Button-1>"
        """
        choice = self.pie.selected.get()
        if choice == 777 or choice == 600:
            tkMessageBox.showinfo("", ("Please make a choice"))
        else:
            cnext = self.pingpong(choice)
            if cnext is False:
                self.end_question(choice)
            else:
                self.update_choice()
        return None

    def determine_fill(self, choice, current):
        cdic = {1: (self.mmin, current),
                0: (current, self.mmax)}
        min_c, max_c = actual = cdic.get(choice)
        alternatives = cdic.get(abs(1 - choice))
        self.choice_record.update({choice:current})

        last_c_set = set(actual).intersection(set(alternatives))
        last_c = list(last_c_set)[0]
        if choice == 0:
            self.confirm_val = last_c
        elif choice == 1:
            self.confirm_val = last_c + self.stimuli_step
        return min_c, max_c, current, choice

    def pingpong(self, choice):
        current = self.c0.get()
        fill_params = self.determine_fill(choice, current)
        go_next = self.fill(*fill_params)
        self.tracker.update_choice(choice, current)

        if go_next == True:
            cnext = self.get_next()
            self.c_1.set(current)
            self.c0.set(cnext)
        elif go_next == False:
            cnext = False
        return cnext

    def fill(self, mmin, mmax, current, choice):
        fill_check = range(mmin,
                           mmax + self.stimuli_step, self.stimuli_step)
        #cvar = self.current_bts.get(current).get("var")
        #cvar.set(choice)
        self.checked.extend(fill_check)
        checked_set = set(self.checked)
        self.checked = list(checked_set)
        return len(checked_set) != len(self.steps)

    def get_next(self):
        """Takes the 2nd-last and the most recent choice made
        Determines what has been checked by comparing sets of checked and
        the entire set of steps.

        Returns: the point in the middle of the list of unchecked values
        """
        c0 = self.c0.get()
        c_1 = self.c_1.get()
        unchecked = list(set(self.steps) - set(self.checked))
        unchecked.sort()
        midpoint = int(round(len(unchecked) / 2))
        if c0 <= c_1:
            cnext = unchecked[-midpoint]
        elif c0 > c_1:
            cnext = unchecked[midpoint]
        return cnext

    def save_question(self):
        max_end = self.mmax + self.stimuli_step
        endpoints = {self.mmin: (self.confirm_val, "NA"),
                     max_end: ("NA", self.confirm_val - self.stimuli_step)}
        if self.confirm_val in endpoints.keys():
            confirm_tuple = endpoints.get(self.confirm_val)
        else:
            confirm_tuple = (self.confirm_val,
                             self.confirm_val - self.stimuli_step)

        self.data_labels = ("qorder", "cl_idx",
                            "elicit", "start_amt",
                            "min_choice_p0", "max_choice_p1",
                            "min_choice_0", "max_choice_1")
        data_point = (self.qidx,
                      self.cl_idx,
                      self.pie.elicit,
                      self.start) + \
            tuple(self.choice_record.values()) + confirm_tuple

        choice_row = dict(zip(self.data_labels, data_point))
        choice_row.update(self.idvars)

        #choice_row = dict(zip(self.data_labels, data_point))
        self.choice_data[self.qidx] = choice_row
        return None

    def end_question(self, choice):
        """Initiate the series of confirmation steps after end of pingpong
        """
        self.edit.pack(side = "right")
        self.bt_frame.focus_set()
        [bt.pack() for bt in self.confirm_bts]
        self.pie.end_question()
        self.tracker.confirmation_fill(choice)
        self.tracker.slider.config(command = self.control_scale)
        return None

    def remove_functionality(self):
        keys = ("<Up>", "<Down>", "<Button-1>")
        self.pie.set_bindings(on = False)
        self.unbind("<Double-Button-1>")
        self.tracker.slider.config(command = None)
        self.edit.pack_forget()
        self.bt_frame.pack_forget()
        return None

    def avoid_overwrite(self, base_name, data_file):
        if os.path.exists(data_file) == True:
            fnames = [f for f in os.listdir(data_path) if f[0:10] == base_name]
            fidx = len(fnames)
            new_base = base_name + "_{}".format(fidx)
            filename = new_base + ".csv".format(**self.idvars)
            data_file = os.path.join(data_path, filename)
        return None

    def write_data(self):
        """Unpack data dictionary and write to csv file

        --File name should be "time_enum_vid_wzb.hh.id.csv" 
        """

        data_path = self.main.data_path
        filename_vars = ("vid", "enum_id", "wzb.hh.id")
        self.idvars["wzbhhid"] = self.idvars["wzb.hh.id"]
        base_name = 'time_{vid}_{enum_id}_{wzbhhid}'.format(**self.idvars)
        filename = base_name + ".csv"
        data_file = os.path.join(data_path, filename)

        id_vars = ("wzb.hh.id", "wzb.ind.id", "vid", "tid", "enumerator")
        write_labels = id_vars + self.data_labels
        data_list = [[dic.get(l) for l in write_labels]
                     for dic in self.choice_data.values()]

        with open(data_file, "a") as csvfile:
            data = csv.writer(csvfile)
            if self.order == 0:
                data.writerow(write_labels)
            [data.writerow(row) for row in data_list]
        print "Data written to  " + data_file
        return None

    def end_experiment_default(self):
        self.begin_payment()
        return None

    def begin_payment(self):
        tkMessageBox.showinfo("", ("Payment."))
        self.pack_forget()
        self.main.pay_screen = Payment(self.main)
        return None

    def translate_choice_to_payment(self, stimuli, choice):
        block = stimuli.get("block")
        choice_dic = {True: "BLUE", False: "RED"}

        amt = None
        balls_0 = None
        balls_1 = None
        amt_0 = None
        amt_1 = None
        amt_c21 = None
        amt_double = False
        win_1 = None
        win_2 = None

        ## Took a shortcut with the times. Will not work for generalisations!
        t1 = int(stimuli.get("t12"))
        t2 = int(stimuli.get("t22"))
        dates = [(datetime.date.today() +\
                  datetime.timedelta(t * 365 / 12 + 1)).strftime("%d-%b-%Y")
                 for t in (t1, t2)]
        #self.pie.elicit = stimuli.get("elicit")

        name = self.idvars.get("name")
        if name == "":
            name = "The player "

        if self.pie.elicit == "amt":
            if block == "risk":
                if choice == False:
                    lottery = False
                    amt = self.pay_val
                    date = dates[0]
                    win_1 = amt
                else:
                    lottery = True
                    prob = 50
                    amt_0 = stimuli.get("x22")
                    amt_1 = stimuli.get("y22")
                    date = dates[1]
            elif block == "time":
                lottery = False
                date = dates[0]
                if choice == False:
                    amt = self.pay_val
                    win_1 = amt
                else:
                    amt = stimuli.get("x22")
                    amt_c21 = stimuli.get("c21")
                    win_1 = amt
                    if amt_c21 != "na":
                        amt_double = True
                        lottery = "amt_double"
                        date = "{} and {}".format(*dates)
                        win_1 = amt_c21
                        win_2 = amt
                
        elif self.pie.elicit == "prob":
            if choice == False:
                lottery = True
                prob = self.pay_val
                amt_0 = stimuli.get("x22")
                date = dates[0]
            else:
                lottery = False
                amt = stimuli.get("x22")
                date = dates[1]
                win_1 = amt

        if amt_double == False:
            direct_winnings = amt
            dates[1] = None
        else:
            direct_winnings = "{}g and {}".format(amt_c21, amt)

        if lottery == True:
            balls_0 = (int(prob) * 20 )/ 100
            balls_1 = 20 - balls_0

        lottery_name_dic = {True: "a LOTTERY",
                            False: "a DIRECT PAYMENT",
                            "amt_double": "two DIRECT PAYMENTS"}

        pay_type = lottery_name_dic.get(lottery)
        red = choice_dic.get(choice)

        results_text = "{} chose {} This means {}.\n".format(name,
                                                               red,
                                                               pay_type)

        direct_text = "{} gets a direct payment of {}".format(name,
                                                              amt)

        lottery_base = ("Play the lottery with {} GREEN balls and {} "
                        "YELLOW balls.")

        lottery_text = lottery_base.format(balls_0,
                                           balls_1,
                                           name, amt_0,
                                           name, amt_1)

        texts_dic = {True: lottery_text, False: ""}

        output = results_text + texts_dic.get(lottery, "")

        ctext_dic = {"tea": "g of TEA", "money": "Rs"}
        pay_configs = {"amt_0": amt_0,
                       "amt_1": amt_1,
                       "lottery": lottery,
                       "amt": amt,
                       "amts": (amt_0, amt_1),
                       "times": (t1, t2),
                       "paydate_1": dates[0],
                       "paydate_2": dates[1],
                       "name": name,
                       "balls": (balls_0, balls_1),
                       "t1": t1,
                       "t2": t2,
                       "winnings": direct_winnings,
                       "win_1": win_1,
                       "win_2": win_2,
                       "commodity": self.commodity,
                       "commodity_text":ctext_dic.get(self.commodity),
                       "date": date}
        pay_configs.update(self.idvars)
        return output, pay_configs

    def show_payment(self, qidx):
        #self.pie.focus_force()
        stimulus = self.stimuli_dic.get(qidx)
        self.update_question(stimulus, real = False)
        if self.pie.elicit == "prob":
            self.pie.pies[0].update_probability("---")
        elif self.pie.elicit == "amt":
            self.pie.pies[0].update_choice("---")
        self.pie.selected.set(999)


#root = tk.Tk()
#ChoiceScreen(root)
