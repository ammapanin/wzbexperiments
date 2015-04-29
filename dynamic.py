import Tkinter as Tk




class DynamicDropdown(tk.StringVar):

    def __init__(self, master, options, *args, **kwargs):
        tk.StringVar.__init__(self, master)

        self.options = options
        self.dropdown = apply(tk.OptionMenu,
                              ((master, self) + ("No selection made",)))
        self.dropdown.grid()
        self.trace("w", self.update_dropdown)

    def update_dropdown(self, name, index, var):
        key = self.get()
        values = self.options.get(key, ("No value found", ))
        self.dropdown["menu"].delete(0, "end")
        for value in values:
            self.dropdown["menu"].add_command(label = "",
                                              command = tk._setit(self, value))








the_choice = {"l1": ["The intellect of man is forced to choose",
                     "perfection of life or that of the work"],
              "l2": ["And if it take the second must refuse",
                     "A heavenly mansion, raging in the dark"]}

root_beer = tk.Tk()
amma = DynamicDropdown(root_beer, the_choice)

fred = tk.Radiobutton(root_beer, variable = amma, value = "l1")
bob = tk.Radiobutton(root_beer, variable = amma, value = "l2")

[b.grid() for b in (fred, bob)]
