import csv
import os
import Tkinter as tk
import tkFont


class DraggableList(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master)
        self.vsb = tk.Scrollbar(self)
        self.canvas = DraggableCanvas(self, **kwargs)

        self.vsb.configure(command = self.canvas.yview)
        self.canvas.configure(yscrollcommand = self.vsb.set)

        self.pack(side = "left",
                  fill = "both",
                  expand = True)
        self.canvas.pack(side = "left",
                         fill = "both",
                         expand = True)
        self.vsb.pack(side = "right",
                      fill = "y")


class DraggableCanvas(tk.Canvas):
    def __init__(self, master, ncol = 1, field_float = True):
        """Initialise draggable canvas
        Args:  
        floating fields - True/False
        columns - integer, nr. of columns
        """
        tk.Canvas.__init__(self, master, width = 400, height = 400)
        self.pack()
        self.ncol = ncol

    def create_partitions(self, partitions):
        """Creates the major partitions of the canvas

        Args:
        partitions - integer, number of columns

        Definitions:
        A few functions determine the exact postioning of the various
        grids: round_up, get_side

        Boxes are created with a light fill
         tags: box_NAME, 
        Title text is created at top of box
         tags: headers, title_NAME
        """
        xn = 100
        npartitions = len(partitions)

        def round_up(np, nc):
            return int(np / nc) + (np / nc > 0)

        def get_side(n):
            x0 = 4 + (xn + 2) * n
            x1 = x0 + xn
            return x0, x1

        nrows =  round_up(npartitions, self.ncol)
        colrange = range(self.ncol)
        rowrange = range(nrows)
        cols = [get_side(n) for n in colrange]
        rows = [get_side(n) for n in rowrange]
        boxes = list()
        for col in cols:
            for row in rows:
                i, k, j, l = col + row
                box = (i, j, k, l)
                boxes.append(box)

        self.boxes = dict()
        self.titles = dict()
        self.anchors = dict()
        for t, box in zip(partitions, boxes):
            x0, y0, x1, y1 = box
            box_id = self.create_rectangle(*box, fill = "light blue", 
                                           tags = ("box_" + t,))
            title_id = self.create_text(x0 + 2, y0, text = t,
                                        anchor = "nw", 
                                        tags = ("headers", "title_" + t))
            self.boxes.update({"box_" + t: box_id})
            self.titles.update({"title_" + t: title_id})
            self.anchors.update({box_id:  (x0 + 2, y0 + 20)})


    def update_tabs(self, tab_list):
        existing_tabs = self.find_withtag("tab")
        tab_font = tkFont.Font(size = 13, weight = "bold")
        tabs = [self.create_text(5, i * 40,
                                 font = tab_font,
                                 text = txt, anchor = "nw",
                                 tags = ("tab", txt))
                for i, txt in enumerate(tab_list)]
        self.tab_texts = ["box_" + t for t in tab_list]
        self.config(scrollregion = self.bbox("all"))
        print "anything fishy?"
        return tab_list

    def change_label_tab(self, idx, new_tab, text):
        self.delete(idx)
        self.create_label(new_tab, text)
        return None

    def create_label(self, box, text):
        """Adds a draggable label reading 'text' to the box
        """
        box_name = "box_" + box
        box_id = self.boxes.get(box_name)
        labels = self.box_labels(box = box_id)
        x0, y0 = anchor = self.anchors.get(box_id)
        n = len(labels)
        lab = tk.Canvas.create_text(self, x0, y0 + 20 * n,
                                    text = text,
                                    anchor = "nw",
                                    tags = (box, text, "label"))
        self.make_draggable(lab)
        self.config(scrollregion = self.bbox("all"))
        return None

    def make_draggable(self, item):
        self.tag_bind(item, "<Button-1>", self.select)
        self.tag_bind(item, "<B1-Motion>", self.drag)
        self.tag_bind(item, "<ButtonRelease-1>", self.drop)

    def get_box(self, item):
        """For a given item, returns the box it belongs to
        
        Assumes text labels only have box as a tag  !!
        Box will be a tuple, so only return first item
        """
        box_tag = ["box_" + t for t in self.gettags(item)
                   if "box_" + t in self.boxes.keys()][0]
        box = self.boxes.get(box_tag)
        return box

    def select(self, event):
        """Initialises necessary vars for the selected object
        """
        self.idx  = self.find_closest(event.x, event.y)
        idx = self.find_withtag("current")
        tab = self.get_box(idx)

        self.initial_coords = self.coords(idx)
        self.moveable_limits = self.bbox(tab)
        self.dragx = event.x
        self.dragy = event.y
        self.item_fill = self.itemcget(self.idx, "fill")
        self.itemconfig(self.idx, fill = "yellow")

    def drag(self, event):
        """Moves the label the distance between initial coords
           and final destination
        """
        dx = event.x - self.dragx
        dy = event.y - self.dragy
        self.dy = dy
        self.dragx = event.x
        self.dragy = event.y
        self.move(self.idx, dx, dy)

    def grid_round(self, x):
        x0 = round(float(x) / 20)
        return x0 * 20

    def box_labels(self, idx = False, box = False):
        """Return sorted lists of ids
        """
        if box == False:
            box = self.get_box(idx)     
        bbox = self.bbox(box)
        box_items = self.find_enclosed(*bbox)
        labels = [idx for idx in box_items 
                  if "label" in self.gettags(idx)]
        labels.sort(key = self.item_y)
        return labels

    def set_new_locations(self, labels_idx):
        box = self.get_box(self.idx)
        x0, y0 = self.anchors.get(box)
        print x0, y0
        #idx = upper_idx + lower_idx
        print labels_idx
        print "relocating"
        for i, idx in enumerate(labels_idx):
            print i, idx
            self.coords(idx, x0, y0 + i * 20)
            print "done"
        self.itemconfig(self.idx, fill = self.item_fill)
        return None

    def check_bbox(self, idx):
        x0_b, y0_b, x1_b, y1_b = self.bbox(idx)
        x0_M, y0_M, x1_M, y1_M = self.moveable_limits
        x_okay = ((x0_b in range(x0_M, x1_M)) & 
                  (x1_b in range(x0_M, x1_M)))
        y_okay = ((y0_b in range(y0_M, y1_M)) & 
                  (y1_b in range(y0_M, y1_M)))
        return x_okay & y_okay

    def item_y(self, idx):
        return self.coords(idx)[1]

    def drop(self, event):
        y_possible = self.grid_round(event.y)
        x_possible = self.grid_round(event.x)

        miny = self.moveable_limits[1]
        maxy = self.moveable_limits[3]

        print "Potential x and y"
        print x_possible
        print y_possible
        print "moveable limits", self.moveable_limits
        
        check_bbox = self.check_bbox(self.idx)
        if check_bbox == False:
            self.itemconfig(self.idx, fill = self.item_fill)
            self.coords(self.idx, *self.initial_coords)
            print "Overstepping bounds!"
        elif check_bbox == True:
            labels = self.box_labels(self.idx)
            #rint "Moving up and down"
            #print upper, lower
            self.set_new_locations(labels)

def test_this(layout,  ncol, field_float):
    root = tk.Tk()
    bob = DraggableCanvas(root, ncol, field_float)
    return bob

test_params = ("Harry", "Cora", "Amadi", "Will", "Jorge")
v = test_this("l", 3, True)
v.create_partitions(test_params)
