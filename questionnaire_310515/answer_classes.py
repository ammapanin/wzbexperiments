import Tkinter as tk
import tkFont


class Answer(tk.Frame):
    def __init__(self, master,  **kwargs):
        tk.Frame.__init__(self, master, name = kwargs.get("frame_name"))

        if kwargs.get("qview") == "single":
            self.pack(side = "top", expand = True, anchor = "w")

        self.answer_var = tk.StringVar(self)
        self.answer_var.set("x99")
        self.options = kwargs.get("options")
        self.label = kwargs.get("label")

        self.clickable_widgets = [self]

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

class TextBox(Answer):
    def __init__(self, master, **kwargs):
        Answer.__init__(self, master, **kwargs)

        answer = self.text = tk.Text(self, bg = "snow3", 
                                     height = 10,
                                     width = 25,
                                     wrap = "word")
        answer.pack(side = "top", anchor = "w") 

class DynamicText(TextBox):
    def __init__(self, master, **kwargs):
        TextBox.__init__(self, master, **kwargs)
        self.options = kwargs

        update = tk.Button(self, text = "update table", command = self.update_table)
        update.pack(side = "top")
        
    def update_table(self, event = ""):
        table = self.options.get("table")
        rownames = self.text.get(0.0, "end").split("\n")
        rownames = [r for r in rownames if len(r) > 0] 

        existing = [name[:-1] for name in  table.frame.children.keys()]
        print "existing", existing
        not_existing = set(rownames) - set(existing)
        print "rows to be added", not_existing
        for n in existing:
            if n not in rownames:         
                table.remove_row(n)
            else:
                pass
        [table.add_row(r) for r in not_existing]

class Slider(Answer, object):
    def __init__(self, master, **kwargs):
        Answer.__init__(self, master, **kwargs)
        start_n, end_n, step_n = self.options

        frame = tk.Frame(self)
        frame.pack(side = "top", anchor = "w")

        scale_font = tkFont.Font(size = 18, weight = "bold")
        labs = [tk.Label(frame,
                         text = txt,
                         font = scale_font)
                for txt in (start_n, end_n)]
        self.labs = labs
        lab_cols = zip(labs, (0, 2))

        scale = tk.Scale(frame,
                         from_ = start_n,
                         to = end_n,
                         resolution = step_n,
                         orient = "horizontal",
                         variable = self.answer_var)

        scale.grid(row = 0, column = 1)
        [l.grid(row = 0, column = i, sticky = "sw", padx = 3)
         for l, i in lab_cols]

        self.activity_widgets = [scale]
        self.clickable_widgets.extend([self, frame, scale] + self.labs)

    def make_inactive(self):
        super(Slider, self).make_inactive()
        [l.config(fg = "gray") for l in self.labs]

    def make_active(self):
        super(Slider, self).make_active()
        [l.config(fg = "black") for l in self.labs]



class Dropdown(Answer):
    def __init__(self, master, **kwargs):
        Answer.__init__(self, master, **kwargs)

        self.default_answer = "No selection made"
        self.answer_var.set(self.default_answer)

        drop_texts = (self.default_answer,) + tuple(self.options)
        drop_options = ((self, self.answer_var) + drop_texts)

        dropdown = apply(tk.OptionMenu, drop_options)
        dropdown.pack(side = "top", anchor = "w")
        self.activity_widgets = [dropdown]
        self.clickable_widgets.extend([self, dropdown])

    def been_answered(self):
        answer = self.answer_var.get()
        return answer != self.default_answer

class Check(Answer):
    def __init__(self, master, **kwargs):
        Answer.__init__(self, master, **kwargs)

        self.check_vars = [tk.StringVar(self) for txt in self.options]
        [v.set(0) for v in self.check_vars]
        check_options = zip(self.options, self.check_vars)

        bts = [tk.Checkbutton(self,
                                   text = txt,
                                   var = var)
                    for txt, var in check_options]
        [bt.pack(side = "top", anchor = "w") for bt in bts]
        self.activity_widgets = bts
        self.clickable_widgets.extend([self, bts])

    def get_answer(self):
        labels = [self.label + "_{}".format(i)
                  for i, txt in enumerate(self.options)]
        answers = [v.get() for v in self.check_vars]
        return zip(labels, answers)

    def been_answered(self):
        return True


class Choice(Answer):
    def __init__(self, master, **kwargs):
        Answer.__init__(self, master, **kwargs)

        bts = [tk.Radiobutton(self,
                              text = txt,
                              var = self.answer_var,
                              value = txt)
               for txt in self.options]
        [bt.pack(side = "top", anchor = "w") for bt in bts]
        self.activity_widgets = bts
        self.clickable_widgets.extend([self, bts])


class Entry(Answer):
    def __init__(self, master, **kwargs):
        Answer.__init__(self, master, **kwargs)
        entry = tk.Entry(self,
                         textvariable = self.answer_var,
                         show = " ")
        entry.pack(side = "top", anchor = "w", pady = 2)

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


