import csv
import os
import Tkinter as tk
import tkFont
import tkFileDialog

from draggable import DraggableList
from create_questionnaire import DefineQuestion


class ScrollableFrame(tk.Frame):
    def __init__(self, master, label = False):
        tk.Frame.__init__(self, master)

        self.canvas = tk.Canvas(self, bg = "red")
        if label == True:
            self.frame = tk.LabelFrame(self.canvas)
        else:
            self.frame = tk.Frame(self.canvas)

        vsb = tk.Scrollbar(self, command = self.canvas.yview)
        self.canvas.configure(yscrollcommand = vsb.set)

        vsb.pack(side = "right", fill = "y")

        self.canvas.create_window((5,5),
                                  window = self.frame,
                                  anchor = "nw",
                                  tags = "frame")

        self.frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.pack(side = "left", fill = "both", expand = True)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
        return None

    def on_canvas_configure(self, event):
        self.canvas.itemconfig("frame",
                               width = event.width)
        return None

class AddQuestions(tk.Frame):

    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master)
        self.pack(side = "top", fill = "both", expand = True)

        rbase, qbasic, qlist = self.make_frames()

        self.lab_list = self.make_qlist(qlist)

        self.qframe = rbase.frame

        self.make_details(qbasic)

    def make_frames(self):
        lbase = tk.Frame(self)
        rbase = ScrollableFrame(self)

        lbase.pack(side = "left", fill = "y", expand = False)
        rbase.pack(side = "left", fill = "both", expand = True)

        qbasic = tk.Frame(lbase)
        qlist = tk.LabelFrame(lbase)
        #qlist =  ScrollableFrame(lbase, label = True)

        qbasic.pack(side = "top", anchor = "nw")
        qlist.pack(side = "top", fill = "y", expand = True)
        return rbase, qbasic, qlist

    def make_qlist(self, master):
        lab_font = tkFont.Font(weight = "bold", size = 14)
        lab_title = tk.Label(master,
                             text = "List of questions",
                             font = lab_font)
        lab_title.pack(side = "top", anchor = "nw")
        lab_list = DraggableList(master)
        return lab_list.canvas

    def save_properties(self):
        print "something"
        tabs = self.tab_list.get("1.0", "end").split("\n")
        tabs = [t for t in tabs if len(t) > 0]
        self.lab_list.update_tabs(tabs)
        DefineQuestion.tabs = tuple(tabs)
        print "added"
        return None

    def add_question(self):
        DefineQuestion(self.qframe, self.lab_list.create_label)
        return(None)

    def make_details(self, master):
        title_font = tkFont.Font(master, weight = "bold", size = 14)
        lab_texts = ("Questionnaire title",
                     "Questionnaire subsections",
                     "Path to csv file",
                     "Path do data file")
        labels = [tk.Label(master, text = txt, font = title_font)
                  for txt in lab_texts]
        title, tab_title, csv_title, data_title = labels

        title_var = tk.StringVar(master)
        title_entry = tk.Entry(master, textvariable = title_var)
        self.tab_list = tabs = tk.Text(master,
                                       width = 20, height = 5, bg = "snow3")

        path_texts = ("please select csv path",
                      "please select data path")
        text_vars = [tk.StringVar(master) for i in path_texts]
        [v.set(i) for v, i in zip(text_vars, path_texts)]
        csv_var, data_var = text_vars
        path_font = tkFont.Font(master, size = 9, slant = "italic")
        path_labels = [tk.Label(master, textvariable = v, font = path_font)
                       for v in text_vars]
        csv_lab, data_lab = path_labels

        def get_csvpath(var):
            path = tkFileDialog.askdirectory()
            var.set(path)
            return None

        csv_bt, data_bt = [tk.Button(master, text = "...",
                                     command = lambda x = var: get_csvpath(x))
                           for var in text_vars]

        ctrl_texts = ("save properties",
                      "Add question")
        ctrl_cmds = (self.save_properties,
                     self.add_question)
        save_bt, add_bt = [tk.Button(master, text = txt, command = cmd)
                           for txt, cmd in zip(ctrl_texts, ctrl_cmds)]

        title.grid(row = 0, column = 0, columnspan = 2, sticky = "nw")
        title_entry.grid(row = 1, column = 0, columnspan = 2, sticky = "nw")

        tab_title.grid(row = 2, column = 0, sticky = "nw")
        tabs.grid(row = 3, column = 0, sticky = "nw")

        csv_title.grid(row = 4, column = 0, columnspan = 2, sticky = "nw")
        csv_lab.grid(row = 5, column = 0, sticky = "nw")
        csv_bt.grid(row = 5, column = 1, sticky = "nw")

        data_title.grid(row = 6, column = 0, columnspan = 2, sticky = "nw")
        data_lab.grid(row = 7, column = 0, sticky = "nw")
        data_bt.grid(row = 7, column = 1, sticky = "nw")

        save_bt.grid(row = 8, column = 0, sticky = "nw")
        add_bt.grid(row = 8, column = 1, sticky = "nw")
        return "fun stuff"




def test_questionnaire_definer():
    reload(draggable)
#    reload(
    root = tk.Tk()
    simon = AddQuestions(root)
    return simon
