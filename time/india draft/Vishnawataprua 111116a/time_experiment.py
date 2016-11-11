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
from program_files.questionnaire.questionnaire import Questionnaire


class TimeExperiment(tk.Frame):
    def __init__(self,
                 master,
                 program_path,
                 stim_path_str,
                 debug,
                 prob_type,
                 commodities,
                 survey_dic):

        tk.Frame.__init__(self, master)
        self.pack(side = "top", fill = "both", expand = True)
        self.root  = master

        if debug == True:
            self.debug_segue = False
            self.idvars = (0, 0)
            self.start_experiment("practice",
                                  end_func = False,
                                  prob_type = prob_type,
                                  commodity = "tea")
        else:
            self.survey_dic = survey_dic
            self.setup_paths(program_path, stim_path_str)
            self.start_screen()
            self.debug_segue = self.segue_experiment
            self.prob_type = prob_type
            self.commodities = commodities


    def setup_paths(self, base_folder, stim_path_str):
        """Create stimuli, data, payment paths as attributes of TimeExperiment
        """
        def make_if_not(path):
            if os.path.exists(path) == False:
                os.makedirs(path)
                print "Created path:  {}".format(path)
            return None

        self.stimuli_path = os.path.join(base_folder,
                                         "program_files",
                                         stim_path_str,
                                         "stimuli")

        self.payment_path = os.path.join(base_folder,
                                         "payment")

        self.data_path = os.path.join(base_folder,
                                      "data")

        survey_path = os.path.join(base_folder,
                                   "survey data")
        self.survey_dic["data_path"] = survey_path

        data_paths =  (self.payment_path, self.data_path, survey_path)
        [make_if_not(p) for p in data_paths]
        return None

    def start_screen(self):
         login = tk.Frame(self)
         login.pack()
         Startscreen(login, self.show_instructions, definitions, False)
         self.login = login
         return None

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
            self.training.next_function = lambda: self.start_practice("practice",
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

    def start_practice(self, mode, end_func, prob_type, commodity):
        self.training.destroy()
        stimuli = self.get_stimuli(mode, commodity)
        self.practice = ChoiceScreen(self,
                                stimuli,
                                mode,
                                end_func,
                                self.idvars,
                                prob_type,
                                commodity)
        self.practice.start()
        return None

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

        def begin():
            s = self.choices[self.other]
            self.show_choices(s)
            return None

        self.choices[self.start].end_experiment = begin
        self.choices[self.other].end_experiment = self.show_survey
        #self.choices[self.other].end_experiment = self.end_experiment
        self.choices[self.start].start()
        self.choices[self.start].order = 0
        self.choices[self.other].order = 1
        return self.choices

    def show_choices(self, screen):
        [c.pack_forget() for c in self.choices]
        print "the screen is here", screen
        screen.start()
        return None

    def segue_experiment(self):
        tkMessageBox.showinfo("", ("Begin the real experiment."))
        self.practice.pack_forget()
        self.setup_full_experiments("full", self.prob_type)
        return None

    def show_survey(self):
        self.survey_dic["next_function"] = self.choices[-1].begin_payment
        self.survey =  Questionnaire(self, **self.survey_dic)

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


def run_experiment(base_path,
                   stim_str,
                   debug,
                   prob_type,
                   commodities,
                   survey_dic):
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.title("Risk and time experiment")
    x = TimeExperiment(root, base_path, stim_str,
                       debug, prob_type, commodities, survey_dic)
    root.mainloop()
    return x





# "/Users/aserwaahWZB/Projects/GUI Code/india other data/Old versions/120915/pkg/lcf survey/details/definitions"

#base_folder = "/Users/aserwaahWZB/Projects/GUI Code/time/india draft/draft 271016/"
base_folder = os.path.dirname(os.path.realpath(__file__))
csv_path = os.path.join(base_folder, "program_files/definitions")

title = "Time preferences survey"
survey_dic = {"csv_path": csv_path,
         "data_path": "",
         "title": title,
         "next_function": ""}

x = run_experiment(base_folder,
                   "full",
                   debug = False,
                   prob_type = "circles",
                   commodities = ("tea", "money"),
                   survey_dic = survey_dic)




