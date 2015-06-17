import csv
import os
import Tkinter as tk
import tkFont
import sys

import question
from question import Question
import answer_classes as answers
from cognition import CognitionTab

import traceback

class Questionnaire(tk.Frame):
    def __init__(self, master, **kwargs):
        """Creates a questionnaire object frame.

        Questionnaire initial dic accepts the following options:
        title: the questionnaire title
        csv_path: path to the actual csv questions
        data_path: path to the folder where data will be written
        next_function: function to show the next section

        """

        tk.Frame.__init__(self, master)
        self.pack(fill = "both", expand = True, anchor = "w")

        self.options = kwargs
        self.qorder, self.lab_tab_dic, self.tabs = self.get_structure()
        self.tabs.append("cognition")

        title_frame, q_frame, bt_frame = [tk.Frame(self) for f in range(0, 3)]
        canvas = tk.Canvas(q_frame, bg = "blue", highlightthickness = 0)

        self.make_labels(title_frame)

        q_frame.pack(side = "top", fill = "both", expand = True)
        self.current_lab = tk.StringVar(self)
        self.latest_lab = tk.StringVar(self)

        q_scroll_frame = self.make_question_frame(canvas, q_frame, title_frame)
        self.tab_dic = self.make_tabs(q_scroll_frame)

        self.qobjects = self.make_questions()
        self.qobjects[0].make_active()
        self.qobjects[0].make_current()
        self.cognition = CognitionTab(self.tab_dic.get("cognition"))

        bt_frame.pack(side = "top")
        self.complete_bt = tk.Button(bt_frame,
                                     text = "Validate",
                                     command = self.validate)
        self.complete_bt.pack(side = "bottom")


    def make_tabs(self, question_frame):
        tab_frames = dict([(txt,
                            tk.Frame(question_frame))
                           for txt in self.tabs])
        return tab_frames

    def show_tab(self, event, tab_name):
        [t.pack_forget() for t in self.tab_dic.values()]
        tab = self.tab_dic.get(tab_name)
        tab.pack(side = "left")
        return None

    def make_tab_frames(self, title_master, q_master):
        label_frame = tk.Frame(title_master)
        tab_frame = tk.LabelFrame(q_master)
        [f.pack(side = "top") for f in (label_frame, tab_frame)]

        tab_labs = [tk.Label(label_frame, text = txt.capitalize())
                    for txt in self.tabs]
        [t.pack(side = "left") for t in tab_labs]

        [t.bind("<Button-1>",
                lambda event, x = tab_name: self.show_tab(event, x))
         for tab_name, t in zip(self.tabs, tab_labs)]
        return tab_frame

    def make_question_frame(self, canvas, q_frame, title_frame):
        frame = tk.LabelFrame(canvas)
        tab_frame = self.make_tab_frames(title_frame, frame)

        canvas.pack(side = "left", fill = "both", expand = True)
        vsb = tk.Scrollbar(q_frame,
                           command = canvas.yview)
        vsb.pack(side = "right", fill = "y")

        canvas.configure(yscrollcommand = vsb.set)
        canvas.create_window((4,4),
                             window = frame,
                             anchor = "nw",
                             tags = "frame")

        def on_frame_configure(event):
            canvas.configure(scrollregion = canvas.bbox("all"))
            return None
        def on_canvas_configure(event):
            canvas.itemconfig("frame", width = event.width)
            return None

        canvas.bind("<Configure>",
                    on_canvas_configure)
        frame.bind("<Configure>",
                   on_frame_configure)
        return frame

    def make_frames(self):
        f1, f2, f3 = [tk.Frame(self) for f in range(0, 3)]
        f1.pack(side = "top")
        f3.pack(side = "bottom")
        canvas, qframe = self.make_question_frame(self)
        return f1, qframe, f3

    def make_labels(self, master):
        master.pack(side = "top")
        title_font = tkFont.Font(size = 20, weight = "bold")
        title_text = self.options.get("title")
        title = tk.Label(master, text = title_text, font = title_font)
        title.pack(side = "top", pady = 10)
        self.invalid_label = tk.Label(master)
        return None

    def create_conditions(self, line_dic, ncond):
        conditions = ("cond_{}",
                      "cond_{}_type",
                      "cond_{}_values",
                      "cond_{}_labels",
                      "cond_{}_texts")
        conditions_list = list()

        stock_dic = {"members": self.options.get("members_list")}
            
        for n in range(1, ncond + 1):
            keys = [l.format(n) for l in conditions]
            dependence_type = line_dic.get(keys[1])

            stock = line_dic.get(keys[2])
            if stock in stock_dic.keys():
                line_dic[keys[2]] = ",x".join(stock_dic.get(stock))
   

            if line_dic.get("type") != "check":
                cdic = dict()
                cdic["logic"] = line_dic.get(keys[0])
                cdic["type"] = dependence_type
                cdic["value"] = line_dic.get(keys[2])
                cdic["labels"] = line_dic.get(keys[3]).split(",x")
                cdic["texts"] = line_dic.get(keys[4]).split(",x")

                conditions_list.append(cdic)

            elif line_dic.get("type") == "check":
                conditionals = line_dic.get(keys[2]).split(",x")
                label_lists = line_dic.get(keys[3]).split(",x")
                text_lists = line_dic.get(keys[4]).split(",x")

                value_dic = {"applicable": True,
                             "text": "1,x0",
                             "table": True}

                cdics = [dict() for i in conditionals]

                for i, d in enumerate(cdics):
                    try:
                        depend_texts = text_lists[i].split(",z")
                    except IndexError:
                        depend_texts = None

                    d.update({"logic": "equal",
                              "value": value_dic[dependence_type],
                              "type": dependence_type,
                              "texts": depend_texts})

                    if dependence_type == "table":
                        d["value"] = conditionals[i]
                        d["labels"] = label_lists

                    else:
                        d["labels"] = label_lists[i].split(",z"),

                conditions_list.extend(cdics)

        return conditions_list

    def process_csv_line(self, headers, line):
        """Converts csv line into a dictionary object

        question_text: string
        type: string
        label: string
        options: list
        conditions: list of dictionaries
        -cdics: dictionaries
        --logic, type, value, labels(list), dependence text

        returns a tuple: qview, answer_dic
        """

        basics = ("question_text", "type", "label", "options")
        line_dic = dict(zip(headers, line))
        try:
            qdic = dict()
            qdic.update(dict([(b, line_dic.get(b)) for b in basics]))
            qdic["qview"] = qview = line_dic.get("qview")
            qdic["tab"] = self.tab_dic.get(line_dic.get("tab"))

            #options
            qoptions = qdic.get("options")
            if qoptions != None:
                qdic["options"] = qoptions.split(",x")
            if qoptions == "members":
                member_list = self.options.get("members_list")
                qdic["options"] = member_list

            #conditions
            qdic["conditions"] = list()
            ncond = int(line_dic.get("nconditions"))
            if ncond > 0:
                    conds = self.create_conditions(line_dic, ncond)
                    qdic["conditions"].extend(conds)
            elif ncond == 0:
                pass

            #dynamic table
            if line_dic.get("type") == "dynamic_text":
                qdic["str_table"] = line_dic.get("cond_1_values") 
        except Exception as e:
            print "Problem with: ", line_dic.get("label")
            print traceback.print_exc(e)

        return qview, qdic

    def get_structure(self):
        order_csv = self.options.get("order_path")
        qlabs = list()
        qtabs = dict()

        with open(order_csv) as csvfile:
            qlines = csv.reader(csvfile)
            headers = qlines.next()
            tab_order = qlines.next()[0].split(",x")
            for ql, qt, qname in qlines:
                qlabs.append(ql)
                qtabs.update({ql:{"tab": qt, "text": qname}})
        
        tab_from_order = [v.get("tab") for v in qtabs.values()]
        all_tabs = set(tab_from_order) - set(tab_order)
        if len(all_tabs) != 0:
            print "Missing tabs :", all_tabs
        return qlabs, qtabs, tab_order

    def get_questions(self):
        """Gets question definitions from csv files

        Returns list of adics, list of qorders, dictionary of qtabs
        """
        questions = list()
        question_csv = self.options.get("csv_path")

        with open(question_csv) as csvfile:
            qlines = enumerate(csv.reader(csvfile))
            headers = qlines.next()[1]
            for qidx, qinfo in qlines:
                qdic = self.process_csv_line(headers, qinfo)
                questions.append(qdic)
        return questions

    def create_singles(self, qdics):
        singles = dict([(q["label"], q)
                        for i, q in qdics if i == "single"])
        [q.update({"qlabel": q.get("label")})
         for q in singles.values()]
        return singles

    def create_tables(self, qdics, qtabs):
        """ Sort out list of qdics into question tables
        Returns list of question dictionaries ready for Question(*)
        """
        def is_table(string):
            return string[0:5] == "table"

        tab_names = set([i for i, q in qdics if is_table(i) == True])
        tables = dict([(t, {"qlabel": t,
                            "questions":list(),
                            "qview": "table",
                            "tab": self.tab_dic.get(qtabs.get(t).get("tab")),
                            "question_text": qtabs.get(t).get("text"),
                            "conditions": []})
                       for t in tab_names])
        [tables[i]["questions"].append(q)
         for i, q in qdics if is_table(i) == True]
        return tables

    def make_questions(self):
        """Creates a list of question objects from list of qdics
           Transforms groups of answers to questions

        Question object views could either be either 'tables' or 'single'
        Question objects require a dictionary containing the following:

        qidx: question number
        qlabel: question label, maybe different from answer label
        #answer_var: a tk.StringVar for the questions
        current_lab_var: questionnaire level current var
        latest_lab_var: questionnaire level latest var
        tab: frame selected from self.tab_dic

        - self.get_questions() returns a list of qdics
        - group labs by tables, etc
        - set question varoiables form above (qidx, qlab, current/latest, tab)

        After all qidx have been set, add following as attribute of Question
        i)   label to idx dic
        ii)  label to objects dic
        iii) question_cycle
        """

        qdics = self.get_questions()

        responses = dict()
        tables = self.create_tables(qdics, self.lab_tab_dic)
        singles = self.create_singles(qdics)

        responses.update(tables)
        responses.update(singles)
        
        
        questions = list()
        for qlab in self.qorder:
            try:
                questions.append(responses[qlab])
            except KeyError as e:
                print "Problem with: ", qlab
                print traceback.print_exc(e)

        #questions = [responses.get(qlab) for qlab in qorders]
        [dic.update({"current_lab_var" : self.current_lab,
                     "latest_lab_var": self.latest_lab,
                     "qidx": i})
         for i, dic in enumerate(questions, 1)]

        self.trial_questions = questions
        qobjects = [Question(**qdic) for qdic in questions]

        self.qlab_object = dict([(q.qlabel, q) for q in qobjects])
        self.qlab_idx = dict([(q.qlabel, q.qidx) for q in qobjects])
        self.question_cycle = [(q.qlabel, q.qidx) for q in qobjects]

        for q in qobjects:
            q.lab_object = self.qlab_object
            q.lab_idx = self.qlab_idx
            q.qcycle = self.question_cycle

            if q.options.get("type") == "dynamic_text":
                tab_str = q.options.get("str_table")
                q.answer.options["table"] = self.qlab_object.get(tab_str).answer
        return qobjects

    def go_next(self, event):
        lab_current = self.current_lab.get()
        lab_last = self.latest_lab.get()

        labs_cycle = [l[0] for l in self.question_cycle]
        pos = labs_cycle.index(lab_last)
        pos_next = pos + 1

        try:
            lab_next = labs_cycle[pos_next]
            qobj_next = self.qlab_object.get(lab_next)
            qobj_next.make_active()
            qobj_next.make_current()
        except IndexError:
            # self.end_questionnaire()
            print "Questionnaire completed"
        return None


    def set_key_bindings(self):
        self.bind_all("<Return>", self.go_next)

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
        #go_next = self.options.get("next_function")
        self.save_answers()
        self.pack_forget()
        go_next()

        print "Questionnaire completed"
        return None



def dummy_next():
    print "Finished with the questionnaire test"
    return None

def test_run():
    reload(answers)
    reload(question)
    reload(answer_classes)

    test_dict = {"title": "Trial",
                 "csv_path": "household_details.csv",
                 "order_path": "hh_order.csv",
                 "data_path": "test_data",
                 "next_function": dummy_next,
                 "members": ["Pauline", "Ruta", "Nora"]}


    root = tk.Tk()
    root.attributes("-fullscreen", True)
    tls = Questionnaire(root, **test_dict)

    print("done making questionnaire")
    return tls




#sai = test_run()

