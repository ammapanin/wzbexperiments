#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk
import os
from program_files.questionnaire.questionnaire import Questionnaire

base_folder = os.path.dirname(os.path.realpath(__file__))
csv_path = os.path.join(base_folder, "program_files/definitions")

title = "Time preferences survey"
survey_dic = {"csv_path": csv_path,
         "data_path": "",
         "title": title,
         "next_function": ""}


root = tk.Tk()
bob = Questionnaire(root, **survey_dic)
root.mainloop()
