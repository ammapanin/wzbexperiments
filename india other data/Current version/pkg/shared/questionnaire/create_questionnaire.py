import csv
import os
import Tkinter as tk
import tkFont


class DefineQuestion(tk.LabelFrame):

    def __init__(self, master, label_func):
        tk.LabelFrame.__init__(self, master)
        self.pack(side = "top", fill = "both")

        self.add_label = label_func
        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(side = "top", fill = "both")

        basic_frame = tk.LabelFrame(self.entry_frame)
        basic_frame.pack(side = "top", fill = "x", anchor = "w")

        label_texts = ("Please enter question text",
                       "Variable label",
                       "Type of question",
                       "Please enter the question options",
                       "Tab where the question will appear")

        labs = [tk.Label(basic_frame, text = l)
                for l in label_texts]
        qtext_lab, qlabel_lab, qtype_lab, qoptions_lab, qtab_lab = labs


        self.qvars = [tk.StringVar(self) for i in range(0, 4)]
        text_var, label_var, type_var, tab_var = self.qvars

        qtypes = ("choice", "entry", "slider", "check", "dropdown")
        qtype_options = (basic_frame, type_var) + qtypes
        qtab_options = (basic_frame, tab_var) + DefineQuestion.tabs

        qtext = tk.Entry(basic_frame, textvariable = text_var, width = 80)
        qlabel = tk.Entry(basic_frame, textvariable = label_var)
        qtype = apply(tk.OptionMenu, qtype_options)
        qtab = apply(tk.OptionMenu, qtab_options)
        qoptions = tk.Text(basic_frame, height = 8, width = 23, bg = "snow3")
        self.qoptions = qoptions

        qtext_lab.grid(sticky = "w", row = 0, column = 1, columnspan = 4)
        qtext.grid(sticky = "w", row = 1, column = 1, columnspan = 4)

        qlabel_lab.grid(sticky = "w", row = 2, column = 1)
        qlabel.grid(sticky = "w", row = 2, column = 2)

        qtype_lab.grid(sticky = "e", row = 2, column = 3)
        qtype.grid(sticky = "e", row = 2, column = 4)

        qoptions_lab.grid(sticky = "nw", row = 3, column = 1)
        qoptions.grid(sticky = "w", row = 3, column = 2)

        qtab_lab.grid(sticky = "nw", row = 3, column = 3)
        qtab.grid(sticky = "ne", row = 3, column = 4)

        entry_bt_frame = tk.Frame(self.entry_frame)
        entry_bt_frame.pack(side = "bottom", anchor = "e")

        self.min_frame = tk.Frame(self)

        min_label = tk.Label(self.min_frame, textvariable = text_var)
        min_bt = tk.Button(entry_bt_frame, text = "-",
                           command = self.minimise)
        max_bt = tk.Button(self.min_frame, text = "+",
                           command = self.maximise)

        min_label.pack(side = "left")
        max_bt.pack(side = "right")


        update_bt = tk.Button(basic_frame,
                            text = "Update question",
                            command = self.update_info)
        add_bt = tk.Button(basic_frame,
                           text = "Add a condition",
                           command = self.add_condition)

        save_bt = tk.Button(entry_bt_frame,
                            text = "Save question",
                            command = self.save_info)

        update_bt.grid(row = 4, column = 1, sticky = "w")
        add_bt.grid(row = 5, column = 1, sticky = "w")
        min_bt.pack(side = "right")
        save_bt.pack(side = "right", anchor = "w")

        self.qdic = dict()

    def get_info(self):
        o_list = self.qoptions.get("1.0", "end").split("\n")
        options = ",x".join(o_list)
        infos = [v.get() for v in self.qvars] + [options]
        return infos

    def update_info(self):
        text, label, qtype, tab, options = self.get_info()
        self.qdic["question_text"] = text
        self.qdic["label"] = label
        self.qdic["tab"] = tab
        self.qdic["qtype"] = qtype
        self.qdic["options"] = options

        self.add_label(tab = tab, text = label)

    def add_condition(self):
        c = Condition(self.entry_frame, **self.qdic)
        return c

    def save_info(self):
        self.update_info()

        i_strings = ("question_text", "label", "tab", "qtype", "options")
        infos = [self.qdic.get(s) for s in i_strings]
        qtext, qtype, label, tab, options = infos

        conds = [list(c.get_info()) for c in Condition.conditions]
        [infos.extend(c) for c in conds]

        print infos
        return infos

    def minimise(self):
        self.entry_frame.pack_forget()
        self.min_frame.pack(side = "top", anchor = "w")

    def maximise(self):
        self.min_frame.pack_forget()
        self.entry_frame.pack(side = "top", anchor = "w")


