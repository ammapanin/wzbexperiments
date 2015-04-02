# Startscreen for India experiments
# Last updated: 26 March 2015


import Tkinter as tk
import datetime
import csv
import tkFont
import os


class Startscreen(tk.Frame):

    def __init__(self, master, start_function):
        self.BASE = os.path.dirname(os.path.abspath(__file__))
        self.master = master
        self.start_experiment_now = start_function
        self.start_frames = self.show_startscreen(master)


    def show_startscreen(self, master):
        welcome_text = ("Welcome to the experiement. \n"
                        "Please enter the folowing information.\n"
                        "When you are ready, press the "
                        "'"'Get date and time'"' button to continue")


        main_frames = [tk.Frame(master) for i in (0, 1)]
        [f.pack(side = "left", expand = True, anchor = "n", pady = 20)
         for f in main_frames]

        self.error_frame, entry_frames = main_frames

        submain_frames = [tk.Frame(entry_frames) for i in (0, 1)]
        [f.pack(side = "top", expand = True, anchor = a, pady = 20)
         for a, f in zip(("s", "n"), submain_frames)]

        title_frame, entry_widgets_frame = submain_frames

        title_font = tkFont.Font(size = 20, weight = "bold")
        title = tk.Label(title_frame,
                         text = welcome_text,
                         justify = "left",
                         font = title_font)
        title.pack()

        self.make_entries(entry_widgets_frame)
        return main_frames


    def get_dropdown_data(self):
        datafilepath = os.path.join(self.BASE,
                                    "identifiers")


        filenames = ("enumerators.csv", "villages.csv", "heads.csv", "members.csv")

        enumeratorspath, \
            villagespath, \
            householdpath, \
            memberspath = [os.path.join(datafilepath, fname)
                           for fname in filenames]


        with open(enumeratorspath, "r") as enumfile:
            enum = csv.reader(enumfile)
            enumerators_csv = dict([(int(e[1]), e[0])
                                for e in enum])

        def pad(num_in):
            num = str(num_in)
            pad = 2 - len(num)
            return "0" * pad + num

        enumerator_dic = dict([(pad(key) + " - " + value, key)
                               for key, value
                               in sorted(enumerators_csv.items())])


        with open(villagespath, "r") as vfile:
            vcsv = csv.reader(vfile)
            rownames = vcsv.next()
            village_info = dict([(v[0], {"village": v[0],
                                         "taluk":   v[1],
                                         "tid":     v[2],
                                         "vid":     v[3]})
                                 for v in vcsv])

        def name_to_id_dic(name, name_id):
            village_dics = village_info.values()

            name_dic = dict([(d.get(name), d.get(name_id))
                             for d in village_dics])

            id_dic = dict([(d.get(name_id), d.get(name))
                           for d in village_dics])

            return name_dic, id_dic

        taluk_dic, tid_dic = name_to_id_dic("taluk", "tid")
        village_dic, vid_dic = name_to_id_dic("village", "vid")


        enumerators_tuple = tuple(enumerator_dic.keys())
        taluks_tuple = tuple(taluk_dic.keys())

        self.member_name_to_id = dict()

        member_relations = {1 : {"1": "Head"},
                            2 : {"2": "Wife", "1": "Husband"},
                            3 : {"2": "Daughter", "1":"Son"},
                            4 : {"2": "Mother", "1": "Father"},
                            5 : {"2": "Sister", "1": "Brother"},
                            6 : {"2": "Mother", "1": "Father-in-law"},
                            7 : {"2": "Sister", "1": "Brother-in-law"},
                            8 : {"1": "Servant/Employee"},
                            9 : {"1": "Lodger"},
                            10: {"1": "Son-in-law", "2": "Daughter-in-law"},
                            11: {"2": "Grandmother", "1":"Grandfather"},
                            -5: {"1": "Other"},
                            12: {"2": "Granddaughter", "1": "Grandson"}}

        with open(memberspath, "r") as mfile:
            mcsv = csv.reader(mfile)
            names = mcsv.next()

            labelled_rows = [dict(zip(names, row)) for row in mcsv]
            heads = list(set([row.get("wzb.hh.id")
                              for row in labelled_rows]))

            member_lists = [{"names": list(),
                             "wzb.ind.ids": list()}
                            for i in heads]

            self.members = dict(zip(heads, member_lists))
            name_details = ("name",
                            "name_initials",
                            "relation",
                            "gender")

            for member in labelled_rows:
                head = member.get("wzb.hh.id")
                ind_id = member.get("wzb.ind.id")
                member_name = [member.get(detail)
                               for detail in name_details]

                m = int(member_name[2])
                gender = member_name[3]

                relationship = member_relations[m].get(gender,
                                                       member_relations[m].get("1"))

                name = (member_name[0] + " " + \
                        member_name[1] + \
                        " ({})".format(relationship)).upper()

                self.members[head]["names"].append(name)
                self.members[head]["wzb.ind.ids"].append(ind_id)
                self.member_name_to_id[name] = ind_id




        shortration = "outputRationcard_number"
        shortelection = "electionid"
        shortname = "houhseholdhead_name"
        shortrelation = "houhseholdhead_relation"

        with open(householdpath, "r") as hfile:
            hcsv = csv.reader(hfile)
            names = hcsv.next()

            labelled_rows = [dict(zip(names, row)) for row in hcsv]
            self.households = dict()

            for row in labelled_rows:
                name = (row.get(shortname) +
                        " {} ".format(row.get("relationTag")) +
                        row.get(shortrelation)).upper()

                hh_dic = {"vid": row.get("village"),
                          "tid": row.get("taluk"),
                          "hid": row.get("wzb.hh.id"),
                          "ration_nr": row.get(shortration),
                          "election_id": row.get(shortelection),
                          "hh_name": name,
                          "taluk": tid_dic.get(row.get("taluk")),
                          "village": vid_dic.get(row.get("village"))}

                self.households.update({name: hh_dic})


        self.name_to_id_dics = {"enumerator": enumerator_dic,
                                "village": village_dic,
                                "taluk": taluk_dic}

        return enumerators_tuple, taluks_tuple


    def make_entries(self, master):
        self.entry_dic = dict()

        enums_list, taluks_list = self.get_dropdown_data()
        empty = ("No selection made.", )

        data_lists = (enums_list, taluks_list, empty, empty)
        labels = ("Enumerator ID", "Taluk", "Village", "Household")
        levels = ("enumerator", "taluk", "village", "hh_name")

        d_info = zip(data_lists, labels, levels)

        dropdowns =  [self.make_dropdown(master, row, d[0], d[1], d[2])
                      for row, d in enumerate(d_info)]

        enums, taluks, villages, householdheads = dropdowns

        dynamics = [(taluks + villages), (villages + householdheads)]

        d_funcs = [self.get_trace_functions(*d) for d in dynamics]

        [var.trace_variable("w", func) for var, func in d_funcs]


        hh_info_row = len(data_lists) + 1

        def show_household_details(name, index, mode):
            hh_name = householdheads[1].get()
            hid = self.households[hh_name].get("hid")

            hid_var = tk.StringVar(master)
            hid_var.set(hid)
            self.entry_dic.update({"wzb.hh.id":hid_var})

            details = dict([(idx, self.select_hh_subset(idx,
                                                        "hid",
                                                        hid)[0])
                       for idx in ("ration_nr", "election_id")])

            hh_info = {"hh_name": hh_name,
                       "hid": hid}
            hh_info.update(details)

            daterow = self.show_corrections(master, hh_info, hh_info_row)
            self.make_time_entries(master, daterow)
            return None

        householdheads[1].trace_variable("w", show_household_details)
        return "pancakes and flowers"


    def make_time_entries(self, master, row_i):
        date_vars = [tk.StringVar(master) for i in (0, 1)]
        entries = [tk.Entry(master, textvariable = v, state = "disabled")
                   for v in date_vars]
        bt = tk.Button(master)

        dic_names = ("time", "date")
        var_dic = dict([(name, var)
                         for name, var in zip(dic_names, date_vars)])
        self.entry_dic.update(var_dic)


        def fill_time(entry_time, entry_date):
            [entry.config(state = "normal")
             for entry in (entry_time, entry_date)]
            timenow = datetime.datetime.now()
            time_string = timenow.strftime("%H:%M")
            date_string = timenow.strftime("%d/%m/%y")

            entry_time.insert(0, time_string)
            entry_time.config(state = "disabled")

            entry_date.insert(0, date_string)
            entry_date.config(state = "disabled")


            bt.config(text = "Begin experiment",
                      command = lambda: self.start_experiment("bob"))

            return None

        def entry_validation():
            show_instructions = self.validation()

            if show_instructions == True:
                bt.config(text = "Get time and date",
                          command = lambda: fill_time(*entries))
            elif show_instructions == False:
                pass
            return show_instructions

        bt.config(text = "Validate information",
                  command = entry_validation)


        entryrows = (row_i, row_i + 1)
        btrow = entryrows[0]

        [e.grid(row = i, column = 0, sticky = "w")
         for e, i in zip(entries, entryrows)]
        bt.grid(row = btrow, column = 1, sticky = "e")
        return None


    def make_dropdown(self, master, row_n, entries, label_text, level):
        var = tk.StringVar(master)
        dropdown = apply(tk.OptionMenu, (master, var) + entries)
        dropdown.config(width = 30)
        dropdown.grid(row = row_n, column = 1, sticky = "w")

        l = tk.Label(master,
                     text = label_text)
        l.grid(row = row_n, column = 0, sticky = "w")

        self.entry_dic.update({level:var})

        return dropdown, var, level

    def get_trace_functions(self, selector_dropdown, selector_var, level,\
                            dropdown, dropdown_var, selected):

        def trace_function(name, index, mode):

            dynamic_list =  self.select_hh_subset(selected,
                                                  level,
                                                  selector_var.get())
            self.update_dropdowns(dropdown, dropdown_var, dynamic_list)

            if level == "household":
                pass

            return None
        return selector_var, trace_function


    def select_hh_subset(self, selected, level, selector):

        # print "selector", selector
        # print "level", level
        # print "selected", selected
        sublist = tuple(set([value.get(selected)
                             for value in self.households.values()
                             if value.get(level) == selector]))

        return sublist

    def update_dropdowns(self, dropdown, var, newlist):
        dropdown["menu"].delete(0, "end")
        [dropdown["menu"].add_command(label = b,
                                      command = tk._setit(var, b))
         for b in newlist]

    def make_correction_check(self, master, row_n, label_text, var_name):
        check_var = tk.IntVar(master)
        check_var.set(777)
        string_var = tk.StringVar(master)

        check = tk.Checkbutton(master,
                               text = label_text,
                               variable = check_var)
        box = tk.Entry(master, textvariable = string_var)

        def show_entrybox(name, index, mode):
            if check_var.get() == 1:
                box.grid(row = row_n, column = 1)
            elif check_var.get() == 0:
                box.grid_forget()

        check.grid(row = row_n, column = 0, sticky = "w")
        if var_name != "yes":
            check_var.trace_variable("w", show_entrybox)

        dic_names = (var_name + "_problem",
                     var_name + "_corrected")
        var_dic = dict([(name, var)
                        for name, var in zip(dic_names,
                                             (check_var, string_var))])

        self.entry_dic.update(var_dic)

        return check_var, string_var


    def show_corrections(self, master, hh_info, row_i):

        lines = [tk.Canvas(master, width = 700, height = 20) for i in (0, 1)]
        [l.create_line(0, 10, 700, 10) for l in lines]

        labs = ("Are the following details of the household head correct?",
                "Household head name",
                "Rationcard Number",
                "Election ID")

        corrections = ("Yes, all details are correct.",
                       "No, the household head has a different name",
                       "No, the ration card has a problem",
                       "No, the election ID has a problem")

        dic_names = ("yes", "hh_name", "ration", "election")

        hh_details = tuple([hh_info.get(detail)
                            for detail in
                            ("hh_name", "ration_nr", "election_id")])

        info_labs = [tk.Label(master, text = l)
                     for l in labs + hh_details]

        line_rows = (row_i, row_i + + 1 + 2 * len(labs))
        inforow = line_rows[0] + 1

        labstart = inforow + 1
        labn = len(labs) - 1
        lab_rows = 2 * range(labstart, labstart+ labn)
        lab_columns = labn * (0,) + labn * (1,)

        cn = lab_rows[-1] + 1
        correction_rows = range(cn, cn + len(corrections))


        [c.grid(row = i, column = 0, columnspan = 2)
         for c, i in zip(lines, line_rows)]

        info_labs[0].grid(row = inforow, column = 0,
                          columnspan = 2, sticky = "w")

        [l.grid(row = i, column = n, sticky = "w")
         for l, i, n in (zip(info_labs[1:], lab_rows, lab_columns))]

        coptions = zip(correction_rows, corrections, dic_names)
        correction_vars = [self.make_correction_check(master, n, text, name)
                           for n, text, name in coptions]

        date_row = self.show_person_interviewed(master,
                                                hh_info["hid"],
                                                line_rows[-1] + 1)

        return date_row



    def show_person_interviewed(self, master, hid, row_i):

        print hid, "hid"
        interview_var = tk.StringVar()
        relations = self.members.get(hid)
        relations = tuple(relations.get("names")) + ("Other", )

        qlab = tk.Label(master,
                        text = "Who is being interviewed?")
        qlist = apply(tk.OptionMenu,
                      (master, interview_var) + relations)

        self.entry_dic.update({"interviewed_check": interview_var})

        check_row = row_i
        line_row = row_i + 1

        line = tk.Canvas(master, width = 700, height = 20)
        line.create_line(0, 10, 700, 10)
        line.grid(row = line_row, column = 0, columnspan = 2, sticky = "w")

        qlab.grid(row = check_row, column = 0, sticky = "w")
        qlist.grid(row = check_row, column = 1, sticky = "w")

        self.interview_widgets = None

        def other_interview(name, index, mode):
            person = interview_var.get()
            if person == "Other":
                line.grid_forget()
                new_line_row = self.show_other_person_interviewed(master,
                                                                  line_row)
                line.grid(row = new_line_row,
                          column = 0,
                          columnspan = 2,
                          sticky = "w")
                next_row = new_line_row + 1
            else:
                if self.interview_widgets:
                    [w.grid_forget() for w in self.interview_widgets]
                else:
                    pass
                next_row = line_row + 1
            return next_row

        interview_var.trace_variable("w", other_interview)

        return line_row + 8



    def show_other_person_interviewed(self, master, row_i):

        labs = (("Please enter the details"
                 " of the person being interviewed"),
                "Interviewee name",
                "Interviewee Rationcard Number",
                "Interviewee Election ID",
                "Relationship to head of household",)

        relations = ("Wife", "Husband",
                     "Mother", "Father",
                     "Son", "Daughter",
                     "Son-in-law", "Daughter-in-law",
                     "Mother-in-law", "Father-in-law")

        person_vars = [tk.StringVar(master) for l in labs[1:]]
        relation_var = person_vars[-1]

        dic_tags = ("interviewed_name",
                    "interviewed_ration",
                    "interviewed_election",
                    "interviewed_relation")

        var_dic = zip(dic_tags, person_vars)
        self.entry_dic.update(var_dic)

        plabrow = row_i + 1
        pn = plabrow + 1
        person_rows = range(pn, pn + len(labs))
        relation_row = person_rows[-1]


        person_labs = [tk.Label(master, text = l)
                           for l in labs]

        entries = [tk.Entry(master, textvariable = v)
                   for v in person_vars[:-1]]

        relationship = apply(tk.OptionMenu,
                             (master, relation_var) + relations)


        [l.grid(row = i, column = 0, sticky = "w")
         for l, i in zip(person_labs, person_rows)]
        [l.grid(row = i, column = 1, sticky = "w")
         for l, i in zip(entries, person_rows)]

        relationship.grid(row = relation_row, column = 1)


        self.interview_widgets = person_labs + entries + [relationship]


        return relation_row + 1

    def validation(self):
        d = dict([(key, value.get())
                  for key, value in self.entry_dic.items()])

        enum_var = d.get("enumerator")
        if enum_var == "":
            enumerator = 1
        elif enum_var !="":
            enumerator = 0

        p = "_problem"
        c = "_corrected"
        hh_strings = ("hh_name", "ration", "election")

        yes_var = d.get("yes_problem")
        if yes_var == 777:
            hh_check = True not in [d.get(v + p) != 777 for v in hh_strings]
        elif yes_var != 777:
            hh_check = 0

        hh_details = [d.get(var + p) == 1 and d.get(var + c) == ""
                      for var in hh_strings]
        hh_name, hh_ration, hh_election = hh_details

        interview_var = d.get("interviewed_check")
        if interview_var == "":
            i_check = 1
            i_person = 1

        elif interview_var != "":
            i_check = 0
            i_person = interview_var

        i_strings = tuple(["interviewed_" + i
                           for i in ("name", "ration", "election", "relation")])
        i_vars = [d.get(var) == "" for var in i_strings]
        interview = [i_person == "Other" and i == True for i in i_vars]

        answers = ("enumerator", "hh_check", "interview_check")
        answer_vars = [enumerator, hh_check, i_check]

        validation_strings = answers + hh_strings + i_strings


        entry_msgs = ["Please enter the {}.".format(s)
                      for s in ("household head name",
                                "household head ration card number",
                                "household head election id",
                                "interviewee name",
                                "interviewee ration card number",
                                "interviewee election id",
                                "interviewee relationship to household head")]

        answer_msgs = ["Please select an enumerator",
                       ("Please indicate whether the"
                        " details of the household head are correct"),
                       "Please indicate who is being interviewed"]

        msg_dic = dict([(s, msg)
                        for s, msg in
                        zip(validation_strings, answer_msgs + entry_msgs)])

        valid_dic = dict(zip(validation_strings,
                              answer_vars + hh_details + interview))

        messages = [msg_dic.get(s) for s in validation_strings
                    if valid_dic.get(s) == True]

        [f.pack_forget() for f in self.error_frame.winfo_children()]
        if len(messages) > 0:
            head_lab = tk.Label(self.error_frame,
                                text = "Please make the following corrections")
            labs = [tk.Label(self.error_frame, text = m, fg = "red")
                    for m in messages]
            [l.pack(side = "top", anchor = "w") for l in [head_lab] + labs]

        elif len(messages) == 0:
            head_lab = tk.Label(self.error_frame,
                                text = "No validation errors found")
            head_lab.pack(side = "top", anchor = "nw")

        return len(messages) == 0


    def start_experiment(self, experiment):
        print self.entry_dic.keys()
        print self.entry_dic.get("interviewed_check").get()
        id_dics = self.name_to_id_dics
        numeric_tags = ("tid", "vid", "enumid")
        id_levels = ("taluk", "village", "enumerator")

        values = [(level, self.entry_dic.get(level).get())
                  for level in id_levels]

        ids = [id_dics.get(level).get(value)
               for level, value in values]

        interviewed_name = self.entry_dic.get("interviewed_check").get()
        interviewed_id = self.member_name_to_id.get(interviewed_name)

        numeric_ids = [tk.IntVar() for v in numeric_tags]
        [v.set(idx) for v, idx in zip(numeric_ids, ids)]


        numeric_dic = dict(zip(numeric_tags, numeric_ids))

        interviewed_dic = {"interviewed_name": interviewed_name,
                           "wzb.ind.id": interviewed_id}

        self.entry_dic.update(numeric_dic)
        self.entry_dic.update(interviewed_dic)

        [f.pack_forget() for f in self.start_frames]

        if callable(self.start_experiment_now):
            self.start_experiment_now()
        else:
            self.dummy_start()

        return None

    def dummy_start(self):
        for key, value in self.entry_dic.items():
            print key, value







if __name__ == "__main__":
    root = tk.Tk()
    crustacean = Startscreen(root, "start_function")
    root.mainloop()
