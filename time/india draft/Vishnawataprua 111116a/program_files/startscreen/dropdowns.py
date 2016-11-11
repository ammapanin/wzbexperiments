# -*- coding: utf-8 -*-

### TODO:
### 1. Check about accepting lists of values
### 2. See about transform dictionaries for standard dropdowns

import Tkinter as tk
import os
import csv
from collections import defaultdict
from itertools import chain


class SpecialString(str):
    """A string class that also accepts a pointer to a line dictionary.
    """
    def __new__(self, value, row_dic):
        return str.__new__(self, value)

    def __init__(self, value, row_dic):
        self.row_dic = row_dic

class SpecialStringVar(tk.StringVar, object):
    """A tkinter string variable class that allows access to line dictionaries.
    """
    def __init__(self, master):
        tk.StringVar.__init__(self, master)

    def set(self, sstring):
        try:
            self.row_dic = sstring.row_dic
        except AttributeError:
            pass
        super(SpecialStringVar, self).set(sstring)
        return None

    def get_dictionary(self):
        try:
            return self.row_dic
        except AttributeError:
            pass

class ListDic(dict):
    """A dictionary of unique tuples, ready for a dropdown menu
    """
    def __init__(self):
        super(dict, self).__init__()
        self.sets = defaultdict(set)

    def add(self, key, *args):
        self.sets[key].update(args)
        self[key] = tuple(sorted(list(self.sets[key])))

class GeneralDynamicDropdown(tk.OptionMenu):
    def __init__(self, master, select_var, control_var, control_dic, **kwargs):
        """
        select_var (tk.Stringvar): variable records list item selection
        control_var (tk.Stringvar): traced variable, controls the
            subsequent dropdown menu = select_var for a previous dropdown
        """
        tk.OptionMenu.__init__(self, master, select_var, "Nothing selected")
        self.control_var = control_var
        self.select_var = select_var
        self.control_dic = control_dic
        self.control_var.trace("w", self.update)

    def update(self, name, index, mode):
        """Change the contents of the dropdown menu depending on what has been
            selected for control_var
        """
        self.select_var.set("Nothing selected")
        lab = self.control_var.get()
        row_dic = self.control_var.get_dictionary()
        new_list = self.control_dic.get(lab)
        menu = self.children.get("menu")
        menu.delete("0", "end")
        if new_list == None:
            pass
        else:
            for item in new_list:
                fill_list = lambda v = item: self.select_var.set(v)
                menu.add_command(label = item,
                                 command = fill_list)

