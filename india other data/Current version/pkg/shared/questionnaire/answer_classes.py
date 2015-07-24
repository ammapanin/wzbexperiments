import Tkinter as tk
import tkFont
import re
from input_classes import *

class DynamicTable(tk.LabelFrame):
    def __init__(self, master, table_objects):
        tk.LabelFrame.__init__(self, master)
        self.pack(fill = "both", expand = True)

        self.frame = self.make_scrollable_frame()
        self.qobjects = table_objects
        self.col_names = [q.get("question_text")
                          for q in table_objects]
        self.make_headers(self.col_names)
        self.nrows = tk.IntVar(self.frame)
        self.nrows.set(1)

    def make_scrollable_frame(self):
        canvas = tk.Canvas(self, bg = "light salmon",
                           height = 350, width = 1600)

        frame = tk.LabelFrame(canvas, bg = "dim gray")
        yscroll = tk.Scrollbar(self, command = canvas.yview, bg = "red")
        xscroll = tk.Scrollbar(self,
                               orient = "horizontal",
                               command = canvas.xview,
                               bg = "red")

        canvas.config(yscrollcommand = yscroll.set,
                           xscrollcommand = xscroll.set)

        canvas.create_window((5, 5,),
                             window = frame,
                             anchor = "nw",
                             tags = "frame")

        def on_frame_configure(event):
            w = frame.winfo_reqwidth()
            h = frame.winfo_reqheight()
            canvas.configure(scrollregion = (5, 5, w, h))
            return None

        frame.bind("<Configure>", on_frame_configure)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        canvas.grid(row = 0, column = 0, sticky = "nswe")
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

    def make_columns(self, row_name):
        col_vars = [tk.StringVar(self) for c in self.qobjects]
        [q_v[0].update({"answer_var": q_v[1],
                        "frame_name": row_name.lower() + "xx{}".format(i)})
         for i, q_v in enumerate(zip(self.qobjects, col_vars), 1)]

        col_types = [q.get("type") for q in self.qobjects]
        cidx = [classes.get(qtype) for qtype in col_types]
        answer_objects = [c(self.frame, **q)
                          for c, q in zip(cidx, self.qobjects)]
        return answer_objects

    def add_row(self, row_name):
        name_0 = row_name.lower() + "xx0"

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
        return None

    def remove_row(self, row_name):
        cell_names = [row_name.lower() + "xx{}".format(i)
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
        # answers = list()
        # for w in self.frame.children.values():
        #     try:
        #         a = w.been_answered()
        #         answers.append(a)
        #     except AttributeError:
        #         pass
        return True

    def get_idx(self, str_name):
        print str_name
        p = re.compile("\d*xx\d*")
        xx_str = p.search(str_name).group()
        col_idx = xx_str.split("xx")[1]
        return int(col_idx)

    def get_answer(self):
        lab_names = [q.get("label") for q in self.qobjects]

        widgets = [(k, v) for k, v in self.frame.children.items()
                   if "xx" in k]
        info_widgets = [(k, v) for k, v in widgets
                        if v.__class__ != tk.Label]
        rownames = set([k.split("xx")[0] for k, v in info_widgets])

        rows = dict([(r, list()) for r in list(rownames)])
        print rows

        for name, widget in info_widgets:
            rowname = name.split("xx")[0]
            idx = self.get_idx(name)
            rows[rowname].append((idx, widget))

        answers = list()
        for rowname, row in rows.items():
            for col in row:
                print col
                colname = lab_names[col[0] - 1]
                widget = col[1]
                #name = colname + "_" + rowname
                col_answers = widget.get_answer()
                answer = [(colname - "_" + rowname, a) for rowname, a
                          in col_answers]
                answers.append(answer)
        print answers
        return answers

classes = {"choice": Choice,
           "entry": Entry,
           "slider": Slider,
           "check": Check,
           "dropdown": Dropdown,
           "text": TextBox,
           "dynamic_text": DynamicText}


def answer_class_test():
    root = tk.Tk()
    avar = tk.StringVar(root)
    avar.set("x99")

    test_q = {"options": [9, 25, "1,zLet's,zgo to the dogs tonight"],
              "label": "dogs",
              "num_list": True,
              "qview": "single"}

    fred = Slider(root, **test_q)
    # choice = Choice(root, **test_q)
    # entry = Entry(root, **test_q)
    # check = Check(root, **test_q)
    # dropdown = Dropdown(root, **test_qlist)
    # slider = Slider(root, **test_qscale)

    return fred

#gunners = answer_class_test()
