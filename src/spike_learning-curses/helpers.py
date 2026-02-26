import curses

def add_color(colors, name, color):
    color_number = len(colors) + 1 + 16
    curses.init_color(color_number, *color)
    colors[name] = color_number

def add_color_pair(color_pairs, name, fg_color, bg_color):
    pair_number = len(color_pairs) + 1
    curses.init_pair(pair_number, fg_color, bg_color)
    color_pairs[name] = curses.color_pair(pair_number)