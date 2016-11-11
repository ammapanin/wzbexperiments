#!/usr/bin/python
# -*- coding: utf-8 -*-

### Standardised log-in page for enumerator data collection in India
### Last updated: 7.11.16 , beginning work for the time preference tasks

import Tkinter as tk
import os
import tkFont

from dropdowns import SelectorDropdowns
### Keep this import statement only for testing!
#from definitions import *

class Startscreen(tk.Frame):
    def __init__(self, master, start_function, definitions, test_mode):
        """Initialise startscreen.

        Args:
            master (tk.Frame)
            root (tk.Frame)
            definitions (dict) - dictionary containing all the definitions
                of a given startscreen. {"standard": *defs*, "dynamic": *defs*}
            test_mode (Bool) - True/False
         """

        tk.Frame.__init__(self, master)
        self.pack(side = "top")

        self.show_experiment = start_function
        standard, dynamic = [definitions.get(i) for i in ("standard", "dynamic")]
        msg_frame, dropdown_frame, bt_frame = self.make_frames()
        self.display_info(msg_frame)
        self.dropdowns = SelectorDropdowns(dropdown_frame,
                                           standard, dynamic)
        self.bt = self.make_button(bt_frame)

    def make_frames(self):
        msg, dropdown, bt = [tk.Frame(self) for i in range(0, 3)]
        [f.pack(side = "top", fill = "both", expand = True)
         for f in (msg, dropdown)]
        bt.pack(side = "bottom", anchor = "w")
        return msg, dropdown, bt

    def display_info(self, master):
        header_font = tkFont.Font(size = 15, weight = "bold")
        heading = ("Please select the following informatigon. "
                   "When you have finished, pressed validate."
                   "\nIf there are any other corrections, "
                   "please note them at the end of the experiment.")
        head_lab = tk.Label(master,
                            text = heading,
                            font = header_font,
                            wraplength = 1000)
        head_lab.pack(side = "top", fill = "both")
        return None

    def make_button(self, master):
        self.bt = tk.Button(master,
                            text = "Begin",
                            command = self.begin_experiment)
        self.bt.pack(side = "bottom", anchor = "sw")

    def transform_variables(self, dic):
        """Ensure that variables are saved with user-friendly names
        """
        
        tdic, new_idx = self.dropdowns.transform.get("enumerator")
        value = dic.get("enumerator")
        if tdic != None:
            new_value = tdic.get(value)
            dic.update({new_idx: new_value})
        return dic

    def begin_experiment(self):
        idx_dic = self.dropdowns.save_data()
        tdic = self.transform_variables(idx_dic)
        #idx_dic.update({"enum_id": tdic.get("enumerator")})
        self.pack_forget()
        self.show_experiment(idx_dic)
        return None


# root = tk.Tk()
# Startscreen(root, "", definitions, False)
# root.mainloop()
