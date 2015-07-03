import csv
import os
import sys
import Tkinter as tk

from shared.startscreen.startscreen import Startscreen
from shared.questionnaire.questionnaire import Questionnaire


class QuestionnaireProgram(tk.Frame):
    def __init__(self, master, qdic):
        tk.Frame.__init__(self, master)
        self.pack(fill = "both", expand = True)

        self.qdic = qdic
        self.root = qdic.get("root")
        mode = qdic.get("test_mode")

        self.startscreen = Startscreen(self,
                                       self.load_questionnaire,
                                       self.root,
                                       mode)

    def load_questionnaire(self, idx_dic):
        """Allows the startscreen to exit and load the questionnaire
        
        qdic is a dictionary of customisable options
        --title
        --stimuli - [(class_object(tk.Frame), tab_name), ...]
        --csv_path - path where the csv definitions are kept
        --data_path - path where data should be stored
        --next function - function to be called after 
          questionnaire is completed
        """

        self.qdic.update(idx_dic)        
        if self.qdic.get("next_function") == "comments":
            self.qdic["next_function"] = self.get_comments

        q = Questionnaire(self, **self.qdic)
        return q

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

        
def run_survey(mode, qoptions):
    root = tk.Tk()
    root.title("Low carbon survey")
    root.attributes("-fullscreen", True)
    survey_options = {"root": root,
                      "test_mode": mode}
    survey_options.update(qoptions)
    survey = QuestionnaireProgram(master = root, qdic = survey_options)
    print "Survey running...ASP"
    root.mainloop()
    return survey
        
