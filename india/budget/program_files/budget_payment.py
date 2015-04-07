# Payment code for budget class
# Last updated: 26 January 2015

import Tkinter as tk
import tkMessageBox
from dateutil.relativedelta import relativedelta
import tkFont
from datetime import datetime
import os
import csv

class BudgetPayment():
    def __init__(self):
        pass

    def make_payment_objects(self):
        self.sp_screen.pack_forget()
        [screen.scale_balls()
         for screen in (self.riskscreen, self.timescreen)]

        self.question_list = tk.Listbox(self.payment_frame,
                                        selectmode = "browse")
        self.question_list.focus()
        self.question_list.grid(row = 0, column = 0, rowspan = 2)

        [self.question_list.insert("end", i)
         for i in range(1, self.total_questions + 1)]

        self.pop_bt = tk.Button(self.payment_frame,
                                text = "OK",
                                command = self.get_question)
        self.pop_bt.grid(row = 0, column = 3)

        payfont = tkFont.Font(size = 15, weight = "bold")
        self.info_frame_0 = tk.Label(self.payment_frame,
                                     font = payfont)
        self.info_frame_0.grid(row = 0, column = 2)



    def get_question(self):
        self.wq_idx = int(self.question_list.curselection()[0]) + 1
        self.question_list.config(state = "disabled")
        self.wt = self.treatment_question_dic[self.wq_idx][0]
        self.q = self.treatment_question_dic[self.wq_idx][1]
        self.wq = self.treatment_dic[self.wt]["data"][self.q]

        self.remember_frame()
        return None

    def remember_frame(self):

        person = self.idx_data["hh_name"]
        screen = self.treatment_dic[self.wt]["screen"]

        screen.qtimes = self.wq["tL"], self.wq["tR"]
        screen.qprices = self.wq["pL"], self.wq["pR"]
        screen_nr = self.wq["nR"]

        screen.treatment = self.wt
        screen.scale.set(screen_nr)
        screen.nr_fixed = screen_nr
        screen.scale.config(command = screen.fix_amount)
        screen.update_times(screen.qtimes)
        screen.update_prices(screen.qprices)
        screen.update_allocation("event")


        payinfotext = "In question {}, {} answered a {} question. {} will {}"
        direct = "receive two direct payments with the amounts shown."
        lottery = "now play a lottery with the amounts shown."
        t = payinfotext.format(self.wq_idx, person, self.wt.upper(), person, {})

        if self.wt == "time":
            tkMessageBox.showinfo("", t.format(direct))
            self.show_payment()

        if self.wt == "risk":
            tkMessageBox.showinfo("", t.format(lottery))
            self.show_lottery()

        screen.mainframe.pack()

    def show_lottery(self):
        lotterytext = ("Play the lottery: {} red balls for Rs {} "
                       "and {} yellow balls for Rs {}.")
        self.info_frame_0.config(text = \
                                 lotterytext.format(self.riskscreen.prob,
                                                    self.wq["aL"],
                                                    10 - self.riskscreen.prob,
                                                    self.wq["aR"]))

        self.pay_lotteryvar = tk.IntVar(self.payment_frame)
        self.bts_payframe = tk.LabelFrame(self.payment_frame, bg = "firebrick")
        self.bts_payframe.grid(row = 1, column = 1)

        bts = [tk.Radiobutton(self.bts_payframe,
                              text = "Rs {}".format(int(amt)),
                              value = v,
                              variable = self.pay_lotteryvar)
               for amt, v in zip((self.wq['aL'], self.wq['aR']),
                              (1, 2))]
        [bt.grid(row = 0, column = i) for i, bt in enumerate(bts)]

        self.pop_bt.config(command = self.show_payment)
        self.pop_bt.grid(row = 1, column = 2)


    def show_payment(self):

        tomorrow = datetime.today() + relativedelta(days = 1)

        if self.wt == "risk":
            winamt_dic = {1: self.wq['aL'], 2: self.wq['aR']}
            win_idx = self.pay_lotteryvar.get()
            a_win = winamt_dic[win_idx]
            payment_text = "{} will receive {} on {}."

            tomorrow_text = tomorrow.strftime("%d/%m/%y")
            ptext = payment_text.format(self.wq["hh_name"],
                                        int(a_win),
                                        tomorrow_text)
            winnings = [a_win, "NA"]
            timing = [tomorrow_text, "NA"]

        if self.wt == "time":
            payment_text = "{} will receive Rs {} on {} AND Rs {} on {}."

            paydate_1 = (tomorrow + \
                        relativedelta(months = self.wq["tL"])).strftime("%d/%m/%y")
            paydate_2 = (tomorrow + \
                        relativedelta(months = self.wq["tR"])).strftime("%d/%m/%y")

            ptext = payment_text.format(self.wq["hh_name"],
                                       int(self.wq["aL"]),
                                       paydate_1,
                                       int(self.wq["aR"]),
                                       paydate_2)
            winnings = [self.wq.get(i) for i in ("aL", "aR")]
            timing = [paydate_1, paydate_2]

        self.info_frame_0.config(text = ptext)

        fname = "payments_{}.csv".format(self.idx_data["vid"])
        paymentfilename = os.path.join(self.paymentsPATH, fname)

        colnames = ("tid", "vid","enumid",
                    "wzb.hh.id", "wzb.ind.id", "time", "date",
                    "interviewed_name", "hh_name", "hh_name_corrected",
                    "election_id", "election_corrected",
                    "ration_nr", "ration_corrected",
                    "interviewed_election", "interviewed_ration")

        paynames = ("pay_treatment",
                    "payment_1",
                    "payment_2",
                    "paydate_1",
                    "paydate2")

        paydata = [self.idx_data.get(cname)
                   for cname in colnames]

        print "writing payment...{}".format(paymentfilename)

        if os.path.isfile(paymentfilename) == False:
            with open(paymentfilename, 'w') as outfile:
                pwrite = csv.writer(outfile)
                pwrite.writerow(colnames + paynames)

        with open(paymentfilename, 'a') as outfile:
            pwrite = csv.writer(outfile)
            pwrite.writerow(paydata + [self.wt] + winnings + timing)

        self.pop_bt.config(command = self.close_window)
        return None

    def close_window(self):
        self.root.destroy()
