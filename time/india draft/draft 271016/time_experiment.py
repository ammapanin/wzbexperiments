### Determines the whole structure of the program
### Set the desks, import the stimuli etc.

### Last updated: 4.11.16
## TODO:
## - Work on the switch between tea and money, make it prettier
## - Have a log-in screen for Akurru
## - Start thinking about the general log-in screen

import Tkinter as tk
import tkFont
import tkMessageBox
import os
import csv
import random

from program_files.Choicescreen import ChoiceScreen
from program_files.training import Training
from program_files.startscreen.startscreen import Startscreen
from program_files.startscreen.definitions import *

class TimeExperiment(tk.Frame):
    def __init__(self, master, stimuli_path, debug, prob_type, commodities):
        tk.Frame.__init__(self, master)
        self.pack(side = "top", fill = "both", expand = True)
        self.root  = master
        self.stimuli_path = stimuli_path

        if debug == True:
            self.debug_segue = False
            self.idvars = (0, 0)
            self.start_experiment("practice",
                                  end_func = False,
                                  prob_type = prob_type,
                                  commodity = "tea")
        else:
            self.deskvar = tk.IntVar()
            self.deskvar.set("")
            self.start_screen()
            self.debug_segue = self.segue_experiment
            self.prob_type = prob_type
            self.commodities = commodities

    def start_screen(self):
         login = tk.Frame(self)
         login.pack()
         Startscreen(login, self.show_instructions, definitions, False)
         self.login = login
         return None
    #     self.idvars = (tk.StringVar(self), tk.StringVar(self))
    #     enum_var, ind_var = self.idvars

    #     titlefont = tkFont.Font(size = 20, weight = "bold")
    #     title = tk.Label(self,
    #                      text = ("Welcome to the experiment."),
    #                      justify = "left", font = titlefont)

    #     with open(os.path.join(base_folder,
    #                            "program_files",
    #                            "enumerators.csv")) as enums_file:
    #             enums = csv.reader(enums_file)
    #             enum_names = tuple([enum[0] for enum in enums])

    #     with open(os.path.join(base_folder,
    #                            "program_files",
    #                            "akkuru_names.csv")) as akkuru_file:
    #             akkuru = csv.reader(akkuru_file)
    #             akkuru_names = tuple([person[0] for person in akkuru])

    #     enumerators = enum_names
    #     enums = apply(tk.OptionMenu,
    #                   (login, enum_var) + tuple(enum_names))
    #     ind = apply(tk.OptionMenu,
    #                 (login, ind_var) + tuple(akkuru_names))
    #     labs = [tk.Label(login, text = txt)
    #             for txt in ("Enumerator", "Individual")]
    #     ok = tk.Button(login, text = "OK")

    #     big_widgets =  enumerate((enums, ind, ok))
    #     [w.grid(row = i, column = 0, sticky = "w") for i, w in enumerate(labs)]
    #     [w.grid(row = i, column = 1, sticky = "w") for i, w in big_widgets]

    #     [w.pack(side = "top", anchor = "w", padx = 10, pady = 10)
    #      for w in (title, login)]

    #     def next_step():
    #         title.destroy()
    #         login.destroy()
    #         self.show_instructions()
    #         return None
    #     ok.config(command = next_step)
    #     #entry_box.bind("<Return>", next_step)

    def show_instructions(self, idx_dic):
        self.login.destroy()

        self.idvars = idx_dic
        instructionfont = tkFont.Font(size = 40, weight = "bold")
        button_font = tkFont.Font(size = 20, weight = "bold")
        instruction_text = ("Thank you for your time. \n"
                            "We will start with two real examples. \n"
                            "Then we will use the computer to record all"
                            " your choices. \n"
                            "At the end, one choice will be selected"
                            " and we will pay you.")

        iframe = tk.Frame(self)
        iframe.pack(side = "top", fill = "both", expand = False, anchor = "w")
        instructions = tk.Label(iframe,
                                text = instruction_text,
                                font = instructionfont,
                                wrap = 1200,
                                justify = "left")
        instructions.pack(side = "top",
                          expand = False,
                          anchor = "w",
                          pady = 10,
                          padx = 10)
        def next_step():
            iframe.destroy()
            self.training = Training(self)
            self.training.next_function = lambda: self.start_experiment("practice",
                                                                   self.debug_segue,
                                                                   self.prob_type,
                                                                   "tea")
            return None

        ok_bt = tk.Button(iframe,
                          font = button_font,
                          text = "Begin real examples",
                          height = 5)

        ok_bt.config(command = next_step)
        ok_bt.pack(side = "top", anchor = "w", padx = 20)

    def setup_full_experiments(self, mode, prob_type):
        stimuli = [self.get_stimuli(mode, commodity)
                   for commodity in self.commodities]
        #idvars = tuple([v for v in self.idvars.values()])
        idvars = self.idvars
        self.choices = [ChoiceScreen(self,
                                     cstimuli,
                                     mode,
                                     False,
                                     idvars,
                                     prob_type,
                                     commodity)
                        for cstimuli, commodity
                        in zip(stimuli, self.commodities)]

        self.start = random.choice([0, 1])
        self.other = abs(1 - self.start)

        self.choices[self.start].end_experiment = self.show_other
        #self.choices[self.other].end_experiment = self.end_experiment
        self.choices[self.start].start()
        return self.choices

    def show_other(self):
        start = self.choices[self.start]
        #start.write_data()
        start.pack_forget()
        other = self.choices[self.other]
        other.pack(expand = True, fill = "both")
        other.start()
        return None

    def end_experiment(self):
        [p.pack_forget() for p in self.choices]
        frame = tk.Frame(self)
        frame.pack(fill = "both", expand = True)

        pay_var = tk.IntVar(self)
        commodityfont = tkFont.Font(size = 25, weight = "bold")
        choices = [tk.Radiobutton(frame,
                                  value = i,
                                  text = screen.commodity,
                                  variable = pay_var,
                                  font = commodityfont) for
                   i, screen in enumerate(self.choices)]
        [bt.pack(side = "left") for bt in choices]

        def trigger_payment():
            idx = pay_var.get()
            frame.pack_forget()
            self.choices[idx].pack(fill = "both", expand = True)
            self.choices[idx].begin_payment("event")
            return None

        ok = tk.Button(frame,
                       text = "OK, begin payment",
                       command = trigger_payment)

        ok.pack(side = "left")

    def start_experiment(self, mode, end_func, prob_type, commodity):
        self.training.destroy()
        stimuli = self.get_stimuli(mode, commodity)
        print self.idvars
        #idvars = tuple(self.idvars.values())#tuple([v.get() for v in self.idvars])
        self.choices = ChoiceScreen(self,
                                    stimuli,
                                    mode,
                                    end_func,
                                    self.idvars,
                                    prob_type,
                                    commodity)
        self.choices.start()
        return None

    def segue_experiment(self):
        tkMessageBox.showinfo("", ("You will now begin the real experiment. "
                                   "Please ask your experimenter if anything "
                                   "remains unclear."))

        self.choices.pack_forget()
        self.setup_full_experiments("full", self.prob_type)
        # self.start_experiment("full",
        #                       end_func = False,
        #                       prob_type = self.prob_type,
        #                       commodity = self.commodity)
        return None

    def get_stimuli(self, mode, commodity):
        """Transforms the csv file into a form ready for the program

        Args: mode (string) -- "full", "practice"
        Stimuli file requires the following headers:
         ("elicit" : 'prob' or 'amt', "qidx",
          "c11, x12, c1, y12, p1, c21, x22, c22, y22, p2, t11, t12, t21, t22")
        """

        stimulipath = self.stimuli_path + "_{}_{}.csv".format(commodity, mode)
        blocks_dic = dict()
        with open(stimulipath, "rU") as sfile:
            dialect = csv.Sniffer().sniff(sfile.read(1024))
            sfile.seek(0)
            scsv = csv.reader(sfile, dialect)
            fnames = scsv.next()
            lines_dic = [dict(zip(fnames, line)) for line in scsv]
            for line in lines_dic:
                block = line.get("block")
                if blocks_dic.get(block) is not None:
                    blocks_dic[block].append(line)
                else:
                    blocks_dic[block] = [line]

            blocks = blocks_dic.values()

            # Uncomment here to vary randomisation
            # TODO streamline randomisation tagging
            [random.shuffle(block) for block in blocks]
            random.shuffle(blocks)
            stimuli = [stim for b in blocks for stim in b]
            lines = enumerate(stimuli, 1)
        return lines, len(stimuli)

def run_experiment(stimuli_path, debug, prob_type, commodities):
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.title("Risk and time experiment")
    x = TimeExperiment(root, stimuli_path, debug, prob_type, commodities)
    root.mainloop()
    return x

#base_folder = "/Users/aserwaahWZB/Projects/GUI Code/time/india draft/draft 271016/"
base_folder = os.path.dirname(os.path.realpath(__file__))
stimuli_path = csvpath = os.path.join(base_folder,
                                      "program_files",
                                      "test",
                                      "stimuli")
x = run_experiment(stimuli_path,
                   debug = False,
                   prob_type = "circles",
                   commodities = ("tea", "money"))


