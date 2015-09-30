import Tkinter as tk

class Instructions(tk.Frame):
    def __init__(self, master, ipath):
        tk.Frame.__init__(self, master)
        self.pack(side = "top", expand = True, fill = "both")

        textbox = tk.Text(self)
        vscroll = tk.Scrollbar(self, orient = "vertical")
        textbox.pack(side = "left", fill = "both", expand = True)
        vscroll.pack(side = "right", fill = "y", expand = False)
        vscroll.config(command = textbox.yview)
        textbox.config(yscrollcommand = vscroll.set)
 
        with open(ipath, "rb") as ifile:
            itext = ifile.read()

        textbox.insert("0.0", itext)
        textbox.config(state = "disabled")


        #amma = tk.Frame(self)
        #bob = tk.Label(amma, text = "Quelle heure est-il au paradis?")
        #bob.pack()

        #textbox.window_create("5.0", window = amma)


root = tk.Tk()
Amma = Instructions(root, "instructions_test.txt")
        
