import time
import os
import Tkinter as tk
import tkFont


class CognitionTab(tk.Frame):
    def __init__(self, master, task):
        tk.Frame.__init__(self, master)
        self.pack(side = "top", fill = "both", expand = True)

        self.base = os.path.dirname(os.path.abspath(__file__))

        self.practice_frame, self.main_frame = [tk.Frame(self) for i in (0, 1)]

        info_font = tkFont.Font(size = 14)
        self.info = tk.Label(self,
                        text = ("You will now face a series of tasks. "
                                "These tasks will be timed, "
                                "so please pay attention. "
                                "Below are two examples to work through. "
                                "When you are satisfied with understanding, "
                                "please press ENTER to begin"),
                             justify = "left",
                             font = info_font,
                             wrap = 550)

        instructions_font = tkFont.Font(weight = "bold")
        self.instructions = tk.Label(self, 
                                     font = instructions_font,
                                     text = task.extra_info,
                                     justify = "left",
                                     wrap = 550)

        self.info.pack(side = "top", anchor = "w")
        self.instructions.pack(side = "top", pady = 3, anchor = "w")

        self.practice_lab = tk.Label(self,
                                     text = "This is a practice round",
                                     bg = "orange")
        self.practice_lab.pack(side = "top", pady = 3)
        self.begin_bt = tk.Button(self, text = "Start real round",
                                  command = self.start_real)
        self.begin_bt.pack(side = "bottom")

        self.practice_frame.pack(side = "bottom", fill = "both")
        self.main_frame.pack(side = "top", fill = "both")

        self.practice = task(self.practice_frame, "practice", self.base)
        self.real = task(self.main_frame, "real", self.base)
        self.practice.pack()

    def start_real(self):
        self.practice_lab.config(text = "This is the real round",
                                 bg = "lawn green")
        self.practice.pack_forget()
        self.real.pack()
        self.begin_bt.pack_forget()

class Task:
    def __init__(self, master, base_path):
        self.answer_dic = dict([(i, {"correct": correct,
                                     "answer": None,
                                     "time": None})
                                for i, correct in self.qid_answers])
        self.questions = enumerate([q for q, a in self.qid_answers])

        self.qidx = tk.IntVar()
        self.qidx.set(0)
        self.start = tk.DoubleVar()
        self.click_id = self.bind_class(self.name + "cognition_click",
                                        "<Button-1>", 
                                        self.make_binding, "+")
 
    def make_binding(self, event):
        print self.click_id
        print self.name
        #self.unbind("<Button-1>", self.click_id)
        print "click unbound, enter bound"
        self.enter_id = self.bind_all("<Return>", self.go_next)

    def clock(self, c):
        t = time.time()
        if c == "start":
            self.start.set(t)
        elif c == "stop":
            start = self.start.get()
            return t - start

class StroopTask(Task, tk.Frame):
    extra_info = ("In this task you must state " 
                  "the correct number of digits")

    def __init__(self, master, mode, base):
        tk.Frame.__init__(self, master)
        #self.pack(side = "top", fill = "both", expand = True)
        self.name = "stroop" + str(mode)
        stroopfont = tkFont.Font(self, weight = "bold", size = 20)
        self.num_var = tk.StringVar(self)
        self.answer_var = tk.StringVar()
        self.number = tk.Label(self, text = "", font = stroopfont,
                               textvariable = self.num_var)
        self.answer = tk.Entry(self, textvariable = self.answer_var)
        [w.pack(side = "top") for w in (self.number, self.answer)]

        for w in (self.answer, self.number):
            w.bindtags((self.name + "cognition_click",) + w.bindtags())

        if mode == "real":
            numeric_strings = ("555", "8", "99",
                               "44", "1111", "5555", "77", 
                               "222", "33", "111")

        elif mode == "practice":
            numeric_strings = ("66", "777", "1", "222")


 
        self.qid_answers = [(i, len(strg))
                            for i, strg in enumerate(numeric_strings)]
        Task.__init__(self, master, base)
        self.strings = enumerate(numeric_strings)
        self.new_number()


    def new_number(self):
        try:
            idx, current_string = self.strings.next()
            self.num_var.set(current_string)
            self.qidx.set(idx)
            self.clock("start")
        except StopIteration:
            self.num_var.set("Task complete")
            self.unbind("<Return>", self.enter_id)
            self.answer.pack_forget()

    def go_next(self, event = ""):
        idx = self.qidx.get()
        answer = self.answer_var.get()
        if answer != "":
            time_taken = self.clock("stop")
            self.answer_dic[idx]["answer"] = answer
            self.answer_dic[idx]["time"] = time_taken
            self.answer_var.set("")
            self.new_number()
        elif answer == "":
            print "troubles"
            pass
        return None

    def end_task(self, event = "event"):
        self.number.pack_forget()
        self.bt.pack_forget()
        self.next_task()

    def start_task(self):
        self.next_id = self.answer.bind("<Return>", self.get_answer)
        self.new_number()


