import Tkinter as tk
import os
import csv

class DynamicVar(tk.StringVar):

    def __init__(self, master, options, list_var, *args, **kwargs):
        tk.StringVar.__init__(self, master)

        self.options = options
        self.dropdown = apply(tk.OptionMenu,
                              ((master, list_var) + ("No selection made",)))
        self.trace("w", self.update_dropdown)
        self.dropdown_var = list_var

    def update_dropdown(self, name, index, var):
        key = self.get()
        no_value = ("No value found", )
        values = self.options.get(key, no_value)
        if len(values) == 0:
            values = no_value

        self.dropdown["menu"].delete(0, "end")
        for value in values:
            self.dropdown["menu"].add_command(label = value,
                                              command=tk._setit(self.dropdown_var,
                                                                value))



class Dropdowns(tk.LabelFrame):

    def __init__(self, master, participation_func, *args, **kwargs):
        tk.LabelFrame.__init__(self, master, *args, **kwargs)
        self.pack(fill = "x", expand = True)
        #self.datapath = os.path.join()

        self.data_path = ("/Users/aserwaahWZB/Projects/Experiments"
                          "/india/details/shared/identifiers")


        enums_list = self.get_enumerators()
        taluks_list, villages_list  = self.get_villages()
        self.households = self.get_households()
        taluks_villages = self.subset_taluks(taluks_list)
        villages_households = self.subset_villages(villages_list)



        dropdown_frame = tk.Frame(self)
        dropdown_frame.pack(side = "top", expand = True, fill = "both")

        enums_var = tk.StringVar(dropdown_frame)
        hh_var = self.hh_var = tk.StringVar(dropdown_frame)
        village_var = DynamicVar(dropdown_frame, villages_households, hh_var)
        taluk_var = DynamicVar(dropdown_frame, taluks_villages, village_var)

        enums = apply(tk.OptionMenu,
                      ((dropdown_frame, enums_var) + enums_list))
        taluks = apply(tk.OptionMenu,
                       ((dropdown_frame, taluk_var) + taluks_list))
        villages = taluk_var.dropdown
        households = village_var.dropdown

        dropdowns = [enums, taluks, villages, households]

        label_names = ("Enumerator ID", "Taluk", "Village", "Household")
        labels = [tk.Label(dropdown_frame, text = l) for l in label_names]

        for i, (l, d) in enumerate(zip(labels, dropdowns)):
            l.grid(row = i, column = 0, sticky = "w")
            d.grid(row = i, column = 1, sticky = "w")


        participation_var = tk.BooleanVar(master)
        participation_var.trace("w",
                                participation_func)
        self.participate = participation_var
        ptext =  "Is this household willing to participate?"
        participate_bt = tk.Checkbutton(self,
                                        text = ptext,
                                        variable = participation_var)
        participate_bt.pack(side = "top",
                            anchor = "w",)



    def select_sublist(self, selected, level, selector):
        """Return sorted selected sublist

        -self.households is a dictionary with dictionary values
        -each value dictionary is of a single household

        selected = desired hh attribute: name, rationcard, etc
        level = village, taluk, etc.
        selector = particular value of a taluk, village, etc.
        """

        sublist = list(set([value.get(selected)
                            for value in self.households.values()
                            if value.get(level) == selector]))
        sublist.sort()
        return selector, sublist

    def subset_villages(self, village_list):
        vdic = dict([self.select_sublist("hh_name", "village", vname)
                     for vname in village_list])
        return vdic

    def subset_taluks(self, taluks_list):
        tdic = dict([self.select_sublist("village", "taluk", tname)
                     for tname in taluks_list])
        return tdic


    def get_enumerators(self):
        enum_path = os.path.join(self.data_path,
                                 "enumerators.csv")

        with open(enum_path, "r") as enumfile:
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

        enumerators = tuple([pad(key) + " - " + value
                             for key, value
                             in sorted(enumerators_csv.items())])

        return enumerators


    def get_villages(self):
        village_path = os.path.join(self.data_path,
                                    "villages.csv")

        with open(village_path, "r") as vfile:
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

        self.name_tid, self.tid_name  = name_to_id_dic("taluk", "tid")
        self.name_vid, self.vid_name = name_to_id_dic("village", "vid")

        taluks = tuple(sorted(self.name_tid.keys()))
        villages = tuple(self.name_vid.keys())

        return taluks, villages



    def get_households(self):
        shortration = "outputRationcard_number"
        shortelection = "electionid"
        shortname = "houhseholdhead_name"
        shortrelation = "houhseholdhead_relation"

        hh_path = os.path.join(self.data_path,
                               "households.csv")

        with open(hh_path, "r") as hfile:
            hcsv = csv.reader(hfile)
            names = hcsv.next()

            labelled_rows = [dict(zip(names, row)) for row in hcsv]
            households = dict()

            for row in labelled_rows:
                relation = row.get("relationTag")
                try:
                    r = int(relation)
                    rdic =  {1:'S/O', 2:'D/O', 3:'W/O'}
                    relationship = rdic.get(r, " ")
                except ValueError:
                    relationship = relation

                name = (row.get(shortname) +
                        " " + relationship + " " +
                        row.get(shortrelation)).upper()

                hh_dic = {"vid": row.get("village"),
                          "tid": row.get("taluk"),
                          "hid": row.get("wzb.hh.id"),
                          "ration_nr": row.get(shortration),
                          "election_id": row.get(shortelection),
                          "hh_name": name.strip(),
                          "taluk": self.tid_name.get(row.get("taluk")),
                          "village": self.vid_name.get(row.get("village"))}

                households.update({name: hh_dic})

        return households






    def get_members(self):
        members_path = os.path.join(self.data_path,
                               "members.csv")

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


        with open(members_path, "r") as mfile:
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
                #print "village"
                #print member.get("village")
                #print member_name
                try:
                    m_idx = int(member_name[2])
                    gender = member_name[3]
                    general_relation = member_relations[m]
                    default = general_relation.get("1")
                    relationship = general_relationship.get(gender, default)
                except ValueError:
                    relationship = " "

                name = (member_name[0] + " " + \
                        member_name[1] + \
                        " ({})".format(relationship)).upper()

                self.members[head]["names"].append(name)
                self.members[head]["wzb.ind.ids"].append(ind_id)
                self.member_name_to_id[name] = ind_id






    def draw_dropdowns(self):
        """Draw the 3 levels of dropdown menus

        - Enumerators is independent
        - selecting a Taluk updates the Villages list
        - selecting a Village updates the Households list

        - 'enumerators' needs a tuple
        - 'taluks' needs a tuple
        """
        pass
        def show_household_details(name, index, mode):
            """Record and display household identifier information

            -Take name from list of household names
            -Use name to recover household details from
             self.households dictionary (hh_name: {other identifiers})
            -Store data in dictionary for display
            -Store data in entry_dic for data recording
            """

            hh_name = householdheads[1].get()
            hid = self.households[hh_name].get("hid")
            field_idx = ("ration_nr", "election_id")
            id_vars = [tk.StringVar(master) for i in ("hid",) + field_idx]

            hh_id_strings = [self.select_hh_subset(idx, "hid", hid)[0]
                             for idx in field_idx]
            [var.set(i) for var, i in zip(id_vars, [hid] + hh_id_strings)]

            string_details = dict(zip(field_idx, hh_id_strings))
            var_names = ("wzb.hh.id",) + field_idx
            var_details = dict(zip(var_names, id_vars))

            hh_info = {"hh_name": hh_name,
                       "hid": hid}
            hh_info.update(string_details)

            self.entry_dic.update(var_details)

            daterow = self.show_corrections(master, hh_info, hh_info_row)
            self.make_time_entries(master, daterow)
            return None




#root = tk.Tk()
#Dropdowns(root)
