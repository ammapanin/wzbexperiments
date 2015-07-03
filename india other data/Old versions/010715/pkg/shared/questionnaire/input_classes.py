import Tkinter as tk
import tkFont
import operator

class Input(tk.Frame):
    def __init__(self, master,  **kwargs):
        tk.Frame.__init__(self, master, name = kwargs.get("frame_name"))
        
        self.answer_var = tk.StringVar(self)
        self.answer_var.set("x99")
        self.input_vars = [self.answer_var]
        
        #print kwargs
        self.qtype = kwargs.get("type")
        self.options = kwargs.get("options")
        self.label = kwargs.get("label")
        self.conditions = kwargs.get("conditions")
        self.num_list = int(kwargs.get("num_list"))
     
        #self.lab_qobject_dic = kwargs.get("lab_qobject_dic")
        if self.qtype == "check":
            self.check_vars = [tk.StringVar(self) for i in self.options]
            self.input_vars = self.check_vars

        if kwargs.get("qview") == "single":
            self.pack(side = "top", expand = True, anchor = "w")
        elif kwargs.get("qview")[0:5] == "table":
            self.lab_qobject_dic = kwargs.get("lab_qobject_dic")
            print "adding table rows"
            print kwargs.keys()
            self.configure_dependencies()

        if self.num_list == True:
            self.qvars = self.add_number_lists()

        self.clickable_widgets = [self]
            
    def add_number_lists(self):
        if self.qtype == "check" or self.qtype == "choice":
            noptions = len(self.options)
        else:
            noptions = 1

        qvars = [tk.IntVar(self) for i in range(noptions)]
        listvars = [(self, var) + tuple(range(1, 25))
                    for var in qvars]
        nlists = [apply(tk.OptionMenu, loptions) 
                  for loptions in listvars]
        [l.grid(row = i, column = 2) for i, l in enumerate(nlists)]

        self.option_number_dic = dict(zip(self.options, qvars))
        return qvars

    def configure_dependencies(self):
        if self.conditions != None:
            if self.qtype == "check":
                self.apply_check_conditions()
            elif self.qtype != "check":
                self.apply_conditions()
        
    def apply_conditions(self):
        self.answer_var.trace("w", self.control_dependents)
        return None

    def control_dependents(self, name, index, mode):
        conditions = self.conditions
        [self.apply_condition(d, self.answer_var) for d in conditions]
        return None

    def apply_check_conditions(self):
        """Gets customised control functions and applies them for each check var
        """
        #In current form, assumes each check var only has ONE condition
        # CHANGE: make check conditions a list of lists
        conditions = self.conditions
        #print conditions
        cond_vars = zip(conditions, self.check_vars)
        ctrl_funcs = [(v, self.control_checkvars(c, v))
                      for c, v in cond_vars]
        #print ctrl_funcs
        [v.trace("w", cfunc) for v, cfunc in ctrl_funcs]
        return None

    def control_checkvars(self, cond, var):
        """Creates a control function for a single check var
        """
        #left vague to allow conds to be a dictionary
        def control_var(name, index, mode):
            [self.apply_condition(d, var) for d in [cond]]
        return control_var

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

    def add_multiple_rows(self, table, add_row, row_name):
        """"Adds rows when there is a multiple number of row objects

        -Gets the number of rows from the dropdown list number
        -Gets all the existing rows associated with a particular object
        -Each time a row is to be added, checks whether the number 
         of selected rows has changed
        """
        nrow_var = self.option_number_dic.get(row_name)
        nrows = nrow_var.get()
        nchar = len(row_name)
        add_rows = [row_name + " {}".format(i + 1) for i in range(nrows)]
        remove_names = set([r.split("xx")[0] 
                            for r in table.frame.children.keys()
                            if r[0: nchar] == row_name.lower()])
        if add_row == True:
            remove_rows = list((set(remove_names) -
                                set([r.lower() for r in add_rows])))
            [table.add_row(r) for r in add_rows]
            [table.remove_row(r) for r in remove_rows]
        elif add_row == False:
            remove_rows = list(remove_names)
            [table.remove_row(r) for r in remove_rows]
        return None

    def add_single_row(self, table, add_row, row_name):
        if add_row == True:
            table.add_row(row_name)
        elif add_row == False:
            table.remove_row(row_name)
        return None

    def add_row_condition(self, logic_func, qobjects, cdic, answer = ""):
        """Adds either a single or multiple rows
        
        Takes answer as an argument for compatibility with other condition types.
        """
        row_name = cdic.get("row_name")
        if row_name == "get_name":
            print "splitting name"
            row_name = self.winfo_name().split("xx")[0]
        table_lab = cdic.get("labels")[0]
        value = cdic.get("value")
        add_row = logic_func(answer, value)
        qtable = qobjects.get(table_lab).answer

        print table_lab
        print cdic
        #num_list = int(self.options.get("num_list"))

        if self.num_list == True:
            self.add_multiple_rows(qtable, add_row, row_name)
        elif self.num_list == False:
            print qtable, add_row, row_name
            self.add_single_row(qtable, add_row, row_name)
        return None
          
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
                        "equal": operator.eq}

        change_dic = {"applicable": self.notapplicable_condition,
                      "text": self.text_condition,
                      "table": self.add_row_condition}

        dependence_type = cdic.get("type")
        change_func = change_dic.get(dependence_type)

        logic = cdic.get("logic")
        logic_func = operator_dic.get(logic)

        labels = cdic.get("labels")
        qobjects = dict([(l, self.lab_qobject_dic.get(l)) for l in labels])

        answer = self.make_int(var.get())
        change_func(logic_func, qobjects, cdic, answer)
        return None

    def get_answer(self):
        answer =  self.answer_var.get()
        return [(self.label, answer)]

    def been_answered(self):
        answer = self.answer_var.get()
        return answer != "x99"

    def make_inactive(self):
        [w.config(state = "disabled") for w in self.activity_widgets]

    def make_active(self):
        [w.config(state = "normal") for w in self.activity_widgets]

        
