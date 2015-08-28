import Tkinter as tk
import os
import csv

class UpdateTable(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.pack(fill = "both", expand = True)

        self.data_path = ("/Users/aserwaahWZB/Projects/"
                          "GUI Code/india other data/"
                          "Current version/pkg/shared/"
                          "startscreen/identifiers")
        taluks, villages = self.get_villages()

        self.village_var = tk.IntVar(self)
        village_list = apply(tk.OptionMenu,
                             ((self, self.village_var) + villages))
        village_list.grid(row = 0, column = 0)
        self.households = self.get_households()
        self.enumerators = self.get_enumerators()

        hh_container = tk.Frame(self)
        hh_container.grid(row = 1, column = 0)
        self.rowconfigure(1, weight = 1)
        self.columnconfigure(0, weight = 1)
        self.frame, self.xframe, self.yframe = self.make_scrollable_frame(hh_container)

        self.make_headers(("Checked", "Date", "Enumerator"))
        self.nrows = tk.IntVar()
        self.nrows.set(0)


    def widget_name(self, rowname):
        nsub = rowname.replace(".", "_")
        #nsub = nsub.replace(" ", "")
        return nsub.lower()

    def make_scrollable_frame(self, master):
        canvas = self.canvas = tk.Canvas(master, bg = "light salmon",
                                         height = 1000, width = 1600)
        self.xcanvas = tk.Canvas(master,
                                 width = 1600, height = 5)
        self.ycanvas = tk.Canvas(master,
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

        yscroll = tk.Scrollbar(master, command = canvases_yview)
        xscroll = tk.Scrollbar(master,
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
        frames = [tk.Frame(self.frame)
                  for f in (0, 1, 2)]
        f1, f2, f3 = frames

        options = ("Surveyed", "Revisit", "Out of sample", "Not surveyed")
        done = [tk.Radiobutton(f1, text = t) for t in options]
        [d.pack(side = "top") for d in done]

        enum_var = tk.StringVar()
        enumerators = apply(tk.OptionMenu,
                            ((f3, enum_var) + self.enumerators))
        enumerators.pack()
        return frames

    def add_row(self, row_name):

        def fix_width(idx):
            cols = self.columns.get(idx)
            self.update_idletasks()
            widget_lengths = [c.winfo_reqwidth() for c in cols]
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
            c.grid(row = row_idx, column = i, 
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


    def get_villages(self):
        village_path = os.path.join(self.data_path,
                                    "villages.csv")
        with open(village_path, "r") as vfile:
            vcsv = csv.reader(vfile)
            rownames = vcsv.next()
            village_info = dict([(v[0], {"village": v[0],
                                         "taluk":   v[1],
                                         "tid":     v[2],
                                         "vid":     v[3]})
                                 for v in vcsv])
        def name_to_id_dic(name, name_id):
            village_dics = village_info.values()

            name_dic = dict([(d.get(name), d.get(name_id))
                             for d in village_dics])

            id_dic = dict([(d.get(name_id), d.get(name))
                           for d in village_dics])
            return name_dic, id_dic

        self.name_tid, self.tid_name  = name_to_id_dic("taluk", "tid")
        self.name_vid, self.vid_name = name_to_id_dic("village", "vid")

        taluks = tuple(sorted(self.name_tid.keys()))
        villages = tuple(self.name_vid.keys())

        return taluks, villages

    def get_households(self):
        shortration = "outputRationcard_number"
        shortelection = "electionid_text"
        shortname = "houhseholdhead_name"
        shortrelation = "houhseholdhead_relation"

        hh_path = os.path.join(self.data_path,
                               "households.csv")

        with open(hh_path, "r") as hfile:
            hcsv = csv.reader(hfile)
            names = hcsv.next()

            labelled_rows = [dict(zip(names, row)) for row in hcsv]
            households = dict()

            for row in labelled_rows:
                relation = row.get("relationTag")
                try:
                    r = int(relation)
                    rdic =  {1:'S/O', 2:'D/O', 3:'W/O'}
                    relationship = rdic.get(r, " ")
                except ValueError:
                    relationship = relation

                name = (row.get(shortname) +
                        " " + relationship + " " +
                        row.get(shortrelation)).upper().strip()

                wzb_hh_id = row.get("wzb.hh.id")
                hh_dic = {"vid": row.get("village"),
                          "tid": row.get("taluk"),
                          "hid": wzb_hh_id,
                          "ration_nr": row.get(shortration),
                          "election_id": row.get(shortelection),
                          "hh_name": name.strip(),
                          "taluk": self.tid_name.get(row.get("taluk")),
                          "village": self.vid_name.get(row.get("village"))}

                # members = self.members.get(wzb_hh_id)
                # if members != None:
                #     members_list = members.keys()
                # elif members == None:
                #     members_list = "No household members entered"
                # hh_dic.update({"members": members,
                #                "members_list": members_list})
                households.update({name: hh_dic})

        return households

    def get_enumerators(self):
        enum_path = os.path.join(self.data_path,
                                 "enumerators.csv")

        with open(enum_path, "r") as enumfile:
            enum = csv.reader(enumfile)
            enumerators_csv = dict([(int(e[1]), e[0])
                                for e in enum])

        def pad(num_in):
            num = str(num_in)
            pad = 2 - len(num)
            return "0" * pad + num

        self.name_enumid = dict([(pad(key) + " - " + value, key)
                                 for key, value
                                 in sorted(enumerators_csv.items())])

        enumerators = tuple(sorted(self.name_enumid.keys()))

        return enumerators


root = tk.Tk()
turku = UpdateTable(root)
turku.add_row("Amma")
