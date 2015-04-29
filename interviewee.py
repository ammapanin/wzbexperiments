import Tkinter as tk



class Interview(tk.LabelFrame):
    def __init__(self, master, members_list, *args, **kwargs):
        tk.LabelFrame.__init__(self, master, *args, **kwargs)


        f = tk.Frame(self)
        f.pack(side = "top", anchor = "w")
        self.member_var = tk.StringVar(self)

        lab_text = "Who is being interviewed?"
        text_label = tk.Label(f, text = lab_text)
        text_label.grid(row = 0, column = 0)

        members = apply(tk.OptionMenu,
                        ((f, self.member_var) + members_list + ("Other",)))
        members.grid(row = 0, column = 1)

        self.correction_frame = self.make_corrections()
        self.member_var.trace("w", self.show_corrections)

    def show(self):
        self.pack()

    def hide():
        self.pack_forget()

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

        return correction_frame


    def show_corrections(self, name, index, mode):
        member = self.member_var.get()

        if member == "Other":
            self.correction_frame.pack()
        else:
            self.correction_frame.pack_forget()
                # Also delete entries!

root = tk.Tk()
bob = Interview(root, ("Disneland" ,"in"))
