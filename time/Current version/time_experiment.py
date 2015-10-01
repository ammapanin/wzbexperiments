import Tkinter as tk
import tkFont
import tkMessageBox
import os
import csv

from program_files.Squarepie import ChoiceScreen

class TimeExperiment(tk.Frame):
    def __init__(self, master, stimuli_path, debug):
        tk.Frame.__init__(self, master)
        self.pack(side = "top", fill = "both", expand = True)

        self.stimuli_path = stimuli_path
        if debug == True:
            self.debug_segue = False
            self.start_experiment("practice", end_func = False)
        else:
            self.deskvar = tk.IntVar()
            self.deskvar.set("")
            self.make_frames()
            self.debug_segue = self.segue_experiment

    def make_frames(self):
        titlefont = tkFont.Font(size = 20, weight = "bold")
        title = tk.Label(self, 
                         text = ("Welcome to the experiment. \n"
                                 "Please enter your desk number, "
                                 "then press 'Enter' to continue"),
                         justify = "left", font = titlefont)
        entry_box = tk.Entry(self, textvariable = self.deskvar)
        [w.pack(side = "top", anchor = "w", padx = 10, pady = 10) 
         for w in (title, entry_box)]

        def next_step(event):
            title.destroy()
            entry_box.destroy()
            self.show_instructions()
            return None
        entry_box.bind("<Return>", next_step)

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
            self.start_experiment("practice", self.debug_segue)
            return None

        ok_bt.config(command = next_step)
        ok_bt.pack(side = "top", anchor = "w", padx = 10)

    def start_experiment(self, mode, end_func):
        stimuli = self.get_stimuli(mode)
        self.choices = ChoiceScreen(self, stimuli, mode, end_func)
        return None

    def segue_experiment(self):
        tkMessageBox.showinfo("", ("You will now begin the real experiment. "
                                   "Please ask your experimenter if anything "
                                   "remains unclear."))
        self.choices.pack_forget()
        self.start_experiment("full", end_func = False)
        return None

    def get_stimuli(self, mode):
        stimulipath = self.stimuli_path + "_{}.csv".format(mode)
        with open(stimulipath, "rb") as sfile:
            scsv = csv.reader(sfile)
            fnames = scsv.next()
            ldic = [dict(zip(fnames, line)) for line in scsv]
            lines = enumerate(ldic, 1)
        return lines, len(ldic)

def run_experiment(stimuli_path, debug):
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.title("Risk and time experiment")
    x = TimeExperiment(root, stimuli_path, debug)
    root.mainloop()
    return x


stimuli_path = csvpath = os.path.join(os.getcwd(), "program_files", "stimuli")
x = run_experiment(stimuli_path, debug = False)
