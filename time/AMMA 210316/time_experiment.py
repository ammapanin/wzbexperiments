import Tkinter as tk
import tkFont
import tkMessageBox
import os
import csv
import random

from program_files.Choicescreen import ChoiceScreen

class TimeExperiment(tk.Frame):
    def __init__(self, master, stimuli_path, debug, prob_type):
        tk.Frame.__init__(self, master)
        self.pack(side = "top", fill = "both", expand = True)

        self.stimuli_path = stimuli_path
        if debug == True:
            self.debug_segue = False
            self.start_experiment("practice",
                                  end_func = False,
                                  prob_type = prob_type)
        else:
            self.deskvar = tk.IntVar()
            self.deskvar.set("")
            self.make_frames()
            self.debug_segue = self.segue_experiment
            self.prob_type = prob_type

    def make_frames(self):
        titlefont = tkFont.Font(size = 20, weight = "bold")
        title = tk.Label(self,
                         text = ("Welcome to the experiment. \n"
                                 "Please enter your desk number, "
                                 "then press 'Enter' to continue"),
                         justify = "left", font = titlefont)

        self.idvars = (tk.StringVar(self), tk.IntVar(self))
        deskvar, sessionvar = self.idvars

        login = tk.Frame(self)

        desks = ("Nyongi", "Friederike", "Felix", "Emmanuel", "Amma")
        sessions = tuple(range(0, 28))
        desk = apply(tk.OptionMenu, (login, deskvar) + tuple(desks))
        session = apply(tk.OptionMenu, (login, sessionvar) + tuple(sessions))
        labs = [tk.Label(login, text = txt) for txt in ("Desk", "Session")]
        ok = tk.Button(login, text = "OK")

        big_widgets =  enumerate((desk, session, ok))
        [w.grid(row = i, column = 0, sticky = "w") for i, w in enumerate(labs)]
        [w.grid(row = i, column = 1, sticky = "w") for i, w in big_widgets]

        [w.pack(side = "top", anchor = "w", padx = 10, pady = 10)
         for w in (title, login)]

        def next_step():
            title.destroy()
            login.destroy()
            self.show_instructions()
            return None
        ok.config(command = next_step)
        #entry_box.bind("<Return>", next_step)

    def show_instructions(self):
        instructionfont = tkFont.Font(size = 20, weight = "bold")
        instruction_text = ("Now please turn your focus to the experimenter, "
                            "who will go through the experiment with you. "
                            "You have a copy of the instructions at your desk. "
                            "Please feel free to return to these or ask a "
                            "question at any point during the experiment.")

        iframe = tk.Frame(self)
        iframe.pack(side = "top", fill = "both", expand = False, anchor = "w")
        instructions = tk.Label(iframe,
                                text = instruction_text,
                                font = instructionfont,
                                wrap = 1000,
                                justify = "left")
        instructions.pack(side = "top",
                          expand = False,
                          anchor = "w",
                          pady = 10,
                          padx = 10)
        ok_bt = tk.Button(iframe,
                          text = "Begin practice")
        def next_step():
            iframe.destroy()
            self.start_experiment("practice",
                                  self.debug_segue,
                                  self.prob_type)
            return None

        ok_bt.config(command = next_step)
        ok_bt.pack(side = "top", anchor = "w", padx = 10)

    def start_experiment(self, mode, end_func, prob_type):
        stimuli = self.get_stimuli(mode)
        idvars = tuple([v.get() for v in self.idvars])
        self.choices = ChoiceScreen(self, stimuli, mode, end_func, idvars,
                                    prob_type)
        return None

    def segue_experiment(self):
        tkMessageBox.showinfo("", ("You will now begin the real experiment. "
                                   "Please ask your experimenter if anything "
                                   "remains unclear."))
        self.choices.pack_forget()
        self.start_experiment("full",
                              end_func = False,
                              prob_type = self.prob_type)
        return None

    def get_stimuli(self, mode):
        stimulipath = self.stimuli_path + "_{}.csv".format(mode)
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
            [random.shuffle(block) for block in blocks]
            random.shuffle(blocks)
            stimuli = [stim for b in blocks for stim in b]
            lines = enumerate(stimuli, 1)
        return lines, len(stimuli)

def run_experiment(stimuli_path, debug, prob_type):
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.title("Risk and time experiment")
    x = TimeExperiment(root, stimuli_path, debug, prob_type)
    root.mainloop()
    return x


stimuli_path = csvpath = os.path.join(os.getcwd(), "program_files", "stimuli")
x = run_experiment(stimuli_path, debug = False, prob_type = "pie")