class SelectorDropdowns(tk.Frame):
    """Dropdown menus used to select Startscreen identifiers
    """
    def __init__(self, master, standard, dynamic, **kwargs):
        """
        Args:
            standard (dic): dictionary? of standard dropdowns. {label: vars}
             dynamic (dic): dictionary? of dynamic dropdowns. {group: values}

        Attributes:
            data_dic (dic): class dictionary populated by {varname : var} for each
                menu
            transform (dic): class dictionary populated by {varname : dic} for each
                menu, with dic a dictionary of transformations
        """

        tk.Frame.__init__(self, master, **kwargs)
        self.pack(side = "top", fill = "both", expand = True)
        self.base = os.path.join(os.path.dirname(__file__),
                                 "identifiers")
        self.data_dic = dict()
        self.transform = dict()
        self.saved_headings = chain(*[l.get("saved_headings")
                                      for l in dynamic.values()])
        self.create_dropdowns(standard, dynamic)

    def save_data(self):
        try:
            d = dict([(key, v.get()) for key, v in self.data_dic.items()])
            id_dic = self.identity_var.get_dictionary()
            [d.update({key: id_dic.get(key)}) for key in self.saved_headings]
        except:
            pass
        return d

    def max_length(self, menu):
        menu_entries = menu.children.get("menu")
        print menu_entries
        return len(max(menu_entries, key = len))

    def create_dropdowns(self, standard, dynamic):
        s = self.create_standard_dropdowns(self, standard)
        d = self.create_dynamic_dropdowns(self, dynamic)


        #menu_widgets = [m[1] for tup in (s, d) for m in tup]
        #print menu_widgets
        #max_length = max([self.max_length(menu) for menu in menu_widgets])
        dropdowns = s + d
        for idx, (lab, dropdown) in enumerate(dropdowns):
            lab.grid(row = idx, column = 0, sticky = "w")
            dropdown.grid(row = idx, column = 1, sticky = "ew")
            dropdown.config(width = 35)
        return None

    def create_standard_dropdowns(self, master, standard):
        csv_output = [self.read_standard_data(var.get("data_path"),
                                              var.get("column"),
                                              var.get("transformations"))
                      for var in standard.values()]
        values = [v[0] for v in csv_output]
        transform_dics = [v[1] for v in csv_output]
        tkvars = [tk.StringVar(self) for item in standard]
        dropdowns = [apply(tk.OptionMenu, (master, var) + vals)
                     for var, vals in zip(tkvars, values)]
        colnames = standard.keys()
        self.transform.update(dict(zip(colnames, transform_dics)))
        collabs = [tk.Label(master, text = txt) for txt in colnames]
        out = zip(collabs, dropdowns)
        [self.data_dic.update({vname: tkvar})
         for vname, tkvar in zip(colnames, tkvars)]
        return out

    def create_dynamic_dropdowns(self, master, dynamic):
        """Create dynamic dropdown menus

            Creates dropdowns for each set of linked variables
            Expects key, value pairs fo reach set of variables
            Creates dropdowns and labels for all menus
            Varnames are takenfrom the colnames attribute

        Args:
            dynamic (dic): dictionary of a set of dynamic variables
        Returns:
            cols_out (list): [(Label, Dropdown), ...]
        """
        sequences = [(varlist.get("columns"),
                      varlist.get("data_path"),
                      varlist.get("condition"),
                      varlist.get("colnames"),
                      varlist.get("transformations"))
                     for varlist in dynamic.values()]
        dropdowns = list()
        for sequence, path, condition, varnames, transform in sequences:
            start_vals, dics = self.read_dynamic_data(path,
                                                      sequence,
                                                      transform,
                                                      condition)
            tkvars = [SpecialStringVar(self) for i in [start_vals] + dics]
            start_drop = apply(tk.OptionMenu, (master, tkvars[0]) + start_vals)
            other_drops = [GeneralDynamicDropdown(master,
                                                  select_var = tkvars[idx + 1],
                                                  control_var = tkvars[idx],
                                                  control_dic = dic)
                           for idx, dic in enumerate(dics)]
            dropdowns.append(start_drop)
            dropdowns.extend(other_drops)
            # DO this formultiple sets of dropdowns
            self.identity_var = tkvars[-1]

        colnames = chain(*[d.get("colnames") for d in dynamic.values()])
        collabs = [tk.Label(master, text = txt) for txt in colnames]
        if len(collabs) != len(dropdowns):
            print "Enter correct number of colnames"
        out = zip(collabs, dropdowns)
        return out

    def read_standard_data(self, data_path, column, transformations):
        """Read in data from a standard path

        Args:
            transformations (tuple - ("key", "value"), "new_name")
        Return:
        "-----"
        """
        data_path = os.path.join(self.base, data_path)
        if os.path.isfile(data_path):
            with open(data_path, "rU") as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                data = csv.reader(csvfile, dialect)
                colnames = data.next()
                ldics = [dict(zip(colnames, line)) for line in data]
            (k, v), new_idx = transformations
            transform_dic = dict([(ldic.get(k), ldic.get(v)) for ldic in ldics])
            raw_values = list(set([ldic.get(column) for ldic in ldics]))
            values = tuple(sorted(raw_values))
            return values, (transform_dic, new_idx)
        else:
            print "Data file does not exist. Don't be a doofus"

    def read_dynamic_data(self, data_path, column_pairs,
                          transformations, condition = None):
        """Read in data for dynamic dropdown menus
            Make a list of dictionaries of each column-row.
            If there is a condition, select only the rows that meet that condition.
        Args:
            data_path (str): file path
            column_pairs (str, str): pairs of columns that depend on each other
            transformations (dic):
                {column name : ((col in data, col in data), out name)}
            condition (str): name of column in data that should be True
        Returns:
            start_list (list): tuple of initial values
            ## latent_dics (list): list of latent dictionaries
            control_dics (list): list of dependent dictionaries
        """
        data_path = os.path.join(self.base, data_path)
        if os.path.isfile(data_path):
            with open(data_path, "rU") as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                data = csv.reader(csvfile, dialect)
                colnames = data.next()
                ldics = [dict(zip(colnames, line)) for line in data]
                if condition != None:
                    ldics = [ldic
                             for ldic in ldics if
                             int(ldic.get(condition)) == True]

            control_dics = self.create_dictionaries(column_pairs, ldics)
            start_key = column_pairs[0][0]
            start_list = tuple(sorted(list(set([ldic.get(start_key)
                                                for ldic in ldics]))))
            ### CHANGE HERE!
            self.amma_control_dics = control_dics
            return start_list, control_dics
        else:
            print "Data file does not exist. Don't be a doofus"

    def create_dictionaries(self, column_pairs, csv_dic_iterable):
        control_dics = [(d, ListDic()) for d in column_pairs]
        for line in csv_dic_iterable:
            for (key, value), dic in control_dics:
                dic.add(line.get(key), SpecialString(line.get(value), line))
        return [d[1] for d in control_dics]

