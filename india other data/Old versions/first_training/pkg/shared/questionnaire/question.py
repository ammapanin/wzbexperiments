import csv
import os
import Tkinter as tk
import tkFont
import operator

import answer_classes as answers

class Question(tk.Frame):
    def __init__(self, **kwargs):
        tk.Frame.__init__(self,
                          master = kwargs.get("tab"),
                          takefocus = True,
                          highlightthickness = 4,
                          highlightcolor = "green")
        self.pack(fill = "x", expand = True, anchor = "w",
                  pady = 5, padx = 2)

        self.options = kwargs
        self.qidx = kwargs.get("qidx")
        self.qlabel = kwargs.get("qlabel")
        
        self.make_control_vars()
        self.qlab = self.make_text_label()
        self.answer = self.make_inputs()
    
    def apply_conditions(self):
        self.answer.lab_qobject_dic = self.lab_object
        if self.options.get("qview") == "single":
            self.answer.configure_dependencies()
        if self.options.get("qview") == "table":
            for q in self.answer.qobjects:
                q["lab_qobject_dic"] = self.lab_object
        return None

    def make_inputs(self):
        qview = self.options.get("qview")
        if qview != "table":
            answer = self.make_answer_box()
        elif qview == "table":
            answer = self.make_table_box() 
        return answer

    def make_control_vars(self):
        self.is_active = tk.BooleanVar(self)
        self.is_current = tk.BooleanVar(self)
        self.is_applicable = tk.BooleanVar(self)

        self.is_current.set(False)
        self.is_applicable.set(False)
        return None

    def make_text_label(self):
        title_font = tkFont.Font(size = 18)
        lab_text = self.options.get("question_text")
        lab_num = self.options.get("qidx")

        qtext = "{}. {}".format(lab_num, lab_text)
        lab = tk.Label(self,
                       text = qtext,
                       font = title_font)
        lab.pack(side = "top", expand = True, anchor = "w")
        return lab

    def make_answer_box(self):
        answer_frame = tk.Frame(self)
        answer_frame.pack(side = "top", anchor = "w",
                          expand = True, fill = "both")
        
        answer_class = answers.classes.get(self.options.get("type"))
        answer = answer_class(answer_frame, **self.options)
        return answer

    def make_table_box(self):
        answer_frame = tk.Frame(self)
        answer_frame.pack(side = "top", anchor = "w",
                          expand = True, fill = "both")

        qlist = self.options.get("questions")
        answer = answers.DynamicTable(answer_frame, qlist)
        return answer

    def been_answered(self):
        answered = self.answer.been_answered()
        q = self.options.get("qidx")
        return q, answered

    def make_current(self):
        q_current_lab = self.options.get("current_lab_var")
        q_latest_lab = self.options.get("latest_lab_var")

        if self.is_active.get() == True:
            self.focus_set()
            q_current_lab.set(self.qlabel)
            self.is_current.set(True)

            latest_lab = q_latest_lab.get()
            current_idx = self.lab_idx.get(self.qlabel)
            latest_idx = self.lab_idx.get(latest_lab)

            if current_idx > latest_idx:
                q_latest_lab.set(self.qlabel)
            elif current_idx <= latest_idx:
                pass
        elif self.is_active.get == False:
            pass
        return None

    def make_inactive(self):
        self.answer.make_inactive()
        self.qlab.config(fg = "gray")
        self.is_active.set(False)
        return None

    def make_active(self):
        self.answer.make_active()
        self.qlab.config(fg = "black")
        self.is_active.set(True)
        return None

    def make_notapplicable(self):
        labs, indexes = zip(*self.qcycle)
        try:
            idx = labs.index(self.qlabel)
            qobj = self.lab_object.get(self.qlabel)
            qobj.make_inactive()
            self.qcycle.pop(idx)
        except ValueError:
            pass
        return None

    def make_applicable(self):
        qlab_idx = (self.qlabel, self.qidx)
        if qlab_idx not in self.qcycle:
            self.qcycle.append(qlab_idx)
        self.qcycle.sort(key = lambda x: x[1])
        return None

    def change_text(self, update_text):
        text_0 = self.options.get("question_text")
        self.qlab.config(text = text_0.format(update_text))
        return None

  


