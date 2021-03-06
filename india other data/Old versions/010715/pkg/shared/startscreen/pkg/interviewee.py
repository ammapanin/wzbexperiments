import Tkinter as tk



class Interview(tk.LabelFrame):
    def __init__(self, master, idx, participate, *args, **kwargs):
        tk.LabelFrame.__init__(self, master, *args, **kwargs)
        self.pack(fill = "both", anchor = "w")

        self.participate = participate
        self.households = idx["households"]
        self.hh_var = idx["hh_var"]
        self.hh_var.trace("w", self.update_members)

        f = tk.Frame(self)
        f.pack(side = "top", anchor = "w")
        self.member_var = tk.StringVar(self)

        lab_text = "Who is being interviewed?"
        text_label = tk.Label(f, text = lab_text)
        text_label.grid(row = 0, column = 0)

        members_list = ("No selection made", )
        self.members = apply(tk.OptionMenu,
                             ((f, self.member_var) + members_list))
        self.members.grid(row = 0, column = 1)

        self.correction_frame, self.correction_vars = self.make_corrections()
        self.member_var.trace("w", self.show_corrections)

    def update_members(self, name, index, mode):
        hh_name = self.hh_var.get()
        hh_members = self.households.get(hh_name).get("members").keys()
        self.refresh_members(hh_members)

    def refresh_members(self, hh_members):
        self.members["menu"].delete(0, "end")
        for value in hh_members  + ["Other"]:
            self.members["menu"].add_command(label = value,
                                             command = tk._setit(self.member_var,
                                                                 value))

    def make_corrections(self):
        correction_frame = tk.Frame(self)

        detail_text = ("Please enter the details"
                       " of the person being interviewed")
        correction = tk.Label(correction_frame,
                                  text = detail_text)
        correction.pack(side = "top", anchor = "w")

        details_frame = tk.Frame(correction_frame)
        details_frame.pack(side = "top")

        texts = ("Interviewee name",
                 "Interviewee Rationcard Number",
                 "Interviewee Election ID",
                 "Relationship to head of household",)

        n = len(texts)-1
        interview_vars = [tk.StringVar(details_frame) for t in texts]
        labs = [tk.Label(details_frame, text = txt) for txt in texts]
        entries = [tk.Entry(details_frame, textvariable = var)
                   for var in interview_vars[0:n]]

        relations = ("Wife", "Husband",
                     "Mother", "Father",
                     "Son", "Daughter",
                     "Son-in-law", "Daughter-in-law",
                     "Mother-in-law", "Father-in-law",
                     "Other")


        relationship = apply(tk.OptionMenu,
                             ((details_frame, interview_vars[n]) + relations))

        entries.append(relationship)

        for i, (l, e) in enumerate(zip(labs, entries)):
            l.grid(row = i, column = 0, sticky = "w")
            e.grid(row = i, column = 1, sticky = "w")


        return correction_frame, interview_vars


    def show_corrections(self, name, index, mode):
        member = self.member_var.get()

        if member == "Other":
            self.correction_frame.pack(anchor = "w")
        else:
            self.correction_frame.pack_forget()
            [v.set("") for v in self.correction_vars]

    def validate(self):
        msg = "Please select the person being interviewed"
        messages = ("Please enter the name of the person being interviewed",
                    ("Please enter the rationcard number "
                     "of the person being interviewed"),
                    ("Please enter the election id of "
                     "the person being interviewed"),
                    ("Please enter the relationship to the "
                     "head of the person being interviewed"))

        member = self.member_var.get()
        corrections = [v.get() for v in self.correction_vars]

        warnings = list()
        if self.participate.get() == 0:
            pass
        else:
            if member == "":
                warnings.append(msg)
            elif member == "Other":
                for c, m in zip(corrections, messages):
                    if c == "":
                        warnings.append(m)

        return warnings

