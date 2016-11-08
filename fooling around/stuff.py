import Tkinter as tk


class ConfirmScale(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        self.pack()

        self.bob = tk.Scale(self)
        #bob.grid(row = 0, column = 1)

        self.create_rectangle(0, 0, 20, 20, fill = "blue")

test = tk.Tk()
tf=ConfirmScale(test)
