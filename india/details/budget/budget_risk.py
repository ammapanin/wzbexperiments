# Budget allocation problem

import Tkinter as tk
import tkFont

import random
from decimal import Decimal as dec
import os
import time

from budget_envelope import Envelope as ev
from budget_methods import budgetSetup, budgetMethods


class RiskScreen(ev, budgetMethods, budgetSetup):

    def __init__(self, master, dims, n_questions, q_index, sp_screen, texts, base):
        self.treatment = "risk"
        self.setup_treatment(master, n_questions, dims, q_index, texts, base)
        self.sp_screen = sp_screen

        self.riskcol = self.payoff_dic['x1']['col']
        self.nullcol = self.payoff_dic['x2']['col']
        self.prob = 5

        self.make_additional_frames()

        self.draw_budgetline()
        self.show_prices()

        # Show lottery
        self.lottery = ev(self.lottery_frame, 
                          certainty = False)

    def add_lottery_text(self, master):
        lottery_lab = tk.Label(master,
                               text = "This is the lottery you will play")
        lottery_lab.pack(side = "bottom")
        return None

    def make_additional_frames(self):
        colcentral, colx1, colx2, = 1, 0, 2
        rowbudget = 1

        self.lottery_frame = tk.LabelFrame(self.choice_graphics_frame)
        self.lottery_frame.pack(side = "bottom",
                                anchor = "center",
                                pady = 15)
        return None

    def update_times(a, b):
        pass
        return None


if __name__ == "__main__":
    bob = full_program()
    print "Risk running...ASP"
