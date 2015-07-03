import os
import datetime
import csv
import Tkinter as tk
import tkFont
import tkMessageBox

import pkg.dropdown as dropdown

class Startscreen(tk.Frame):
    def __init__(self, master, start_function, **kwargs):
        tk.Frame.__init__(self, master)

        self.test_mode = kwargs.get("test_mode")
        self.root = kwargs.get("root")

        header_frame = tk.Frame(self)
        header_frame.pack(side = "top", expand = True, fill = "both")

        content_frame = tk.Frame(self)
        content_frame.pack(side = "top", expand = True, fill = "both")

        header_font = tkFont.Font(size = 15, weight = "bold")
        heading = ("Please select the following information. "
                   "When you have finished, pressed validate."
                   "\nIf there are any other corrections, "
                   "please note them at the end of the experiment.")
        head_lab = tk.Label(header_frame,
                            text = heading,
                            font = header_font,
                            wraplength = 1000)
        head_lab.pack(side = "top", fill = "both")
        self.pack()

       
        self.validation_frame = tk.Frame(content_frame)
        self.validation_frame.pack(side = "left",
                                   fill = "x",
                                   expand = True,
                                   padx = 5,
                                   pady = 10)

        dropdown_frame = tk.Frame(content_frame)
        dropdown_frame.pack(side = "left",
                            expand = True,
                            anchor = "nw",
                            pady = 10,
                            fill = "both")

        if __name__ == "__main__":
            print "Running from the local path!"
            shared = ('/Users/aserwaahWZB/Projects/GUI Code/'
                      'india experiments/Current version/details/shared')
        else:
            shared = os.path.dirname(os.path.abspath(__file__))
        details = os.path.dirname(shared)
        self.identifiers_path = os.path.join(details, "data_identifiers")
        self.show_experiment = start_function

        self.dropdown = dropdown.Dropdowns(dropdown_frame)
        self.bt = tk.Button(self.validation_frame,
                       text = "Validate",
                       command = self.do_validations)
        self.bt.pack(side = "bottom", anchor = "sw")


    def do_validations(self):

        old_frame = self.validation_frame.children.get("warning")
        if old_frame != None:
            old_frame.destroy()

        warnings_frame = tk.Frame(self.validation_frame, name = "warning")
        warnings_frame.pack(side = "top",
                            fill = "both",
                            expand = True,
                            anchor = "n")

        sections = (self.dropdown,
                    self.dropdown.correct.add,
                    self.dropdown.interview.interviewee)

        warnings = list()
        for s in sections:
            warnings.extend(s.validate())

        if self.test_mode == "DEBUG":
            warnings = list()

        if len(warnings) == 0:
            idx_dic = self.get_data()
            self.write_idx(idx_dic)
            p = self.dropdown.interview.interviewee.participate.get()
            if p == True:
                new_command = lambda d = idx_dic: self.begin_experiment(d)
                self.bt.config(text = "Start experiment",
                               command = new_command)
            if p == False:
                self.get_reason(idx_dic)

        for w in warnings:
            lab = tk.Label(warnings_frame, text = w, fg = "red")
            lab.pack(side = "top", anchor = "w", pady = 2)

        return warnings

    def get_data(self):
        variables = ("enumerator",
                     "taluk",
                     "village",
                     "enumid",
                     "tid",
                     "vid",
                     "wzb.hh.id",
                     "head_name",
                     "head_ration_nr",
                     "head_election_id",
                     "hh_participation",
                     "head_name_corrected",
                     "head_ration_corrected",
                     "head_election_corrected",
                     "interview_name",
                     "interview_wzb.ind.id",
                     "interview_other_name",
                     "interview_other_ration",
                     "interview_other_election",
                     "interview_other_relation",
                     "date",
                     "time",
                     "members_list")

        not_found = "not.found"

        idx = tuple([v.get()
                     for v in self.dropdown.dropdown_vars[0:3]])

        enumid = self.dropdown.name_enumid.get(idx[0])
        tid = self.dropdown.name_tid.get(idx[1])
        vid = self.dropdown.name_vid.get(idx[2])

        hh_name = self.dropdown.dropdown_vars[3].get()
        hh = self.dropdown.households.get(hh_name)
        wzb_hh_id = hh.get("hid", not_found)
        ration = hh.get("ration_nr", not_found)
        election = hh.get("election_id", not_found)
        members_list = hh.get("members_list", not_found)

        correct = self.dropdown.correct.add
        head_corrections = tuple([v.get() for v in correct.entry_vars])

        interview = self.dropdown.interview.interviewee
        interview_name = interview.member_var.get()
        wzb_ind_id = hh.get("members").get(interview_name, not_found)
        interview_corrections = tuple([v.get()
                                       for v in interview.correction_vars])

        p = self.dropdown.interview.interviewee.participate.get()

        timenow = datetime.datetime.now()
        time_string = timenow.strftime("%H:%M")
        date_string = timenow.strftime("%d/%m/%y")

        values = idx + (enumid, tid, vid) +\
                 (wzb_hh_id, hh_name, ration, election, p) + \
                 head_corrections + (interview_name, wzb_ind_id) +\
                 interview_corrections + (date_string, time_string, members_list) 

        idx_dic = dict(zip(variables, values))

        return idx_dic


    def get_reason(self, idx_dic):
        name = self.dropdown.dropdown_vars[3].get()

        exit_text = "Are you sure {} does not wish to participate?"
        exit_yes = tkMessageBox.askyesno("Non-participation",
                                         exit_text.format(name))

        if exit_yes == True:
            exit_frame = tk.Frame(self.validation_frame, name = "warning")
            exit_frame.pack(side = "top")

            reason_text = "Please enter the reason."
            exit_lab = tk.Label(exit_frame,
                                text = reason_text.format(name))

            exit_comment = tk.Text(exit_frame,
                                   width = 50,
                                   height = 15,
                                   background = "gray")

            new_command = lambda w = exit_comment, d = idx_dic:\
                          self.exit_experiment(w, d)
            self.bt.config(text = "Exit experiment", command = new_command)

            widgets = (exit_lab, exit_comment)
            [w.pack(side = "top", anchor = "w") for w in widgets]

        elif exit_yes == False:
            pass
        return None


    def exit_experiment(self, exit_comment, idx_dic):
        tid = idx_dic.get("tid")
        vid = idx_dic.get("vid")

        participate_name = "participate_{}_{}.csv".format(tid, vid)
        participate_path = os.path.join(self.identifiers_path,
                                        participate_name)

        if os.path.isdir(self.identifiers_path) == False:
            os.makedirs(self.identifiers_path)

        reason = exit_comment.get(1.0, "end").strip()
        non_participate = idx_dic.values() + [reason]
        with open(participate_path, "a") as idxfile:
            idxwrite = csv.writer(idxfile)
            idxwrite.writerow(non_participate)

        self.root.destroy()

    def write_idx(self, idx_dic):
        idx_cols = ("tid",
                    "vid",
                    "taluk",
                    "village",
                    "enumerator",
                    "date",
                    "time",
                    "wzb.hh.id",
                    "interview_wzb.ind.id",
                    "head_name",
                    "hh_participation",
                    "head_election_id",
                    "head_ration_nr",
                    "head_name_corrected",
                    "head_election_corrected",
                    "head_ration_corrected",
                    "interview_name",
                    "interview_other_name",
                    "interview_other_ration",
                    "interview_other_election",
                    "interview_other_relation")


        individual = [idx_dic.get(tag) for tag in idx_cols]

        tid = idx_dic.get("tid")
        vid = idx_dic.get("vid")

        idxname = "budget_{}_{}.csv".format(tid, vid)
        idxpath = os.path.join(self.identifiers_path, idxname)

        if os.path.isdir(self.identifiers_path) == False:
            os.makedirs(self.identifiers_path)

        with open(idxpath, "a") as idxfile:
            idxwrite = csv.writer(idxfile)
            idxwrite.writerow(individual)

        print "Individual identifying data appended to ", idxname

        return None


    def begin_experiment(self, idx_dic):
        self.pack_forget()
        self.show_experiment(idx_dic)
        return None


def test_startscreen():

    def dummy_start(idx):
        print "Testing over"

    root = tk.Tk()
    a = Startscreen(root, dummy_start, root)
    return a
