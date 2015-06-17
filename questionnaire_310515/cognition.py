import time
import os
import Tkinter as tk
import tkFont

class CognitionTab(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.pack(side = "top", fill = "both", expand = True)

        info_font = tkFont.Font(size = 14)
        self.info = tk.Label(self, 
                        text = ("You will now face a series of tasks. "
                                "These tasks will be times, "
                                "so please pay attention." 
                                "Below are two examples to work through. "
                                "When you are satisfied with understanding, "
                                "please press ENTER to begin"),
                             font = info_font,
                             wrap = 500)
        self.info.pack(side = "top")
        self.enter_idx = self.bind_all("<Return>", self.begin, "+")

    def begin(self, event = ""):
        self.unbind("<Return>", self.enter_idx)
        self.info.pack_forget()
        raven = Raven(self, "dummy")
        stroop = Stroop(self, raven.start_task)
        stroop.start_task()

        
class Task:
    def __init__(self, master, next_task):
        self.answer_dic = dict([(i, {"correct": correct,
                                     "answer": None,
                                     "time": None})
                                for i, correct in self.qid_answers])
        self.questions = enumerate([q for q, a in self.qid_answers])

        self.qidx = tk.IntVar()
        self.qidx.set(0)
        self.start = tk.DoubleVar()
        self.next_task = next_task

    def clock(self, c):
        t = time.time()
        if c == "start":
            self.start.set(t)
        elif c == "stop":
            start = self.start.get()
            return t - start

class Stroop(Task, tk.Frame):
    def __init__(self, master, next_task):
        tk.Frame.__init__(self, master)
        self.pack(side = "top", fill = "both", expand = True)

        stroopfont = tkFont.Font(self, weight = "bold", size = 20)
        self.num_var = tk.StringVar(self)
        self.answer_var = tk.StringVar()
        self.number = tk.Label(self, text = "", font = stroopfont,
                               textvariable = self.num_var)
        self.answer = tk.Entry(self, textvariable = self.answer_var)

        [w.pack(side = "top") for w in (self.number, self.answer)]

        numeric_strings = ("555", "8", "99", "33333",
                           "44", "1111", "5555", "77")

        self.qid_answers = [(i, len(strg))
                            for i, strg in enumerate(numeric_strings)]
        Task.__init__(self, master, next_task)
        self.strings = enumerate(numeric_strings)
        
    def new_number(self):
        try:
            idx, current_string = self.strings.next()
            self.num_var.set(current_string)
            self.qidx.set(idx)
            self.clock("start")
        except StopIteration:
            self.num_var.set("Task complete")
            self.answer.pack_forget()
            def do_pass(self, event = "event"):
                pass
            self.bind_all("<Return>", do_pass)
            self.bt = tk.Button(self, text = "Start new task", 
                                command = self.end_task)
            self.bt.pack(side = "top")
        pass

    def get_answer(self, event = ""):
        idx = self.qidx.get()
        answer = self.answer_var.get()
        if answer != "":
            time_taken = self.clock("stop")
            self.answer_dic[idx]["answer"] = answer
            self.answer_dic[idx]["time"] = time_taken
            self.answer_var.set("")
            self.new_number()
        elif answer == "":
            pass
        return None
        
    def end_task(self, event = "event"):
        self.number.pack_forget()
        self.bt.pack_forget()
        self.next_task()
        
    def start_task(self):
        self.next_id = self.answer.bind("<Return>", self.get_answer)
        self.new_number()
        

class Raven(Task, tk.Frame):
    def __init__(self, master, next_task):
        tk.Frame.__init__(self, master)
        self.pack(side = "top", fill = "both", expand = True)

        stimuli = enumerate(self.get_images())
        qobjects_list = [(i, self.make_choice(i, img, correct))
                         for i, (img, correct) in stimuli]
        self.qobjects = dict(qobjects_list)
        self.qid_answers = [(i, q.get("correct"))
                            for i, q in qobjects_list]
        Task.__init__(self, master, next_task)
        
    def get_images(self):
        raven_files = [os.path.join("raven", f)
                       for f in os.listdir("raven") if f[-3:] == "gif"]

        raven_files.sort(key = lambda x: int(x.split("_")[0][11:]))
        correct = [self.get_correct(f) for f in raven_files]

        return zip(raven_files, correct)

    def get_correct(self, fname):
        base, end = fname.split("_")
        correct = end.strip(".png")
        return correct

    def make_choice(self, qidx, fname_image, correct):
        stimuli_img = tk.PhotoImage(file = fname_image)
        values = range(1, 7)
        self.stimuli = stimuli = tk.Label(self, image = stimuli_img,
                                name = "q" + str(qidx) + "stimuli")
        self.stimuli.image = stimuli_img

        response = tk.Frame(self, name = "q" + str(qidx) + "response")
        response_var = tk.StringVar(response)
        response_var.set(0)
        bts = [tk.Radiobutton(response,
                              text = val,
                              variable = response_var,
                              value = val)
               for val in values]
        [bt.pack(side = "left") for bt in bts]
        qdic = {"widgets": (stimuli, response),
                "var": response_var,
                "correct": correct}
        return qdic

    def show_choice(self, qidx):
        stimuli, response = self.qobjects.get(qidx).get("widgets")

        fname = ["q" + str(qidx - 1) + i for i in ("stimuli", "response")]
        old_widgets = [self.children.get(f) for f in fname]

        if None not in old_widgets:
            [w.pack_forget() for w in old_widgets]

        packers = {"side": "top",
                   "fill": "both",
                   "expand": True,
                   "anchor": "center"}

        stimuli.pack(**packers)
        response.pack(**packers)

        self.clock("start")

    def go_next(self, event = ""):
        print "Any troubles here?"
        qid_0 = self.qidx.get()
        var_0 = self.qobjects.get(qid_0).get("var")

        if var_0 != 0:
            time = self.clock("stop")

            self.answer_dic[qid_0]["answer"] = var_0.get()
            self.answer_dic[qid_0]["time"] = time

            try:
                qid = self.questions.next()[0]
                self.show_choice(qid)
                self.qidx.set(qid)

            except StopIteration:
                stimuli, response = self.qobjects.get(qid_0).get("widgets")
                [i.pack_forget() for i in (stimuli, response)]
                endfont = tkFont.Font(size = 15, weight = "bold")
                end = tk.Label(self, text = "Task complete", font = endfont)
                end.pack(side = "top")
        elif var_0 == 0:
            pass

    def start_task(self):
        self.show_choice(0)
        self.bind_all("<Return>", self.go_next)
        print "binding"
        

#root = tk.Tk()
#cog = CognitionTab(root)
#raven = Raven(root)
#stroop = Stroop(root)
