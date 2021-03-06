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
    def __init__(self, master, *args, **kwargs):
        tk.Canvas.__init__(self, master, *args, **kwargs)

    def update_tabs(self, tab_list):
        existing_tabs = self.find_withtag("tab")

        tab_font = tkFont.Font(size = 13, weight = "bold")
        tabs = [self.create_text(5, i * 40,
                                 font = tab_font,
                                 text = txt, anchor = "nw",
                                 tags = ("tab", txt))
                for i, txt in enumerate(tab_list)]
        self.tab_texts = tab_list
        self.config(scrollregion = self.bbox("all"))
        print "anything fishy?"
        return tab_list

    def change_label_tab(self, idx, new_tab, text):
        self.delete(idx)
        self.create_label(new_tab, text)
        return None

    def create_label(self, tab, text, **args):
        label_exists = len(self.find_withtag(text)) > 0

        if label_exists == True:
            idx = self.find_withtag(text)[0]
            tags = self.gettags(idx)
            old_tab = tags[0][0:-3]
            if old_tab == tab:
                pass
            else:
                self.change_label_tab(idx, tab, text)
        elif label_exists == False:
            anchor_tab = self.find_withtag(tab)
            co_tabs = self.find_withtag(tab + "_co")
            anchor = self.coords(anchor_tab)[1] + 20
            n = len(co_tabs)
            y = anchor + n * 20

            other_tabs = [t for t in self.tab_texts if t != tab]
            other_idxs = [(t, self.find_withtag(t)) for t in other_tabs]

            for other_name, other_idx in other_idxs:
                other_anchor = self.coords(other_idx)[1]
                if other_anchor > anchor:
                    dependents = self.find_withtag(other_name + "_co")
                    for item in  other_idx + dependents:
                        x0, y0 = self.coords(item)
                        self.coords(item, x0, y0 + 20)
                elif other_anchor <= anchor:
                    pass

            li = tk.Canvas.create_text(self, 5, y,
                                       text = text,
                                       anchor = "nw",
                                       tags = (tab + "_co", text),
                                       **args)
            self.make_draggable(li)
            self.config(scrollregion = self.bbox("all"))
        return None

    def make_draggable(self, item):
        self.tag_bind(item, "<Button-1>", self.select)
        self.tag_bind(item, "<B1-Motion>", self.drag)
        self.tag_bind(item, "<ButtonRelease-1>", self.drop)

    def get_tab_from_tags(self, item):
        tags = self.gettags(item)
        print tags
        print self.tab_texts
        tab_co = [t for t in tags if t[0:-3] in self.tab_texts]
        print tab_co
        return tab_co[0]

    def grid_round(self, x):
        x0 = round(float(x) / 20)
        return x0 * 20

    def select(self, event):
        self.idx  = self.find_closest(event.x, event.y)
        idx = self.find_withtag("current")
        tab = self.get_tab_from_tags(idx)

        self.initial_coords = self.coords(idx)
        self.moveable_limits = self.bbox(tab)


        self.dragx = event.x
        self.dragy = event.y

        self.item_fill = self.itemcget(self.idx, "fill")
        self.itemconfig(self.idx, fill = "yellow")

    def drag(self, event):
        dx = event.x - self.dragx
        dy = event.y - self.dragy
        self.dy = dy

        self.dragx = event.x
        self.dragy = event.y

        self.move(self.idx, dx, dy)


    def drop(self, event):
        y_possible = self.grid_round(event.y)


        miny = self.moveable_limits[1]
        maxy = self.moveable_limits[3]

        print self.moveable_limits
        print miny
        print maxy
        print y_possible

        if y_possible < miny or y_possible > maxy:
            self.itemconfig(self.idx, fill = self.item_fill)
            self.coords(self.idx, *self.initial_coords)
            print "Overstepping bounds!"
        else:
            idx_0 = self.find_closest(4, y_possible)
            x0_all, y0_all, x1_all, y1_all = self.bbox("all")
            x0, y0, x1, y1 = self.bbox(idx_0)

            upper_bb = (0, y0_all, x1_all + 5, y1 + 2)
            lower_bb = (0, y0 + 1, x1_all + 5, y1_all + 5)

            directed_tags = (("lower", lower_bb),
                             ("upper", upper_bb))
            [self.addtag_enclosed(t, *bb) for t, bb in directed_tags]

            rm_tag = self.find_withtag("current")
            self.dtag(rm_tag, "upper")
            self.dtag(rm_tag, "lower")

            upper = list(self.find_withtag("upper"))
            lower = list(self.find_withtag("lower"))

            def sort_tags(t):
                return self.coords(t)[1]

            upper.sort(key = sort_tags)
            lower.sort(key = sort_tags)

            move_up = enumerate([(i, self.coords(i)) for i in upper])
            move_down = enumerate([(i, self.coords(i)) for i in lower])

            up_y = 0
            new_y = 0
            for i, tag_coords in move_up:
                tag, cds = tag_coords
                x, y = cds
                self.coords(tag, x, up_y + i * 20)
                new_y += 20
                down_y = new_y + 20
            for i, tag_coords in move_down:
                tag, cds = tag_coords
                x, y = cds
                self.coords(tag, x, down_y + i * 20)

            self.itemconfig(self.idx, fill = self.item_fill)
            self.coords(self.idx, 4, new_y)

        all_tags = self.find_withtag("all")
        [self.dtag(i, "upper") for i in all_tags]
        [self.dtag(i, "lower") for i in all_tags]