class TextBox(Input):
    def __init__(self, master, **kwargs):
        Input.__init__(self, master, **kwargs)

        answer = self.text = tk.Text(self, bg = "snow3", 
                                     height = 10,
                                     width = 25,
                                     wrap = "word")
        answer.grid(sticky = "w", row = 0, column = 0)


class DynamicText(TextBox):
    def __init__(self, master, **kwargs):
        TextBox.__init__(self, master, **kwargs)
        self.options = kwargs

        update = tk.Button(self, 
                           text = "update table", 
                           command = self.update_table)
        update.grid(sticky = "w", row = 1, column = 0)
        
    def update_table(self, event = ""):
        table = self.options.get("table")
        rownames = self.text.get(0.0, "end").split("\n")
        rownames = [r for r in rownames if len(r) > 0] 

        existing = [name[:-1] for name in  table.frame.children.keys()]
        not_existing = set(rownames) - set(existing)
        for n in existing:
            if n not in rownames:         
                table.remove_row(n)
            else:
                pass
        [table.add_row(r) for r in not_existing]

class Slider(Input, object):
    def __init__(self, master, **kwargs):
        Input.__init__(self, master, **kwargs)
        
        self.units = kwargs.get("units").split(",x")
        if self.units != [""]:
            option_lists = [l.split(",x") for l in self.options]
            self.options_dic = dict(zip(self.units, self.options))
            default_unit = self.units[0]
            default_options = self.options_dic.get(default_unit)
            self.make_units(default_unit)
        elif self.units == [""]:
            default_options = ",z".join(self.options)

        self.make_slider(default_options)

    def update_slider(self, name, index, mode):
        unit = self.units_var.get()
        slider_options = self.options_dic.get(unit)

        options = slider_options.split(",z")
        if len(options) == 5:
            start_n, end_n, step_n, start_lab, end_lab = options
        else:
            start_n, end_n, step_n = options
            lab_texts = (start_n, end_n)

        [lab.config(text = txt) for lab, txt in zip(self.labs, lab_texts)]
        self.scale.config(from_ = start_n, to_ = end_n, resolution = step_n)

    def make_units(self, default):
        self.units_var = tk.StringVar(self)
        self.units_var.set(default)
        units = apply(tk.OptionMenu, 
                      ((self, self.units_var) + tuple(self.units)))
        units.grid(row = 0, column = 0)
        self.units_var.trace("w", self.update_slider)

    def make_slider(self, slider_options):
        options = slider_options.split(",z")
         
        if len(options) == 5:
            start_n, end_n, step_n, start_lab, end_lab = options
        else:
            start_n, end_n, step_n = options
            start_lab, end_lab = (start_n, end_n)
        
        slider_frame = tk.Frame(self)
        slider_frame.grid(sticky = "w", row = 0, column = 1)
        scale_font = tkFont.Font(size = 15, weight = "bold")
        self.labs = labs = [tk.Label(slider_frame,
                                     text = txt,
                                     font = scale_font)
                            for txt in (start_lab, end_lab)]
        self.scale = scale = tk.Scale(slider_frame,
                                      length = 200,
                                      from_ = start_n,
                                      to = end_n,
                                      resolution = step_n,
                                      orient = "horizontal",
                                      variable = self.answer_var)

        lab_cols = zip(labs, (0, 2))
        scale.grid(row = 0, column = 1)
        [l.grid(row = 0, column = i, sticky = "sw", padx = 3)
         for l, i in lab_cols]

        self.activity_widgets = [scale]
        self.clickable_widgets.extend([self, slider_frame, scale] + labs)
        return None

    def make_inactive(self):
        super(Slider, self).make_inactive()
        [l.config(fg = "gray") for l in self.labs]

    def make_active(self):
        super(Slider, self).make_active()
        [l.config(fg = "black") for l in self.labs]


