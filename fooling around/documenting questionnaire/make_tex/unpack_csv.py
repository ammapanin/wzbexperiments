"""
Takes the two csv objects that define a questionnaire and returns question dics
"""
import os
import csv

def create_table_dic(table_lab, qcsvdic):
    table_qs = [q for q in qcsvdic.values() 
                if q.get("qview") == table_lab]
    tdic = {"label": table_lab,
            "questions": table_qs,
            "qview": "table"}
    return tdic

def make_tex_dics(idx_label, qidx, qcsvdic):
    idx = idx_label[0]
    label = idx_label[1]
    table = label[0:5] == "table"
    
    if table == True:
        qdic = create_table_dic(label, qcsvdic)
    elif table != True:
        qdic = qcsvdic.get(label)
    if qdic == None:
        print label
        qdic["qidx"] = qidx
    return qdic

def unpack_csv(csv_folder):
    """Unpacks the csv files and ensures that the correct orderings are kept

    Definitions files is first unpacked; dict indexed by label
    Labels are then used to ensure that correct orders are maintained.
    Prints message when certain tabs are in the definitions but 
      are not included in the order csv.
    """
    definitions = os.path.join(csv_folder, "definitions.csv")
    order = os.path.join(csv_folder, "order.csv")

    qcsvdic = dict()
    with open(definitions, "r") as qfile:
        qcsv = csv.reader(qfile)
        headers = qcsv.next()
        for row in qcsv:
            line_dic = dict(zip(headers, row))
            qcsvdic.update({line_dic.get("label"): line_dic})

    tab_dic = dict()
    with open(order, "r") as qfile:
        qcsv = csv.reader(qfile)
        headers = qcsv.next()
        tab_order = qcsv.next()[0].split(",x")
        for i, row in enumerate(qcsv):
            tab = row[1]
            label = row[0]
            idx_label = (i, label)
            if tab in tab_dic.keys():
                tab_dic[tab].append(idx_label)
            elif tab not in tab_dic.keys():
                tab_dic[tab] = [idx_label]
            
    tex_dics = list()
    qidx = 1
    for tab in tab_order:
        labels = tab_dic.get(tab)
        if labels != None:
            for label in labels:
                qdic = make_tex_dics(label, qidx, qcsvdic)
                tex_dics.append(qdic)
                qidx += 1
        if labels == None:
            msg = "\"{}\" is an additional tab and has not been included."
            print msg.format(tab)
        
    return tex_dics
