"""
Produces a tex file and pdf documenting a given questionnaire
Questionnaire must be in standard format.
"""

import os
import subprocess
import shlex
from create_tex import make_questions

def make_doc_tex(title, q):
    """
    Creates basic structure for a tex file
    """
    doc_class = "\\documentclass{{article}} \n"
    enumitem = "\\usepackage{{enumitem}}"
    packages = enumitem
    begin = "\\begin{{document}} \n"
    title_tex = "\\title{{{}}} \n \\maketitle"
    end = "\\end{{document}}"

    doc_base = doc_class + packages + begin + title_tex + "\n{}\n" + end
    doc = doc_base.format(title, q)
    return doc

def make_doc(title, csv_folder, output_folder):
    """
    Creates the final document and processes the pdf

    Args: 
    title - questionnaire title; 
            stripped and lower case version will be used for filename 
    csv_folder - containing questionnaire csv files
    output_folder 
    """
    qtex = make_questions(csv_folder)
    doc_tex = make_doc_tex(title, qtex)

    fname = title.replace(" ", "").lower() + ".tex"
    output_path = os.path.join(output_folder, fname)
    with open(output_path, "w") as tfile:
        tfile.write(doc_tex)

    proc = subprocess.Popen(shlex.split('pdflatex {}'.format(output_path)))
    print "Tex file written to {}".format(output_path)
    return None

#base = "/Users/aserwaahWZB/Projects/GUI Code/fooling around"
#csv_folder = os.path.join(base, "definitions_test")
#output_folder = base
#make_doc("Survey Round 2", csv_folder, output_folder)



qpath = "/Users/aserwaahWZB/Projects/GUI\ Code/india\ other\ data/Current\ version/pkg/survey_round_2/details/definitions"

