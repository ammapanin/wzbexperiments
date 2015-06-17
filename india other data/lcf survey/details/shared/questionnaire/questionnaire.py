import csv
import os
import Tkinter as tk
import tkFont

import answer_classes as answers


class Question(tk.LabelFrame):
    def __init__(self, master, **kwargs):
        tk.LabelFrame.__init__(self, master)
        self.pack(fill = "x", expand = True, anchor = "w",
                  pady = 5, padx = 2b)
        self.options = kwargs

        self.answer_var = tk.StringVar(self)
        self.answer_var.set("x99")
        self.options["answer_var"] = self.answer_var

        self.make_text_label()
        self.make_answer_box()

    def been_answered(self):
        a = self.answer_var.get()
        q = self.options.get("qidx")
        return q, a != "x99"

    def make_text_label(self):
        title_font = tkFont.Font(size = 15)
        lab_text = self.options.get("question_text")
        lab_num = self.options.get("qidx")

        qtext = "{}. {}".format(lab_num, lab_text)
        lab = tk.Label(self,
                       text = qtext)
        lab.grid(row = 0)


    def make_answer_box(self):
        answer_frame = tk.Frame(self)
        answer_frame.grid(row = 1, sticky = "w")

        answer_class = answers.classes.get(self.options.get("type"))
        answer = answer_class(answer_frame, **self.options)


class Questionnaire(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master)
        self.pack(fill = "both", expand = True, anchor = "w")

        self.options = kwargs
        title_frame, question_frame, bt_frame = self.make_frames()

        self.qobjects = self.make_questions(question_frame)

        self.make_labels(title_frame)
        self.complete_bt = tk.Button(bt_frame,
                                     text = "Validate",
                                     command = self.validate)
        self.complete_bt.pack(side = "bottom")


    def make_question_frame(self):
        canvas = tk.Canvas(self, highlightthickness = 0)

        frame = tk.Frame(canvas)
        vsb = tk.Scrollbar(self,
                           command = canvas.yview)

        frame.pack(side = "left", fill = "both", expand = True)
        vsb.pack(side = "right", fill = "y")

        canvas.create_window((4,4),
                             window = frame,
                             anchor = "nw",
                             tags = "frame")
        canvas.configure(yscrollcommand = vsb.set)

        def on_frame_configure(event):
            canvas.configure(scrollregion = canvas.bbox("all"))
            return None

        frame.bind("<Configure>",
                   on_frame_configure)

        return canvas, frame


    def make_frames(self):
        f1, f2 = [tk.Frame(self) for f in range(0, 2)]
        canvas, qframe = self.make_question_frame()

        f1.pack(side = "top")
        canvas.pack(side = "top", fill = "both", expand = True)
        f2.pack(side = "top")

        return f1, qframe, f2

    def make_labels(self, master):
        title_font = tkFont.Font(size = 20, weight = "bold")
        title_text = self.options.get("title")
        title = tk.Label(master, text = title_text, font = title_font)
        title.pack(side = "top", pady = 10)
        self.invalid_label = tk.Label(master)

    def get_questions(self):
        questions = list()
        question_csv = self.options.get("csv_path")
        with open(question_csv) as csvfile:
            qlines = enumerate(csv.reader(csvfile))

            headers = qlines.next()[1]
            for qidx, qinfo in qlines:
                qdic = dict(zip(headers, qinfo))
                qdic["qidx"] = qidx

                qoptions = qdic.get("options")
                if qoptions != None:
                    qdic["options"] = qoptions.split(",x")
                questions.append(qdic)
        return questions

    def make_questions(self, master):
        questions = self.get_questions()
        qobjects = [Question(master, **qdic)
                    for qdic in questions]
        return qobjects

    def validate(self):
        questions = dict([q.been_answered()
                          for q in self.qobjects])
        invalid = [key for key, value in questions.items()
                   if value == False]

        if len(invalid) == 0:
            self.complete_bt.config(text = "Complete",
                                    command = self.complete_questionnaire)
        elif len(invalid) > 0:
            self.request_validations(invalid)
        return questions

    def request_validations(self, invalid_list):
        qlist = str(invalid_list[0])
        if len(invalid_list) > 1:
            for qid in invalid_list[1:]:
                qlist += ", {}".format(qid)

        invalid_text =  "Please answer questions {}".format(qlist)
        self.invalid_label.config(text = invalid_text)
        self.invalid_label.pack(side = "top")

    def save_answers(self):
        data_path = self.options.get("data_path")
        identifiers = ("tid", "vid", "interview_wzb.ind.id")
        tid, vid, hid = [self.options.get(idx) for idx in identifiers]

        fname = "lcf_{}_{}_{}".format(tid, vid, hid)
        answer_path = os.path.join(data_path, fname)

        label_answers = [(q.options.get("label"),
                          q.answer_var.get()) for q in self.qobjects]

        idx_labels = ["tid", "vid", "enumid",
                      "wzb.hh.id", "interview_wzb.ind.id"]
        idx_values = [self.options.get(l) for l in idx_labels]

        labels = idx_labels + [obj[0] for obj in label_answers]
        answers = idx_values + [obj[1] for obj in label_answers]

        if os.path.exists(data_path) == False:
            os.mkdir(data_path)

        with open(answer_path, "w") as datafile:
            d = csv.writer(datafile)
            d.writerow(labels)
            d.writerow(answers)

        return None

    def complete_questionnaire(self):
        go_next = self.options.get("next_function")
        self.save_answers()
        self.pack_forget()
        go_next()

        print "Questionnaire completed"
        return None




def test_run():
    reload(answers)
    root = tk.Tk()
    tls = Questionnaire(root)

    print("done making questionnaire")
    return tls


#sai = test_run()
