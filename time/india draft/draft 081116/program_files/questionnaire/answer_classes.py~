import Tkinter as tk
import tkFont
import re
from input_classes import *

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


class DynamicTable(tk.LabelFrame):
    def __init__(self, master, table_objects):
        tk.LabelFrame.__init__(self, master)
        self.pack(fill = "both", expand = True)

        frames = self.make_scrollable_frame()
        self.frame, self.xframe, self.yframe = frames
        self.qobjects = table_objects
        self.col_names = [q.get("question_text")
                          for q in table_objects]
        self.make_headers(self.col_names)
        self.nrows = tk.IntVar(self.frame)
        self.nrows.set(1)

    def make_scrollable_frame(self):
        canvas = self.canvas = tk.Canvas(self, bg = "light salmon",
                                         height = 200, width = 1600)
        self.xcanvas = tk.Canvas(self, bg = "medium orchid",
                                 width = 1600, height = 5)
        self.ycanvas = tk.Canvas(self, bg = "SpringGreen2",
                                 width = 50, height = 200)

        def canvases_xview(*args):
            canvas.xview(*args)
            self.xcanvas.xview(*args)

        def canvases_yview(*args):
            canvas.yview(*args)
            self.ycanvas.yview(*args)

        canvases = (canvas, self.xcanvas, self.ycanvas)
        frames =  [tk.LabelFrame(c, bg = "dim gray") for c in canvases]
        frame, xframe, yframe = frames

        yscroll = tk.Scrollbar(self, command = canvases_yview)
        xscroll = tk.Scrollbar(self,
                               orient = "horizontal",
                               command = canvases_xview)

        self.xcanvas.config(xscrollcommand = xscroll.set)
        self.ycanvas.config(yscrollcommand = yscroll.set)
        canvas.config(yscrollcommand = yscroll.set,
                      xscrollcommand = xscroll.set)

        self.fid, self.xid, self.yid = [c.create_window((5, 5,),
                                                        window = f,
                                                        anchor = "nw",
                                                        tags = "frame")
                                        for c, f in zip(canvases, frames)]

        def on_frame_configure(event):
            w = frame.winfo_reqwidth()
            h = frame.winfo_reqheight()
            canvas.configure(scrollregion = (5, 5, w, h))
            self.xcanvas.configure(scrollregion = (5, 5, w, 100))
            self.ycanvas.configure(scrollregion = (5, 5, 50, h))
            return None

        def fix_x_height(event):
            h = xframe.winfo_reqheight()
            self.xcanvas.configure(height = h)

        def fix_y_width(event):
            w = yframe.winfo_reqwidth()
            self.ycanvas.configure(width = w)

        frame.bind("<Configure>", on_frame_configure)
        xframe.bind("<Configure>", fix_x_height)
        yframe.bind("<Configure>", fix_y_width)

        self.columnconfigure(1, weight = 1)
        self.rowconfigure(1, weight = 1)

        self.xcanvas.grid(row = 0, column = 1, sticky = "nswe")
        self.ycanvas.grid(row = 1, column = 0, sticky = "nswe")
        canvas.grid(row = 1, column = 1, sticky = "nswe")

        yscroll.grid(row = 1, column = 2, sticky = "ns")
        xscroll.grid(row = 2, column = 1, sticky = "ew")
        return frame, xframe, yframe

    def make_headers(self, colnames):
        col_labs = [tk.Frame(self.xframe,
                             bg = "light gray") for col in colnames]
        col_texts = [tk.Label(col,
                              bg = "light gray",
                              text = txt,
                              justify = "left",
                              wraplength = 200)
                     for txt, col in zip(colnames, col_labs)]
        [c.grid(sticky = "nwse") for c in col_texts]
        self.update_idletasks()
        header_widths = [h.winfo_reqwidth() for h in col_texts]
        header_height = max([h.winfo_reqheight() for h in col_texts])
        [f.config(width = w, height = header_height)
         for f, w in zip(col_labs, header_widths)]

        #Changed enumerate! 29.07.15
        self.columns = dict()
        for i, c in enumerate(col_labs):
            c.grid(row = 0, column = i,
                   padx = 1, pady = 1,
                   sticky = "nswe",
                   ipadx = 1)
            self.columns.update({i:[c]})
            c.wlength = len(c.children.values()[0].cget("text"))

        height = self.xframe.winfo_height()
        self.xcanvas.config(height = height)
        [f.grid_propagate(False) for f in col_labs]
        return None

    def make_columns(self, row_name):
        """Creates each colum widget per row
        Returns a list of instantiated(!) answer_classes, incl. length)
        """
        col_vars = [tk.StringVar(self) for c in self.qobjects]
        [q_v[0].update({"answer_var": q_v[1],
                        "frame_name": row_name.lower() + "xx{}".format(i)})
         for i, q_v in enumerate(zip(self.qobjects, col_vars), 1)]

        col_types = [q.get("type") for q in self.qobjects]
        cidx = [classes.get(qtype) for qtype in col_types]
        answer_objects = [c(self.frame, **q)
                          for c, q in zip(cidx, self.qobjects)]
        return answer_objects

    def widget_name(self, rowname):
        nsub = rowname.replace(".", "_")
        nsub = nsub.replace(" ", "")
        return nsub.lower()

    def add_row(self, row_name):
        """Adds a row, calling self.make_columns() to define the column type

        Args: row_name
        Assumes that column definitions are fixed in make_columns
        Fixes the width of each column
        """
        row_idx = self.nrows.get()
        name_stub = self.widget_name(row_name)
        row_heights = list()

        def fix_width(idx):
            cols = self.columns.get(idx)
            self.update_idletasks()
            print cols
            widget_lengths = [c.winfo_width() for c in cols]
            current_height = c.winfo_height()
            row_heights.append(current_height)
            max_width = max(widget_lengths)
            cols[0].config(width = max_width)
            [c.config(width = max_width,
                      height = current_height) for c in cols[1:]]
            c.grid_propagate(False)
            return current_height

        cols = self.make_columns(name_stub)
        for i, c in enumerate(cols):
            self.columns[i].append(c)
            c.grid(row = row_idx, column = i,
                   padx = 1, pady = 1,
                   sticky = "nswe",
                   ipadx = 1)
            fix_width(i)

        name_cell = tk.Frame(self.yframe,
                             bg = "light steel blue",
                             name = name_stub + "xx0")
        name_lab = tk.Label(name_cell,
                            bg = "light steel blue",
                            text = row_name,
                            anchor = "w",
                            justify = "left")
        name_lab.grid(sticky = "nswe")
        row_height = max(row_heights)
        self.update_idletasks()
        name_width = name_cell.winfo_reqwidth()
        name_cell.config(width = name_width, height = row_height)
        name_cell.grid_propagate(False)
        name_cell.grid(row = row_idx,
                       column = 0,
                       sticky = "nswe",
                       pady = 1)
        row_idx +=1
        self.nrows.set(row_idx)
        return None

    def test_rows(self, row_name, rown):
        name_0 = row_name.lower() + "xx0"
        name_cell = tk.Label(self.yframe, text = row_name,
                             anchor = "w",
                             name = name_0)
        name_cell.grid(row = rown, column = 0, pady = 1, sticky = "nswe")

        colnames =  ("Margi", "Lina", "Soo")

    def remove_row(self, row_name):
        name_stub = self.widget_name(row_name)
        cell_names = [name_stub + "xx{}".format(i)
                      for i in range(len(self.qobjects) + 1)]
        cells = [self.frame.children.get(n) for n in cell_names] +\
                [self.yframe.children.get(name_stub + "xx0")]
        [c.grid_forget() for c in cells if c != None]
        [c.destroy() for c in cells if c != None]

        for i, widget_list in enumerate(self.columns.values(), 1):
            for cell in widget_list:
                if cell._name == name_stub + "xx{}".format(i):
                    ridx = widget_list.index(cell)
                    widget_list.pop(ridx)
        return None

    def get_idx(self, str_name):
        p = re.compile("\d*xx\d*")
        xx_str = p.search(str_name).group()
        col_idx = xx_str.split("xx")[1]
        return int(col_idx)

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
        print self.frame.children.items()
        widgets = [(k, v) for k, v in self.frame.children.items()
                   if "xx" in k]
        info_widgets = [(k, v) for k, v in widgets
                        if v.__class__ != tk.Label]
        rownames = set([k.split("xx")[0] for k, v in info_widgets])

        rows = dict([(r, list()) for r in list(rownames)])

        for name, widget in info_widgets:
            rowname = name.split("xx")[0]
            idx = self.get_idx(name)
            rows[rowname].append((idx, widget))

        answers = list()
        for rowname, row in rows.items():
            for col in row:
                colname = lab_names[col[0] - 1]
                widget = col[1]
                #name = colname + "_" + rowname
                colname, a = widget.get_answer()[0]
                answer = (rowname + "_" + colname, a)
                answers.append(answer)
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
