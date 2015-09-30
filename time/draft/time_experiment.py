import Tkinter as tk
import tkMessageBox
import os
import csv

from Squarepie import ChoiceScreen

class TimeExperiment(tk.Frame):
    def __init__(self, master, stimuli_path, debug):
        tk.Frame.__init__(self, master)
        self.pack(side = "top", fill = "both", expand = True)

        self.stimuli_path = stimuli_path
        if debug == True:
            self.start_experiment("practice", end_func = False)
        else:
            self.deskvar = tk.IntVar()
            self.deskvar.set("")
            self.make_frames()


    def make_frames(self):
        title = tk.Label(self, text = ("Please enter your desk number, "
                                "then press 'Enter' to continue"))
        title.pack(side = "top")
        entry_box = tk.Entry(self, textvariable = self.deskvar)
        entry_box.pack(side = "top")
        def next_step(event):
            title.destroy()
            entry_box.destroy()
            self.show_instructions()
            return None
        entry_box.bind("<Return>", next_step)

    def show_instructions(self):
        iframe = tk.Frame(self)

        icanvas = tk.Canvas(self)
        icanvas.create_window(0, 0, window = iframe, anchor = "sw")
        iframe.pack(side = "top", fill = "both", expand = True)
        icanvas.pack(side = "top", fill = "both", expand = True)
        instructions = tk.Label(iframe, text = "Person, place, or thing")
        instructions.pack(side = "top", fill = "both", expand = True)
        ok_bt = tk.Button(iframe,
                          text = "Begin practice")
        def next_step():
            iframe.destroy()
            icanvas.destroy()
            self.start_experiment("practice", end_func = False)
            #self.start_experiment("practice", self.segue_experiment)
            return None
        ok_bt.config(command = next_step)
        ok_bt.pack(side = "bottom")

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
    x = TimeExperiment(root, stimuli_path, debug)
    return x


stimuli_path = csvpath = os.path.join(os.getcwd(), "stimuli")

x = run_experiment(stimuli_path, debug = False)
