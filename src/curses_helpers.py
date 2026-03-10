import curses

def add_color(colors, name, color):
    color_number = None
    if name in colors:
        color_number = colors[name]
    else:
        color_number = len(colors) + 1 + 16
    curses.init_color(color_number, *color)
    colors[name] = color_number


def add_color_pair(color_pairs, name, fg_color, bg_color):
    if name in color_pairs:
        pair_number = curses.pair_number(color_pairs[name])
    else:
        pair_number = len(color_pairs) + 1
    curses.init_pair(pair_number, fg_color, bg_color)
    color_pairs[name] = curses.color_pair(pair_number)

    
    
def write(stdscr, x, y, text, allign="left", color_pair=None):
    if allign == "center":
        x = max(0, x - len(text) // 2)
    if allign == "right":
        x = max(0, x - len(text))
    
    try:
        if color_pair:
            stdscr.addstr(y, x, text, color_pair)
        else:
            stdscr.addstr(y, x, text)
    except curses.error:
        pass
    
def key_down(keys, key):
    if key not in keys or keys[key] in ("UP", "UNPRESSED"):
        keys[key] = "PRESSED"
    else:
        keys[key] = "DOWN"
    
def key_up(keys, key):
    if key not in keys or keys[key] == "UP":
        keys[key] = "UP"
    elif keys[key] in ("DOWN", "PRESSED"):
        keys[key] = "UNPRESSED"
    else:
        keys[key] = "UP"