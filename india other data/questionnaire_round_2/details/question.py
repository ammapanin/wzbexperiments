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
        qview = kwargs.get("qview")


        self.make_control_vars()
        self.qlab = self.make_text_label()

        if qview != "table":
            self.answer = self.make_answer_box()
        elif qview == "table":
            self.answer = self.make_table_box()

        if len(self.options["conditions"]) > 0:
            q_class = self.options.get("type")
            if q_class != "check":
                self.answer_var.trace("w", self.control_dependents)
            elif q_class == "check":
                conditions = self.options.get("conditions")
                check_vars =  self.answer.check_vars
                cond_vars = zip(conditions, check_vars)
                ctrl_funcs = [(v, self.control_checkvars(c, v))
                              for c, v in cond_vars]
                [v.trace("w", cfunc) for v, cfunc in ctrl_funcs]

        #self.make_inactive()


    def make_control_vars(self):
        self.answer_var = tk.StringVar(self)
        self.answer_var.set("x99")
        self.options["answer_var"] = self.answer_var

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

    def control_checkvars(self, cond, var):
        #left vague to allow conds to be a dictionary
        def control_var(name, index, mode):
            [self.apply_condition(d, var) for d in [cond]]
        return control_var

    #[c.trace(control_dependents) for c in self.answer.check_vars]
    def control_dependents(self, name, index, mode):
        conditions = self.options.get("conditions")
        q_class = self.options.get("type")

        if q_class != "check":
            [self.apply_condition(d, self.answer_var) for d in conditions]
        elif q_class == "check":
            pass
            #check_vars = self.answer.check_vars
            #cond_vars = zip(conditions, check_vars)
            #[self.apply_condition(d, v) for d, v in cond_vars]
        return None

    def notapplicable_condition(self, logic_func, qobjects, cdic, answer):
        """Makes dependent questions applicaple or non applicable
        """

        if self.options.get("type") != "check":
            comparison = cdic.get("value")
        else:
            comparison = True

        make_na = logic_func(answer, comparison)
        if make_na == True:
            [q.make_notapplicable() for q in qobjects]
        elif make_na == False:
            for q in qobjects:
                if q.is_applicable.get() == True:
                    pass
                elif q.is_applicable.get() == False:
                    q.make_applicable()
        return None

    def add_row_condition(self, logic_func, qobjects, cdic, answer):
        row_name = cdic.get("value")
        add_row = logic_func(answer, True)
        qtable = qobjects[0].answer
        if add_row == True:
            qtable.add_row(row_name)
        if add_row == False:
            qtable.remove_row(row_name)


    def text_condition(self, logic_func, qobjects, cdic, answer):
        """Updates all question text labels that depend on a certain condition

        First checks if condition is a test of equality.
        If so, the dependent values are stored in a dictionary {answer: value}

        Otherwise, there is a geq/leq comparison.
        Assumes only 2 possible outcomes.
        If the function returns True, take the first outcome
        """

        value = cdic.get("value")
        texts = cdic.get("texts")

        if logic_func == operator.eq:
            values = [self.make_int(v) for v in value.split(",x")]
            value_dic = dict(zip(values, texts))
            update_text = value_dic.get(answer)
        elif logic_func != operator.eq:
            use_default = logic_func(answer, self.make_int(value))
            if use_default == True:
                update_text = texts[0]
            elif use_default == False:
                update_text = texts[1]

        [q.change_text(update_text) for q in qobjects]
        return None

    def make_int(self, string):
        try:
            val = int(string)
        except ValueError:
            val = string
        return val

    def apply_condition(self, cdic, var):
        """Applies one single condition to the answer_var

        cdic containes the following:
        logic: "qeq", "leq", "greater", "less", "equal"
        value: comparison value
        labels: dependent labels
        """

        operator_dic = {"leq": operator.le,
                        "less": operator.lt,
                        "geq": operator.ge,
                        "greater": operator.gt,
                        "equal":operator.eq}

        change_dic = {"applicable": self.notapplicable_condition,
                      "text": self.text_condition,
                      "table": self.add_row_condition}

        dependence_type = cdic.get("type")
        change_func = change_dic.get(dependence_type)

        logic = cdic.get("logic")
        logic_func = operator_dic.get(logic)

        labels = cdic.get("labels")
        qobjects = [self.lab_object.get(l) for l in labels]

        answer = self.make_int(var.get())
        change_func(logic_func, qobjects, cdic, answer)
        return None


