import os
import csv

# Code takes in CSV version of the questionnaire and spits out a tex version, ready to be editied


qfilepath = ('/Users/aserwaahWZB/Projects/GUI Code/questionnaire_310515/household_details.csv')

#qfilepath = "/Users/aserwaahWZB/Desktop/ghana_experiment_121114/ghana_program/ghana_questionnaire.csv"

with open(qfilepath) as myfile:
    qs = [line for line in csv.reader(myfile)]


def to_item(line):
    item = code = None
    label = line[2].replace("_", "\_")
    qtext = line[0]
    qtype = line[1]
    other = line[4] == "1"

    item = "\item {}, \\textbf{{\\({} \\)}} \n".format(qtext, label)
    if qtype == "slider":
        bob = tuple(line[4].split(",x"))
        print bob
        code = "\\textbf{{\emph{{scale, }}}}100 {} - 0 {}\n\n".format(*bob)

    elif qtype == "text":
        code = " "
    else:
        #elif qtype in ("choice", "check", "list_options"):
        choices = line[4].split(",x")
        if other == True:
            choices.append("Other")
        itemlist = "".join(["\item {}\n".format(choice)
                            for choice in choices])

        code = "\\begin{{enumerate}}[label = {{\\arabic*}}]{}\end{{enumerate}}\n\n".format(itemlist)

    # elif line[1] == "dependent_check" or line[1] == "list":
    #      code = " "

    if item and code:
        return item + code
    else:
        print line[0]

for i, line in enumerate(qs):
    if line[0] == None:
        print i


q_lines = list()
for line in qs:
   q = to_item(line)
   if q != None:
       q_lines.append(q)
   elif q == None:
       print line

tex = "".join(q_lines)



with open("/Users/aserwaahWZB/Projects/Ghana/Design documents/Questionnaire code/india_questionnaire.tex", "w") as myfile:

        tex_file = ("\\documentclass{{article}}\n"
                    "\\usepackage{{enumitem}}\n"
                    "\\setlist[enumerate,2]{{start=0}}\n"
                    "\\begin{{document}}\n\n"
                    "\\title{{Finance and religion in Ghana - Survey}}"
                    "\\maketitle"
                    "\\begin{{enumerate}}{}\end{{enumerate}}\n"
                    "\\end{{document}}")

        tex_output = tex_file.format(tex)
        myfile.write(tex_output)

print "finished converting"
