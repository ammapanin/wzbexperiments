import csv
import os
import sys
import Tkinter as tk

lcf_path = os.path.dirname(os.path.abspath(__file__))
code_path = os.path.dirname(lcf_path)
data_path = os.path.join(lcf_path, "data")
comments_path = os.path.join(lcf_path, "comments")

from details.shared.startscreen.startscreen import Startscreen
from details.shared.questionnaire.questionnaire import Questionnaire


class Lcf(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master)
        self.pack(fill = "both", expand = True)

        self.root = master
        self.startscreen = Startscreen(self,
                                  self.load_questionnaire,
                                  kwargs.get("root"))

    def load_questionnaire(self, idx_dic):
        csv_path = os.path.join(lcf_path,
                                "details",
                                "lcf_questionnaire.csv")
        title = "Low Carbon Farming Questionnaire"

        qdic = {"title": title,
                "csv_path": csv_path,
                "data_path": data_path,
                "next_function": self.get_comments}

        qdic.update(idx_dic)

        q = Questionnaire(self, **qdic)


    def get_comments(self):
        variables = ("enumid", "tid", "vid", "interview_wzb.ind.id")
        idx = tuple([self.startscreen.idx_dic.get(v) for v in variables])

        comment_text = "Please enter any comments."
        comment_lab = tk.Label(self,
                             text = comment_text)

        exit_comment = tk.Text(self,
                               width = 50,
                               height = 15,
                               background = "gray")

        info = (idx, exit_comment)
        close = lambda c = exit_comment: self.close_window(info)

        exit_bt = tk.Button(self,
                            text = "End survey",
                            command = close)

        [w.pack(side = "top") for w in (comment_lab,
                                        exit_comment,
                                        exit_bt)]

    def close_window(self, info):
        comment = info[1].get(1.0, "end")
        full_comment = info[0] + (comment,)

        enumid, tid, vid, ind_id = info[0]
        comments_name = "comments_{}_{}_{}.csv".format(enumid, tid, vid)
        fpath = os.path.join(comments_path,
                             comments_name)

        if os.path.isdir(comments_path) == False:
            os.makedirs(comments_path)

        with open(fpath, "a") as commentfile:
            cwrite = csv.writer(commentfile)
            cwrite.writerow(full_comment)

        self.root.destroy()




def run_survey():
    root = tk.Tk()
    root.title("Low carbon survey")
    root.attributes("-fullscreen", True)
    survey = Lcf(root)
    print "LCF survey running...ASP"
    root.mainloop()

    return survey


run_survey()
