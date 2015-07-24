# Main budget program
# Last updated: 14/04/15; 19/03/15; 26/04/15


import Tkinter as tk
import tkMessageBox
import tkFont
import os
import sys

import random
import decimal
import csv

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time


budgetpath = os.path.dirname(os.path.abspath(__file__))
experimentspath = os.path.dirname(budgetpath)
#print "experiments path:  ", experimentspath
sys.path.append(experimentspath)

from shared.startscreen import Startscreen
from budget_risk import RiskScreen
from budget_time import TimeScreen
from budget_payment import BudgetPayment



### Program version ####
version = "2.4"

# version 1.0: Oriinal version sent out beginning of April 2015
# version 1.2: added 2 makali hh, ensured version saved
# version 1.35: fixed Udukunte; removed Keeranigere
# version 1.36: Updated Kallapura
# version 2.1: fixed Tattiguppe; added Byranakahalli, Banavasi
# version 2.2: added Keeranigere, Belkere
# version 2.3: added Keeranigere properly
# version 2.4: added Mogenahalli properly

textfilename = os.path.join(budgetpath, "budget_texts.txt")

with open(textfilename, "r") as textfile:
    bob = textfile.read().split("XXX")
    instructiontext = bob[0]
    risktext = bob[1]
    timetext = bob[2]



class Budget(BudgetPayment):

    def __init__(self, master, dims, n_risk, n_time):

        self.base = budgetpath
        self.paymentsPATH = os.path.join(experimentspath,
                                         "payments")

        self.comments_path = os.path.join(experimentspath,
                                          "comments")

        if os.path.isdir(self.paymentsPATH) == False:
            os.makedirs(self.paymentsPATH)

        self.root = dims["root"]
        self.main_master = master
        self.make_frames(master)

        self.total_questions = n_risk + n_time * 2
        q_index = self.display_question_index(self.topmost_frame)
        self.qtext = q_index["lab"]

        texts = {"risk": risktext, "time": timetext}

        self.sp_screen = self.start_payment(self.budget_frame)

        treatment_opts = {"master": self.budget_frame,
                          "dims": dims,
                          "q_index": q_index,
                          "texts": texts,
                          "base": self.base,
                          "sp_screen": self.sp_screen}

        self.riskscreen = RiskScreen(n_questions = n_risk,
                                     **treatment_opts)
        self.timescreen = TimeScreen(n_questions = n_time,
                                     **treatment_opts)

        screens = [self.riskscreen, self.timescreen]

        self.riskscreen.other_treatment = self.timescreen
        self.timescreen.other_treatment = self.riskscreen

        random.shuffle(screens)

        self.current_screen = screens[0]
        self.next_screen = screens[1]

        self.qlists = [(screen.treatment, i)
                       for screen in (self.current_screen,
                                      self.next_screen)
                       for i in range(1, screen.n_questions + 1)]

        self.treatment_question_dic = dict(enumerate(self.qlists,1))

        self.current_screen.treatment_order = 1
        self.next_screen.treatment_order = 2

        self.treatment_dic = {"risk": {"data": self.riskscreen.q_dic,
                                       "screen": self.riskscreen},
                              "time": {"data": self.timescreen.q_dic,
                                       "screen": self.timescreen}}

        t1 = self.timescreen.times_t1
        t2 = self.timescreen.times_t2


        texts_dic = {"risk": risktext,
                     "time": timetext.format(t1[0], t1[1],
                                             t2[0], t2[1])}

        treatment = self.current_screen.treatment
        introtext = instructiontext.format(treatment.upper(),
                                            texts_dic[treatment])

        self.my_first_text = introtext

        self.startscreen = Startscreen(self.start_frame,
                                       self.show_instructions,
                                       dims["root"])



    def show_instructions(self, idx_dic):
        """Draw starting instructions and save identifier data"""

        #print "ind_data", idx_dic
        idx_dic["version"] = version
        self.idx_data = idx_dic
        [s.ind_data.update(idx_dic)
         for s in self.riskscreen, self.timescreen]

        instruction_font = tkFont.Font(size = 20, weight = "bold")
        instructions = tk.Label(self.start_frame,
                                text = self.my_first_text,
                                font = instruction_font,
                                wraplength = 1000,
                                justify = "left")
        instructions.pack(side = "top",
                          expand = True,
                          fill = "both")
        ok = tk.Button(self.start_frame,
                       text = "Begin experiment",
                       command = self.begin_experiment)
        ok.pack(side = "right")
        return None

    def begin_experiment(self):
        self.start_frame.pack_forget()

        pack_classic = {"expand": True,
                        "side": "top",
                        "fill": "both"}

        self.qtext.pack(**pack_classic)
        self.budget_frame.pack(**pack_classic)
        self.current_screen.mainframe.pack(anchor = "n",
                                           **pack_classic)

        self.current_screen.go_next()
        self.current_screen.next_bt.pack(side = "left")


    def make_frames(self, master):
        self.comments_frame = tk.Frame(master)
        self.comments_frame.pack(side = "top")
        self.start_frame = tk.Frame(master)
        self.start_frame.pack(side = "top",
                              fill = "both",
                              expand = True)

        self.topmost_frame = tk.Frame(master)
        self.topmost_frame.pack(side = "top")

        self.payment_frame = tk.Frame(self.topmost_frame)
        self.payment_frame.pack(side = "bottom")
        self.budget_frame = tk.Frame(master)


        return None

    def display_question_index(self, master):
        q_frame = tk.Frame(master)
        q_info = tk.Label(q_frame,
                          text = ("Please make sure participants "
                                  "see both prices."))

        index_text = "Question {} of {}".format({}, self.total_questions)
        qt_font = tkFont.Font(size = 20, weight = "bold")

        q_text = tk.Label(q_frame,
                         text = index_text.format("X"),
                         font = qt_font,
                         wraplength = 1000,
                         justify = "left")

        q_text.pack(side = "top")

        return {"text":index_text, "lab":q_frame, "index": q_text, "info": q_info}


    def start_payment(self, master):
        startpayfont = tkFont.Font(size = 16, weight = "bold")
        sp_screen = tk.Frame(master)
        start_pay_text = (" Thank you for completing the experiment."
                          " You may now proceed to payment.\n\n"
                          "You will draw one question out of {}. "
                          "We will pay you according to your choice for "
                          "that question. \n\n If the question was a TIME question, "
                          "you will receive direct payments according to the"
                          "date you chose. \n\nIf the question was a RISK question,"
                          " you will play a lottery according to the amounts "
                          "you chose.")

        start_paylab = tk.Label(sp_screen,
                                text = start_pay_text.format(self.total_questions),
                                wraplength = 800,
                                anchor = "w",
                                justify = "left",
                                font = startpayfont)
        start_paybt = tk.Button(sp_screen,
                                text = "OK to continue",
                                command = self.make_payment_objects)

        start_paylab.grid(row = 0)
        start_paybt.grid(row = 1, sticky = "s", pady = 10)

        return sp_screen




def run(nrisk, ntime):
    root = tk.Tk()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.title("Budget experiment")
    root.attributes("-fullscreen", True)
    dims = {"root": root, 'width':w, 'height':h}
    nghi = Budget(root, dims, nrisk, ntime)
    print "Budget experiment running...ASP"
    root.mainloop()
    return nghi


#nghi = full_program()
