#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk
import datetime
import csv
import itertools
import os

class Payment(tk.Frame):
    def __init__(self, main_container):
        tk.Frame.__init__(self, main_container)
        self.pack()

        self.main = main_container
        self.start_idx = self.main.start
        self.other_idx = abs(1 - self.main.start)
        self.setup_payment()

    def setup_payment(self):
        self.info_frame = tk.Frame(self)
        self.info_frame.pack(side = "bottom")

        self.text_labs = [tk.Label(self.info_frame)
                          for i in (0, 1)]
        [lab.pack(side = "top") for lab in self.text_labs]

        self.pay_ok = tk.Button(self.info_frame, 
                                text = "OK",
                                command = self.finish_payment)
        self.qid = tk.IntVar(self)
        self.row_idx = tk.StringVar(self)
        self.qid.trace("w", self.get_question)
        self.row_idx.trace("w", self.show_question)

        self.qid.set("")
        self.row_idx.set("")


        bts_frame = tk.Frame(self.info_frame)
        lottery_var = tk.IntVar(bts_frame)
        lottery_var.set(1969)
        bts = [tk.Radiobutton(bts_frame, 
                              variable = lottery_var, 
                              value = a) 
        for a in (0, 1)]
        [bt.pack(side = "left") for bt in bts]

        def set_winnings(name, index, mode):
            self.pay_ok.config(text = "OK", 
                               command = self.finish_payment)

            win = lottery_var.get()
            atup = self.pay_dic["amts"]
            ttup = self.pay_dic["times"]
            t = int(ttup[win])
            self.pay_dic["winnings"] = atup[win]

        lottery_var.trace("w", set_winnings)
        self.bts = bts
        self.bts_frame = bts_frame
        self.menu_frame, self.qid_menu, self.row_menu = self.draw_menus()
        self.pay_ok.pack(side = "bottom", padx = 15)
        return None

    def draw_menus(self):
        """Draw listboxes indexed by self.pay_idx and self.row_idx
        """
        frame = tk.Frame(self)
        frame.pack(side = "top")

        idx = (self.start_idx, self.other_idx)
        cscreens = [self.main.choices[i] for i in idx]
        self.cscreens = cscreens

        qids = itertools.chain(*[c.stimuli_dic.keys() for c in cscreens])
        qscreens = [[c for i in c.stimuli_dic.keys()] for c in cscreens]
        qid_screen_dic = dict(enumerate(itertools.chain(*qscreens), 1))
        qid_dic = dict(enumerate(qids, 1))

        self.qid_screen_dic = qid_screen_dic
        self.qid_dic = qid_dic
        qid_list = self.qid_dic.keys()

        qidx_menu = apply(tk.OptionMenu,
                          (frame, self.qid) + tuple(qid_list))

        row_menu =  apply(tk.OptionMenu,
                          (frame, self.row_idx) + ("",))
        menus = (qidx_menu, row_menu)

        [menu.config(width = 20) for menu in menus]
        [menu.grid(row = i, column = 1) for i, menu in enumerate(menus)]

        self.labels = [tk.Label(frame, justify = "left") for i in (0, 1)]
        [lab.grid(row = i, column = 0, sticky = "w")
         for i, lab in enumerate(self.labels)]

        qtext = ("1. Please select a question between"
                 " 1 and {}").format(len(qid_dic))
        self.labels[0].config(text = qtext)
        return frame, qidx_menu, row_menu

    def update_lottery(self, amts):
        self.bts_frame.pack(side = "top")
        amts = self.pay_dic["amts"]
        [b.config(text = a) for a, b in zip(amts, self.bts)]
        return None

    def get_question(self, name, index, mode):
        """ Trace function for qid var,
            Once var is selected, fill in rows for subquestion
        """        
        self.restart_payment()
        pos_id = self.qid.get()
        pay_screen = self.qid_screen_dic.get(pos_id)
        qid = self.qid_dic.get(pos_id)
        self.populate_row_menu(pay_screen, qid)
        return None

    def restart_payment(self):
        self.row_menu["menu"].delete("0", "end")
        self.bts_frame.pack_forget()
        [screen.pack_forget() for screen in self.cscreens]
        [lab.config(text = "") for lab in self.text_labs]
        self.pay_ok.config(text = "OK", 
                           command  = self.finish_payment)

    def populate_row_menu(self, pay_screen, qidx):
        """Fill in rows to be selected for subquestion
        """
        stimuli_tup = pay_screen.stimuli_dic.get(qidx)
        stimuli = stimuli_tup[1]
        pay_screen.update_question(stimuli_tup, real = False)
        choice_range = pay_screen.get_choice_range(stimuli)

        self.pay_stimuli = stimuli
        a1 = stimuli.get("x22")
        a2 = stimuli.get("y22")
        if a2.lower() == "na":
            a2 = 0
        min_a = min(int(a1), int(a2))
        max_a = max(int(a1), int(a2))

        e = stimuli.get("elicit")
        edic = {"amt": pay_screen.commodity, "prob": "prob"}
        cdic = {"tea": " g", "money": "Rs", "prob": " %"}
        suffix_i = edic.get(e, "money")
        suffix = cdic.get(suffix_i)

        choices = ["{}: {}{}".format(i, x, suffix)
                   for i, x in enumerate(choice_range, 1)]
        self.row_menu["menu"].delete("0", "end")
        [self.row_menu["menu"].add_command(label = choice,
                                           command = tk._setit(self.row_idx, 
                                                               choice))
         for choice in choices]

        qtext = ("2. Please select a sub-question"
                 " between 1 and {}").format(len(choices))
        self.labels[1].config(text = qtext)
        self.pay_vars = (pay_screen, qidx, stimuli)
        return None
    
    def show_question(self, name, index, mode):
        """Display choicescreen after a sub-question has been selected
        --Traced by self.qid
        """
        if self.pay_ok:
        ## This unituitive if statement is because this is a trace function
        ## It ends up being called(?) before pay_ok is created
            self.pay_ok.config(text = "OK", 
                               command  = self.finish_payment)

        pay_screen, qidx, stimuli = self.pay_vars 
        self.show_pay_question(pay_screen, qidx, stimuli)
        return None

    def show_pay_question(self, pay_screen,  qidx, stimuli):
        qdata = pay_screen.choice_data.get(qidx)
        vstring = self.row_idx.get()
        val = int(vstring.split(":")[1].strip()[0:-2])
        pay_screen.pay_val = val
        min_0 = qdata.get("min_choice_0")
        pay_screen.last_choice = min_0
        choice = val < min_0
        pay_screen.c0.set(val)
        pay_screen.pie.elicit = qdata.get("elicit")
        pay_screen.update_choice()
        pay_screen.pie.__class__.class_selected.set(choice)
        pay_screen.pack(fill = "both", expand = True)
        text, results = pay_screen.translate_choice_to_payment(stimuli, choice)
        self.update_payment_info(text, results)
        return None

    def update_payment_info(self, text_output, pay_configs):  
        [lab.config(text = "") for lab in self.text_labs]
        self.bts_frame.pack_forget()

        self.text_labs[0].config(text = text_output)      
        lottery = pay_configs.get("lottery")
        self.pay_dic = pay_configs 

        if lottery == True:
            amts = [pay_configs.get(a) for a in ("amt_0", "amt_1")]
            self.update_lottery(amts)
        
    def finish_payment(self,):
        payment_output = ("{name} will receive {winnings}"
                          " {commodity_text} on {date}").format(**self.pay_dic)
        self.text_labs[1].config(text = payment_output)
        self.pay_ok.config(text = "End experiment", 
                           command = self.complete_experiment)
        return None

    def complete_experiment(self):
        self.write_payment()
        self.main.root.destroy()

    def write_payment(self):
        id_vars = ("wzb.hh.id", "wzb.ind.id", "vid", "tid", "enumerator")
        win_vars = ("name", "win_1", "win_2", "paydate_1", "paydate_2",
                    "commodity")
        write_vars = id_vars + win_vars
        pay_row = [self.pay_dic.get(v) for v in write_vars]

        fname = "payments_{enum_id}_{vid}.csv".format(**self.pay_dic)
        fpath = os.path.join(self.main.payment_path,
                             fname)

        with open(fpath, "a") as pay_csv:
            pay = csv.writer(pay_csv)
            if os.path.exists(fpath) == False:
                pay.write_row(write_vars)
            pay.writerow(pay_row)
        return None
        


### Take over from here
# Test the dates of double payments
# Change the text 1.1 etc, and colour
# DO NOT WORK BEYOND 9.00pm