class Dropdown(Input):
    def __init__(self, master, **kwargs):
        Input.__init__(self, master, **kwargs)

        self.default_answer = "No selection made"
        self.answer_var.set(self.default_answer)

        drop_texts = (self.default_answer,) + tuple(self.options)
        drop_options = ((self, self.answer_var) + drop_texts)

        dropdown = apply(tk.OptionMenu, drop_options)
        dropdown.grid(sticky = "w", row = 0, column = 0)

    def been_answered(self):
        answer = self.answer_var.get()
        return answer != self.default_answer

class Check(Input):
    def __init__(self, master, **kwargs):
        Input.__init__(self, master, **kwargs)
        self.make_buttons()

        if self.num_list == True:
            self.coordinate_check_numbers()

    def make_buttons(self):
        #self.check_vars = [tk.StringVar(self) for txt in self.options]
        [v.set(0) for v in self.check_vars]
        check_options = zip(self.options, self.check_vars)

        bts = [tk.Checkbutton(self,
                              text = txt,
                              var = var)
               for txt, var in check_options]
        [bt.grid(sticky = "w", row = i, column = 0) for i, bt in enumerate(bts)]
        self.activity_widgets = bts
        self.clickable_widgets.extend([self, bts])

    def coordinate_check_numbers(self):
        def check_var(num_v, check_v):
            def make_check(name, index, mode):
                if num_v.get() > 0:
                    check_v.set(True)
            return make_check
        check_funcs = [(q, check_var(q, c)) 
                       for q, c in zip(self.qvars, self.check_vars)]
        [v.trace("w", cfunc) for v, cfunc in check_funcs]
        return None

    def get_answer(self):
        labels = [self.label + "_{}".format(i)
                  for i, txt in enumerate(self.options)]
        answers = [v.get() for v in self.check_vars]
        return zip(labels, answers)

    def been_answered(self):
        return True


class Choice(Input):
    def __init__(self, master, **kwargs):
        Input.__init__(self, master, **kwargs)

        bts = [tk.Radiobutton(self,
                              text = txt,
                              var = self.answer_var,
                              value = txt)
               for txt in self.options]
        [bt.grid(sticky = "w", row = i, column = 0) for i, bt in enumerate(bts)]
        self.activity_widgets = bts
        self.clickable_widgets.extend([self, bts])


class Entry(Input):
    def __init__(self, master, **kwargs):
        Input.__init__(self, master, **kwargs)
        entry = tk.Entry(self,
                         textvariable = self.answer_var,
                         show = " ")
        entry.grid(sticky = "w", row = 0, column = 0)

        self.ever_answered = 0

        def clear_entry(name, index, mode):
            self.ever_answered += 1
            if self.ever_answered > 1:
                pass
            else:
                entry.delete(0, "end")
                entry.config(show = "")
        self.answer_var.trace("w", clear_entry)
        self.activity_widgets = [entry]
        self.clickable_widgets.extend([self, entry])