class Condition(tk.LabelFrame):
    conditions = list()
    labels = list()

    def __init__(self, master, **kwargs):
        tk.LabelFrame.__init__(self, master)
        self.pack(side = "top", fill = "x", anchor = "w")
        self.options = kwargs
        self.options_list = tuple(kwargs.get("options").split(",x"))

        if_lab = tk.Label(self, text = "If")
        a_lab, a_vars = self.make_answer_lab()
        logic_lab, logic_var, self.logic_dic = self.make_logic_lab()
        value_lab, value_var = self.make_value_options()

        hide_var = tk.StringVar(self)
        hide_lab = apply(tk.OptionMenu, (self, hide_var, "hide"))

        labels_list = self.make_labels_list()

        hide_bt = tk.Button(self, text = "X", command = self.hide)

        widgets = (if_lab, a_lab, logic_lab,
                   value_lab, hide_lab, labels_list)

        [w.pack(side = "left") for w in widgets]
        hide_bt.pack(side = "right")

        self.cond_vars = (logic_var, hide_var, value_var)
        Condition.conditions.append(self)

    def make_answer_lab(self):
        qtype = self.options.get("qtype")
        if qtype == "check":
            check_options = [(txt, tk.StringVar(self))
                             for txt in self.options_list]
            a_frame = tk.Frame(self)
            options = [tk.Checkbutton(a_frame,
                                      text = txt,
                                      variable = v)
                       for txt, v in check_options]
            [o.pack(side = "top") for o in options]
            a_lab = a_frame
        elif qtype != "check":
            a_lab = tk.Label(self, text = "answer")
            dummy_answer = tk.StringVar(self)
            dummy_answer.set(None)
            check_options = [("answer", dummy_answer)]
        return a_lab, dummy_answer

    def make_value_options(self):
        qtype = self.options.get("qtype")
        value_var = tk.StringVar(self)

        if qtype == "entry":
            value_lab = tk.Entry(self)
        if qtype != "entry":
            if qtype == "check":
                values = ("True", "False")
            if qtype != "check":

                values = self.options_list

            value_lab = apply(tk.OptionMenu, (self, value_var) + values)
        return value_lab, value_var

    def make_logic_lab(self):
        logic = {"equals": "equal",
                 "greater than": "greater",
                 "less than": "less",
                 "greater than or equal to": "geq",
                 "less than or equal to": "leq"}

        logic_string = tuple(logic.keys())
        logic_var = tk.StringVar(self)
        logic_lab = apply(tk.OptionMenu, (self, logic_var) + logic_string)
        return logic_lab, logic_var, logic

    def make_labels_list(self):
        labels_list = tk.Listbox(self, height = 4,
                                 exportselection = False,
                                 selectmode = "multiple")
        for i in Condition.labels:
            labels_list.insert("end", i)
        self.lab_list = labels_list
        return labels_list

    def get_info(self):
        logic_string, cond_type, value = [v.get() for v  in self.cond_vars]
        lidx = self.lab_list.curselection()
        labels = ",x".join([self.lab_list.get(idx) for idx in lidx])

        logic = self.logic_dic.get(logic_string)
        return logic, cond_type, value, labels

    def hide(self):
        self.pack_forget()
        clist = Condition.conditions
        self_idx = clist.index(self)
        condition = clist.pop(self_idx)
        del condition

def input_test():
    root = tk.Tk()
    DefineQuestion.tabs = ("first", "second", "third")
    prog = DefineQuestion(root, "bob")
    return prog

#bob = input_test()
