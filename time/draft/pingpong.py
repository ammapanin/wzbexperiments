

class Pingpong:
    def __init__(self):
        self.steps = xrange(0, 200, 20)
        self.checked = [min(steps), max(steps)]
        self.c0 = 40

    def pingpong(self, choice):
        cdic = {0: (min(self.checked), self.c0),
                1: (self.c0, max(self.checked))} 
        min_c, max_c = cdic.get(choice)
        go_next = self.fill(min_c, max_c)
        
        if go_next == True:
            cnext = self.get_next()
            self.c0 = cnext
            print "cnext", cnext
        elif go_next == False:
            cnext = self.end_pingpong()
        return None

    def fill(self, mmin, mmax):
        print mmin, mmax
        fill_check = range(mmin, mmax + 20, 20)
        print fill_check
        self.checked.extend(fill_check)
        checked_set = set(self.checked)
        self.checked = list(checked_set)
        return len(checked_set) != len(self.steps)

    def get_next(self):
        cmin = max([i for i, c in enumerate(self.steps) 
                    if (c in self.checked and c < self.c0)])
        cmax = min([i for i, c in enumerate(self.steps) 
                    if (c in self.checked and c > self.c0)])
        print "idx", cmin, cmax
        idx = cmin + int(round(float(cmax - cmin) / 2))
        amt = self.steps[idx]
        return amt

    def end_pingpong(self):
        print "End"
        
    

p = Pingpong()
