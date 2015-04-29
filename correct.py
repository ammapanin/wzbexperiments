
import Tkinter as tk



class CorrectInfo(tk.LabelFrame):
    def __init__(self, master, idx, *args, **kwargs):
        tk.LabelFrame.__init__(self, master, *args, **kwargs)

        self.households = idx["households"]
        self.hh_var = idx["hh_var"]
        self.hh_var.trace("w", self.update_hh)

        self.display = DisplayCorrectInfo(self, ("A", "b", "CCc"))
        self.add = AddCorrectInfo(self, corrections)

    def update_hh(self, name, index, mode):
        hh_name = self.hh_var.get()
        hh_info = self.get_hh_info(hh_name)
        self.display.refresh(hh_info)

    def get_hh_info(self, hh_name):
        field_ids = ("ration_nr", "election_id")
        hh = self.households.get(hh_name)
        ids = [hh.get(i) for i in field_ids]
        return [hh_name] + ids

    def show(self):
        self.pack(fill = "both", expand = True)

    def hide(self):
        self.pack_forget()


class DisplayCorrectInfo:
    def __init__(self, master, hh_info):
        info_text = ("Are the following details "
                     " of the household head correct?")

        lab_texts = ("Household head name",
                     "Rationcard Number",
                     "Election ID")

        hh_placeholder = ("A", "B", "C")

        info_lab = tk.Label(master, text = info_text)
        info_lab.pack(side = "top", anchor = "w")

        info_frame = tk.Frame(master)
        info_frame.pack(side = "top", anchor = "w", pady = 8)

        labs = [tk.Label(info_frame, text = txt) for txt in lab_texts]
        info = [tk.Label(info_frame, text = txt) for txt in hh_placeholder]
        self.infos = info

        for i, l in enumerate(labs):
            l.grid(row = i, column = 0, sticky = "w")
        for i, l in enumerate(info):
            l.grid(row = i, column = 1, sticky = "w", padx = 10)

    def refresh(self, hh_info):
        labs = zip(self.infos, hh_info)
        [lab.config(text = txt) for lab, txt in labs]


class AddCorrectInfo:
    def __init__(self, master, text_options):

        bt_frame = tk.Frame(master)
        bt_frame.pack(side = "top",
                      fill = "both",
                      expand = True,
                      pady = 10)

        yes_text = text_options[0]
        no_texts = text_options[1:]
        len_no = len(no_texts)

        self.yes_var = tk.BooleanVar(master)
        self.no_var = tk.BooleanVar(master)
        self.correction_vars = [tk.BooleanVar(master) for i in range(len_no)]
        bt_vars = [self.yes_var] + self.correction_vars
        self.entry_vars = [tk.StringVar(master) for i in self.correction_vars]

        txt_vars = zip(text_options, bt_vars)
        bts = [tk.Checkbutton(bt_frame,
                              var = v,
                              text = "{}".format(txt),
                              justify = "left")
               for txt, v in txt_vars]

        [bt.grid(row = i, column = 0, sticky = "w") for i, bt in enumerate(bts)]
        entries = [tk.Entry(bt_frame,
                            textvariable = v)
                   for v in self.entry_vars]

        var_entries = zip(self.correction_vars, entries)
        entry_dic = dict(zip(bts[1:],
                             (enumerate(var_entries, 1))))


        def yes_trace(name, index, mode):
            yes = self.yes_var.get()
            self.no_var.set(1 - yes)
            no = self.no_var.get()
            return None

        def no_trace(name, index, mode):
            on = self.no_var.get()
            if on == False:
                [bt.config(state = "disabled") for bt in bts[1:]]
            elif on == True:
                [bt.config(state = "active") for bt in bts[1:]]

        def correction_trace(name, index, mode):
            correct = [v.get() for v in self.correction_vars]
            if True in correct:
                bts[0].config(state = "disabled")
            elif True not in correct:
                bts[0].config(state = "active")
            return None

        def show_entry(bt_in):
            row_i, (var, entry) = entry_dic.get(bt_in)
            on = var.get()
            if on == True:
                entry.grid(row = row_i, column = 1, padx = 10)
            elif on == False:
                entry.delete(0, "end")
                entry.grid_forget()

        self.yes_var.trace("w", yes_trace)
        self.no_var.trace("w", no_trace)
        [v.trace("w", correction_trace) for v in self.correction_vars]

        for bt in bts[1:]:
            bt.config(command = lambda bt_in = bt: show_entry(bt_in))





corrections = ("Yes, all details are correct.",
               "No, the household head has a different name",
               "No, the ration card has a problem",
               "No, the election ID has a problem")


#root = tk.Tk()
#hector = CorrectInfo(root)



