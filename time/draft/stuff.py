

def grid_xy(n):
    i = 0
    x = 0
    while i < n:
        if i % 2 == 0:
            yield x, 0
        else:
            yield x, 1
            x += 1
        i += 1
