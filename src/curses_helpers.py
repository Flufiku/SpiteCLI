import curses
import colorsys


SENDER_NAME_COLOR_COUNT = 27


def strip_unrenderable_chars(text):
    if text is None:
        return ""

    result = []
    for char in str(text):
        code = ord(char)

        # Block emoji ranges and surrogates
        if 0xD800 <= code <= 0xDFFF:  # Surrogate pairs
            continue
        if code >= 0x1F000:  # Emoji and pictographs start here
            continue

        # Keep everything else: ASCII, symbols, box drawing, etc.
        result.append(char)

    return "".join(result)

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


def _sender_name_color_index(sender_name):
    if not sender_name:
        return SENDER_NAME_COLOR_COUNT - 1

    first_char = str(sender_name)[0].upper()
    if "A" <= first_char <= "Z":
        return ord(first_char) - ord("A")

    return SENDER_NAME_COLOR_COUNT - 1


def init_sender_name_color_pairs(colors, color_pairs):
    for i in range(SENDER_NAME_COLOR_COUNT):
        hue = 5*i / SENDER_NAME_COLOR_COUNT
        red, green, blue = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        color_name = f"sender_name_color_{i}"
        pair_name = f"sender_name_pair_{i}"

        try:
            add_color(colors, color_name, (round(red * 1000), round(green * 1000), round(blue * 1000)))
            add_color_pair(color_pairs, pair_name, colors[color_name], curses.COLOR_BLACK)
        except curses.error:
            break


def get_sender_name_color_pair(sender_name, color_pairs):
    index = _sender_name_color_index(sender_name)
    return color_pairs.get(f"sender_name_pair_{index}")

    
    
def write(stdscr, x, y, text, allign="left", color_pair=None):
    text = strip_unrenderable_chars(text)

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