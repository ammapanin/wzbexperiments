import Tkinter as tk


class Answer(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master)
        self.pack(side = "top", expand = True)

        self.answer_var = kwargs.get("answer_var")
        self.options = kwargs.get("options")

class Choice(Answer):
    def __init__(self, master, **kwargs):
        Answer.__init__(self, master, **kwargs)

        self.bts = [tk.Radiobutton(self,
                                   text = txt,
                                   var = self.answer_var,
                                   value = txt)
                    for txt in self.options]
        [bt.pack(side = "top", anchor = "w") for bt in self.bts]


class Entry(Answer):
    def __init__(self, master, **kwargs):
        Answer.__init__(self, master, **kwargs)
        self.entry = tk.Entry(self,
                              textvariable = self.answer_var,
                              show = " ")
        self.entry.pack(side = "top", anchor = "w", pady = 2)

        self.ever_answered = 0
        def clear_entry(name, index, mode):
            self.ever_answered += 1
            if self.ever_answered > 1:
                pass
            else:
                self.entry.delete(0, "end")
                self.entry.config(show = "")

        self.answer_var.trace("w", clear_entry)


classes = {"choice": Choice,
           "entry": Entry}
