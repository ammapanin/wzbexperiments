import Tkinter as tk


class DynamicTable(tk.LabelFrame):
    def __init__(self, master, headers):
        tk.LabelFrame.__init__(self, master)
        self.pack(fill = "both", expand = True)

        frames = self.make_scrollable_frame()
        self.frame, self.xframe, self.yframe = frames
        #self.qobjects = table_objects
        self.col_names = headers
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
        col_labs = [tk.Label(self.xframe,
                             text = col, 
                             justify = "left", 
                             wraplength = 200)
                    for col in colnames]

        #Changed enumerate! 29.07.15
        self.columns = dict()
        for i, c in enumerate(col_labs):
            c.grid(row = 0, column = i, 
                   padx = 1, pady = 1,
                   sticky = "nswe", 
                   ipadx = 1)
            self.columns.update({i:[c]})
        height = self.xframe.winfo_height()
        print self.xcanvas.bbox(self.xid)
        print height
        self.xcanvas.config(height = height)
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
        #nsub = nsub.replace(" ", "")
        return nsub.lower()

    def add_row(self, row_name):

        def fix_width(idx):
            cols = self.columns.get(idx)
            widget_lengths = [c.wlength for c in cols]
            max_width = min((200, max(widget_lengths)))
            [c.config(width = max_width) for c in cols]
            return None

        row_idx = self.nrows.get()
        name_0 = self.widget_name(row_name) + "xx0"
        name_cell = tk.Label(self.frame, 
                             text = row_name,
                             anchor = "w",
                             justify = "left", 
                             name = name_0)
        name_cell.grid(row = row_idx, column = 0, sticky = "nswe")

        cols = self.make_columns(row_name)
        for i, c in enumerate(cols):
            self.columns[i].append(c)
            c.grid(row = rown, column = i, 
                   padx = 1, pady = 1,
                   sticky = "nswe", 
                   ipadx = 1)
            fix_width(i)

        #tab_row = [name_cell] + cols
        #[c.grid(row = row_idx, column = i, sticky = "nswe",
        #        padx = 1, pady = 1)
        #for i, c in enumerate(tab_row)]

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
        cell_names = [row_name.lower() + "xx{}".format(i)
                      for i in range(len(self.qobjects) + 1)]
        cells = [self.frame.children.get(n) for n in cell_names]
        [c.grid_forget() for c in cells if c != None]
        [c.destroy() for c in cells if c != None]

        return None

    def get_idx(self, str_name):
        print str_name
        p = re.compile("\d*xx\d*")
        xx_str = p.search(str_name).group()
        col_idx = xx_str.split("xx")[1]
        return int(col_idx)



root = tk.Tk()
amma = DynamicTable(root, ["Helsinki", "Turku", "Islands"])