class RavenTask(Task, tk.Frame):
    extra_info = ("In this task you must select the picture that " 
                  "best completes the image.")

    def __init__(self, master, mode, base):
        tk.Frame.__init__(self, master)
        self.base = base

        self.name = "raven" + str(mode)
        stimuli = enumerate(self.get_images(mode))
        qobjects_list = [(i, self.make_choice(i, img, correct))
                         for i, (img, correct) in stimuli]
        self.qobjects = dict(qobjects_list)
        self.qid_answers = [(i, q.get("correct"))
                            for i, q in qobjects_list]
    
        Task.__init__(self, master, base)
        self.show_choice(0)

    def get_images(self, mode):
        raven_files = [os.path.join(self.base, "raven", mode, f)
                       for f in os.listdir(os.path.join(self.base, "raven", mode)) if f[-3:] == "gif"]
        extras = len(self.base + mode + 2 * "raven") + 1
        raven_files.sort(key = lambda x: x.split("_xx")[0])
        correct = [self.get_correct(f) for f in raven_files]
        return zip(raven_files, correct)

    def get_correct(self, fname):
        base, end = fname.split("_xx")
        correct = end.strip(".gif")
        return correct

    def make_choice(self, qidx, fname_image, correct):
        small_stimuli_img = tk.PhotoImage(file = fname_image)
        stimuli_img = small_stimuli_img.zoom(2, 2)
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

        widgets = (stimuli, response)
        for w in widgets:
            w.bindtags((self.name + "cognition_click",) + w.bindtags())
 
        qdic = {"widgets": widgets,
                "var": response_var,
                "correct": correct}
        return qdic

    def show_choice(self, qidx):
        stimuli, response = self.qobjects.get(qidx).get("widgets")

        fname = ["q" + str(qidx - 1) + i for i in ("stimuli", "response")]
        old_widgets = [self.children.get(f) for f in fname]

        if None not in old_widgets:
            [w.pack_forget() for w in old_widgets]

        packers = {"side": "left",
                   "fill": "both",
                   "expand": True,
                   "anchor": "center"}

        stimuli.pack(**packers)
        response.pack(**packers)

        self.clock("start")

    def go_next(self, event = ""):
        qid_0 = self.qidx.get()
        var_0 = self.qobjects.get(qid_0).get("var")

        if var_0 != "moongle":
            time = self.clock("stop")
            self.answer_dic[qid_0]["answer"] = var_0.get()
            self.answer_dic[qid_0]["time"] = time

            try:
                print "getting next number"
                qid = self.questions.next()[0]
                self.show_choice(qid)
                self.qidx.set(qid)
                print qid
            except StopIteration:
                stimuli, response = self.qobjects.get(qid_0).get("widgets")
                [i.pack_forget() for i in (stimuli, response)]
                endfont = tkFont.Font(size = 15, weight = "bold")
                self.unbind("<Return>", self.enter_id)
                end = tk.Label(self, text = "Task complete", font = endfont)
                end.pack(side = "top")
        elif var_0 == 0:
            print "stuff?"
            pass

class Raven(CognitionTab):
    def __init__(self, master, task = RavenTask):
        CognitionTab.__init__(self, master, RavenTask)

class Stroop(CognitionTab):
   def __init__(self, master, task = StroopTask):
        CognitionTab.__init__(self, master, StroopTask)


#root = tk.Tk()
#cog = CognitionTab(root, Stroop)
#raven = Raven(root, "practice")
#stroop = Stroop(root, "practice")
