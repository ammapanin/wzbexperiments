import os
from unpack_csv import unpack_csv

def unpack_qdic(qdic):
    view = qdic.get("qview")
    if view == "single":
        tex = create_question(qdic)
    elif view == "table":
        tex = make_table(qdic)
    return tex

def make_table(qdic):
    #TODO: properly format questions. i.e strip table questions of reserved latex characters

    qdics = qdic.get("questions")
    label = escape_label(qdic.get("label"))
    qtext = "Table"

    qtex = "{{\\bfseries {}}}\\emph{{ {} }} \n"
    question = qtex.format(qtext, label)

    qtexs = [create_question(q) for q in qdics]
    qlist_tex = itemize(qtexs, table = True)

    tex = question + qlist_tex
    return tex

def create_question(qdic):
    """ Returns a tex representation of a question.
    
    Args:
    qdic - a single question dictionary -> a line from csv
    """
    qtext = qdic.get("question_text")
    qtype = qdic.get("type")
    qunits = qdic.get("units")
    options = qdic.get("options")
    notes = qdic.get("notes", '')
    label = escape_label(qdic.get("label"))
    qtex = "{{\\bfseries {}}}\\emph{{ {} }} \n"
    question = qtex.format(qtext, label)
    print label
    tex_options = unpack_options(qtype, options, qunits)
    if notes != "":
        nb = "\\textbf{{{{\\footnotesize NOTE}} {} }} \n"
        tex_notes = nb.format(notes)
    else:
        tex_notes = ""
    tex = question + tex_options + tex_notes
    return tex

def escape_label(lab):
    return lab.replace("_", "\\_")

def itemize(options_list, table = False):
    """Returns itemizes list; special numbering for tables """
    items = ["\\item {} \n".format(i)
             for i in options_list]

    if table == True:
        begin = "\\begin{enumerate}[label*=\\arabic*.] \n"
    else:
        begin = "\\begin{enumerate} \n"
    end = "\\end{enumerate}"

    item_list = "".join(items)
    tex_list = begin + item_list + end
    return tex_list

def unpack_slider(options, sep):
    try:
        smin, smax, sfreq = options.split(sep)[0:3]
    except:
        print options, sep
    tex_base = "\\\\min - {}, max - {}, interval - {} \n"
    tex = tex_base.format(smin, smax, sfreq)
    return tex

def unit_slider(options, units):
    units = units.split(",x")
    unit_options = options.split(",x")
    options_tex = [unpack_slider(u, ",z")[2:] for u in unit_options]
    units_tex = ["\\\\ \\emph{{ {} }}".format(u) for u in units]

    tex = "".join([unit + option
                   for unit, option in zip(units_tex, options_tex)])
    return tex

def unpack_options(qtype, options, units):
    """Deals with the different representations of different question types"""
    if qtype in ("entry", "text", "dynamic_text"):
        tex_options = ""
    elif qtype in ("check", "choice", "dropdown"):
        tex_options = itemize(options.split(",x"))
    elif qtype == "slider":
        if units == "":
            tex_options = unpack_slider(options, ",x")
        elif units != "":
            tex_options = unit_slider(options, units)
    return tex_options

def make_questions(csv_path):
    """Takes csv and returns tex object"""
    tex_dics = unpack_csv(csv_path)
    qtex = itemize([unpack_qdic(q) for q in tex_dics])
    return qtex

def write_test(stuff):
    with open("test.tex", "w") as f:
        f.write(stuff)