class DynamicTable(tk.LabelFrame):
    def __init__(self, master, table_objects):
        tk.LabelFrame.__init__(self, master, width = 10000)
        self.pack(fill = "both", expand = True)

        master.columnconfigure(0, weight = 1)
        master.rowconfigure(0, weight = 1)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)

        self.frame = self.make_scrollable_frame()

        self.qobjects = table_objects
        self.col_names = [q.get("question_text") for q in table_objects]

        self.make_headers(self.col_names)
        self.nrows = tk.IntVar(self.frame)
        self.nrows.set(1)
        self.rows = list()


    def make_scrollable_frame(self):
        self.canvas = tk.Canvas(self, bg = "red",
                                width = 1500,
                                height = 300)
        frame = tk.LabelFrame(self.canvas)
        frame.config(bg = "dim gray")

        yscroll = tk.Scrollbar(self, command = self.canvas.yview)
        xscroll = tk.Scrollbar(self,
                               orient = "horizontal",
                               command = self.canvas.xview)



        self.canvas.config(yscrollcommand = yscroll.set,
                           xscrollcommand = xscroll.set)

        frame_idx = self.canvas.create_window((5, 5,),
                                              window = frame,
                                              anchor = "nw",
                                              tags = "frame")

        def on_frame_configure(event):
            self.canvas.configure(scrollregion = self.canvas.bbox("all"))
            return None

        def on_canvas_configure(event):
            self.canvas.itemconfig("frame",
                                   width = event.width,
                                   height = event.height)
            return None

        self.canvas.bind("<Configure>", on_canvas_configure)
        #frame.bind("<Configure>", on_frame_configure)

        self.canvas.grid(row = 0, column = 0, sticky = "nswe")
        yscroll.grid(row = 0, column = 1, sticky = "ns")
        xscroll.grid(row = 1, column = 0, sticky = "ew")

        return frame

    def make_headers(self, colnames):
        col_labs = [tk.Label(self.frame,
                             text = col, justify = "left", wraplength = 200)
                    for col in colnames]

        [c.grid(row = 0, column = i, padx = 1, pady = 1,
                sticky = "nswe", ipadx = 1)
         for i, c in enumerate(col_labs, 1)]

        [self.frame.columnconfigure(i, weight = 1)
         for i, c in enumerate(col_labs)]

        self.canvas.configure(scrollregion = self.canvas.bbox("all"))

    def make_columns(self, row_name):
        col_vars = [tk.StringVar(self) for c in self.qobjects]
        [q_v[0].update({"answer_var": q_v[1],
                        "frame_name": row_name.lower() + str(i)})
         for i, q_v in enumerate(zip(self.qobjects, col_vars), 1)]

        col_types = [q.get("type") for q in self.qobjects]
        cidx = [classes.get(qtype) for qtype in col_types]
        answer_objects = [c(self.frame, **q)
                          for c, q in zip(cidx, self.qobjects)]
        return answer_objects

    def add_row(self, row_name):
        name_0 = row_name.lower() + "0"
        name_cell = tk.Label(self.frame, text = row_name,
                             justify = "left", name = name_0)

        cols = self.make_columns(row_name)
        tab_row = [name_cell] + cols

        row_idx = self.nrows.get()
        [c.grid(row = row_idx, column = i, sticky = "nswe",
                padx = 1, pady = 1)
         for i, c in enumerate(tab_row)]

        row_idx +=1
        self.nrows.set(row_idx)
        hack_scroll = self.canvas.bbox("all")[0:3] + (row_idx * 30, )
        self.canvas.configure(scrollregion = hack_scroll)
        return None

    def remove_row(self, row_name):
        cell_names = [row_name.lower() + str(i)
                      for i in range(len(self.qobjects) + 1)]
        cells = [self.frame.children.get(n) for n in cell_names]
        [c.grid_forget() for c in cells if c != None]
        [c.destroy() for c in cells if c != None]

        return None

    def make_inactive(self):
        pass

    def make_active(self):
        pass

    def been_answered(self):
        answers = list()
        for w in self.frame.children.values():
            try:
                a = w.been_answered()
                answers.append(a)
            except AttributeError:
                pass
        return False not in answers

classes = {"choice": Choice,
           "entry": Entry,
           "slider": Slider,
           "check": Check,
           "dropdown": Dropdown,
           "text": TextBox,
           "dynamic_text": DynamicText}


# def test_run():
#     root = tk.Tk()
#     avar = tk.StringVar(root)
#     avar.set("x99")

#     test_q = {"options": ["Let's ", "go to the dogs tonight"],
#               "answer_var": avar,
#               "label": "dogs"}

#     test_qlist = {"options": ["Let's ", "go to the dogs tonight"],
#                   "answer_var": tk.StringVar(root),
#                   "label": "dogs"}

#     test_qscale = {"options": [58, 76, 2],
#                   "answer_var": tk.StringVar(root),
#                   "label": "dogs"}

#     choice = Choice(root, **test_q)
#     entry = Entry(root, **test_q)
#     check = Check(root, **test_q)
#     dropdown = Dropdown(root, **test_qlist)
#     slider = Slider(root, **test_qscale)

#     return root, choice, entry, check, dropdown, slider

#gunners = test_run()
