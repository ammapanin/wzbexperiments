import Tkinter as tk




class NewStartScreen(tk.Frame):


    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.pack(fill = "both", expand = True)

        self.idx = Dropdowns(self, self.participation)
        hh_kwargs = {"households": self.idx.households,
                     "hh_var": self.idx.hh_var}
        self.hh_details = CorrectInfo(self, hh_kwargs)


    def participation(self, name, index, mode):
        participate = self.idx.participate.get()

        if participate == True:
            self.hh_details.show()
        elif participate == False:
            self.hh_details.hide()

root = tk.Tk()
NewStartScreen(root)
