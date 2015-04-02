# Latest envelope class
# 23 December 2013

import Tkinter as tk
import tkFont
import tkMessageBox
import os


class Envelope(tk.Canvas):
    def __init__(self, master, certainty):

        tk.Canvas.__init__(self, master)
        self.draw_frames(master)

        self.env_img = self.get_envelope_pic("small")
        self.big_env_img = self.get_envelope_pic("big")

        self.certainty = certainty

        self.riskcol = "firebrick"
        self.nullcol = "goldenrod"
        self.certain_col = "dark green"
        self.high = 24
        self.low = 5

        self.currency = "Rs {}"

        self.on = False
        self.partner = ""
        if self.certainty == False:
            self.envelopes = self.show_envs(self.env_frame)
        elif self.certainty == True:
            self.cert_lab = self.draw_certain(self.env_frame)

    def update_envelopes(self, amounts, p):
        self.high, self.low = amounts
        self.update_prob(p)

    def update_certainty(self, amt):
        self.cert_lab.config(text = self.currency.format(amt))

    def update_prob(self, p):
        self.labs_edit(self.riskcol, self.high,
                       self.envelopes[0:p])
        self.labs_edit(self.nullcol, self.low,
                       self.envelopes[p:10])
        return None

    def labs_edit(self, col, amt, plist):
        [lab.config(bg = col,
                    text = amt)
         for lab in plist]
        return None

    def draw_frames(self, master):
        pierow = 1
        self.selectframe = tk.Frame(master)
        self.selectframe.pack(side = "top",
                                   fill = "both",
                                   expand = True,
                                   anchor = "center")
        self.mainframe = tk.Frame(self.selectframe)
        self.mainframe.pack(fill = "both", expand = True, anchor = "center")


        self.env_frame = tk.LabelFrame(self.mainframe)
        self.env_frame.pack(side = "left",
                            expand = True)
        self.time_frame = tk.Frame(self.mainframe)
        self.time_frame.pack(side = "right",
                             expand = True,
                             anchor = "e")
        return None


    def remind_selection(self):
        if self.partner.on == True:
            self.partner.show_deselected()
        self.show_selected()

    def highlight_choice(self, event):
        if self.on == True:
            self.show_deselected()
        else:
            if self.partner.on == True:
                self.partner.show_deselected()
            self.show_selected()
        return None

    def show_selected(self):
        bg_col = "orange"
        bd_weight = 3
        self.selectframe.config(bd = bd_weight,
                                bg = bg_col)
        self.on = True
        return None

    def show_deselected(self):
        self.selectframe.config(bd = 0)
        self.on = False
        return None


    def get_envelope_pic(self, size):
        imagepath = os.path.join(os.path.dirname(__file__),
                                 "pictures",
                                 "envelope_{}.gif".format(size))
        env_img = tk.PhotoImage(file = imagepath)
        return env_img


    def draw_envelopes(self, prob, x, r, safe, risky, bgs):
        env_configs = self.calc_envelopes(prob, x, r, safe, risky)
        [self.show_env(master, prob, lcol, amt, bgs)
         for master, prob, lcol, amt in env_configs]

        return None

    def draw_certain(self, master):
        imgframe = tk.Frame(master, bg = self.certain_col)
        imgframe.grid(row = 0, column = 0, pady = 1)

        l1 = tk.Label(imgframe, 
                      image = self.big_env_img,
                      text = "",
                      compound = tk.CENTER, bd = 0)
        l1.image = self.big_env_img
        l1.grid(padx = 3, pady = 3, sticky = 'N')
        l1.bind("<k>", self.highlight_choice)
        return l1

    def show_envs(self, master):
        rows = [1, 2, 3, 4, 5, 5, 4, 3, 2, 1]
        cols = [0] * 5 + [1] * 5

        lab_list = [self.make_single_env(master, row, column)
                    for row, column in zip(rows, cols)]
        return lab_list


    def make_single_env(self, master, rown, col):
        imgframe = tk.Frame(master)
        imgframe.grid(row = rown, column = col, pady = 1)

        l1 = tk.Label(imgframe,
                      image = self.env_img,
                      text = 'Rs {}'.format("Bob"),
                      compound = tk.CENTER)

        l1.image = self.env_img
        l1.grid(padx = 2, pady = 2, sticky = 'N')
        l1.bind("<t>", self.highlight_choice)
        return l1




# root = tk.Tk()
# root.title("Pie")
# w = root.winfo_screenwidth()
# h = root.winfo_screenheight()
# amma = riskPie(root, {'w':w, 'h':h}, tconfig)
