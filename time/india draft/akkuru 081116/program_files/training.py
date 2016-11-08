#!/usr/bin/python
# -*- coding: utf-8 -*-


import Tkinter as tk
import tkFont

class Training(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.pack()
        self.setup_examples()
        self.next_function = ""

    def setup_examples(self):
        self.title_font = tkFont.Font(size = 20)
        self.title = tk.Label(self, font = self.title_font)
        self.title.pack(side = "top", padx = 50, anchor = "w")

        self.tea = self.create_tea_example()
        self.money = self.create_money_example()
        self.bt = tk.Button(self, 
                            text = "Example complete",
                            command = self.next_example)
        self.bt.pack(side = "bottom", padx = 20, anchor = "w")
        return None

    def next_example(self):
        self.tea.pack_forget()
        txt = "2. Step by step MONEY example"
        self.title.config(text = txt)

        self.money.pack(side = "top", anchor = "w")
        self.bt.config(command = self.next_function)
        return None

    def make_bt_pair(self, row_i, master, values):
        pair_var = tk.StringVar(master)
        pair_var.set("")
        bts = [tk.Radiobutton(master, 
                              value = v, 
                              variable = pair_var,
                              text = v)
               for v in values]
        [bt.grid(row = row_i, column = ix) 
         for bt, ix in zip(bts, (2, 3))]
        row = tk.Label(master, text = "{}. ".format(row_i))
        row.grid(row = row_i, column = 0) 

        return bts

    def create_tea_example(self):
        frame = tk.Frame(self)
        frame.pack(side = "top", anchor = "w")

        txt = "1. Step by step TEA example"
        self.title.config(text = txt)

        ce_list = ["{}g".format(g) for g in range(0, 600, 100)]
        #ce_list[-1] = "1kg"
        nrow = len(ce_list)
        lottery = ("50% chance of 1kg, 50% chance of 500g",) * nrow
        values = zip(ce_list, lottery)
        [self.make_bt_pair(i, frame, vals)
         for i, vals in enumerate(values, 1)]
        return frame

    def create_money_example(self):
        frame = tk.Frame(self)
        prob_list = [("{}% chance of Rs 200 TOMORROW,"
                      " {}% chance of 0").format(p, 100 - p) 
                     for p in range(0, 105, 5)]
        nrow = len(prob_list)
        fixed = ("Rs 200 after 6 MONTHS",) * nrow
        values = zip(prob_list, fixed)
        bts = [self.make_bt_pair(i, frame, vals)
         for i, vals in enumerate(values, 1)]
        return frame


#root = tk.Tk()
#x  = Training(root)
