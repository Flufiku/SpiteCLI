import curses
import os
from dotenv import load_dotenv
load_dotenv()

from curses_helpers import *
from spite_discord_client import SpiteDiscordClient










def main(stdscr):
    client = SpiteDiscordClient(os.getenv("DISCORD_BOT_TOKEN"))
    client.run()
    
    state = ""
    last_state = ""
    t = 0   # Total on time
    ls = 0  # Time since last state change
    
    colors = {}
    color_pairs = {}

    keys = {}
    
    # Variables for states
    v = {}
    
    curses.curs_set(0)
    stdscr.nodelay(True)

    if curses.has_colors() and curses.can_change_color() and curses.COLORS > 8:
        curses.start_color()
        add_color(colors, "grey", (300, 300, 300))
        add_color_pair(color_pairs, "highlight", curses.COLOR_WHITE, colors["grey"])
        
        add_color(colors, "green", (0, 1000, 0))
        add_color_pair(color_pairs, "green_highlight", colors["green"], colors["grey"])

        add_color(colors, "red", (1000, 0, 0))
        add_color_pair(color_pairs, "error", colors["red"], curses.COLOR_BLACK)

        init_sender_name_color_pairs(colors, color_pairs)

    while True:
		
        state, last_state, ls = next_state(state, last_state, stdscr, keys, client, t, ls, v)
  
        key_input(stdscr, keys, v)
  
        draw(state, last_state, stdscr, client, t, ls, colors, color_pairs, keys, v)

        
        t += 1
        ls += 1
        curses.napms(20)




def draw(state, last_state, stdscr, client, t, ls, colors, color_pairs, keys, v):
    stdscr.erase()

    height, width = stdscr.getmaxyx()
    
    if state == "ERROR_TOO_SMALL":
        write(stdscr, 0, 0, "Window must be at least 80x24.")
        write(stdscr, 0, 1, f"Current size: {width}x{height}", color_pair=color_pairs["error"])
        stdscr.refresh()
        return
        
    if state == "ERROR_NO_COLORS":
        write(stdscr, 0, 0, "Terminal does not support more than 8 custom colors")
        stdscr.refresh()
        return
    
    if state == "ERROR_OFFLINE":
        write(stdscr, 0, 0, "Discord client is offline", color_pair=color_pairs["error"])
        stdscr.refresh()
        return
    
    
    
    if state == "STARTUP" or state == "STARTUP_DONE":
        write(stdscr, width//2, height//2, "Starting...", allign="center", color_pair=color_pairs["highlight"])
        
        original_coords = (width//2, height//2 + 5) # Origin coords
        coords = [
            [original_coords[0], original_coords[1]],
            [original_coords[0]+1, original_coords[1]+1],
            [original_coords[0]+2, original_coords[1]+2],
            [original_coords[0]+3, original_coords[1]+2],
            [original_coords[0]+4, original_coords[1]+2],
            [original_coords[0]+5, original_coords[1]+1],
            [original_coords[0]+5, original_coords[1]],
            [original_coords[0]+5, original_coords[1]-1],
            [original_coords[0]+4, original_coords[1]-2],
            [original_coords[0]+3, original_coords[1]-2],
            [original_coords[0]+2, original_coords[1]-2],
            [original_coords[0]+1, original_coords[1]-1],
            [original_coords[0], original_coords[1]],
            [original_coords[0]-1, original_coords[1]+1],
            [original_coords[0]-2, original_coords[1]+2],
            [original_coords[0]-3, original_coords[1]+2],
            [original_coords[0]-4, original_coords[1]+2],
            [original_coords[0]-5, original_coords[1]+1],
            [original_coords[0]-5, original_coords[1]],
            [original_coords[0]-5, original_coords[1]-1],
            [original_coords[0]-4, original_coords[1]-2],
            [original_coords[0]-3, original_coords[1]-2],
            [original_coords[0]-2, original_coords[1]-2],
            [original_coords[0]-1, original_coords[1]-1]
        ]
        """
        for coord in coords:
            write(stdscr, coord[0], coord[1], "#")
        """
        """
        for i in range(len(coords)):
            temp_name = f"temp_{i}"
            add_color(colors, temp_name, (int(i/(len(coords)-1)*1000), 0, 0))
            add_color_pair(color_pairs, temp_name, colors[temp_name], curses.COLOR_BLACK)
            write(stdscr, coords[(t+i)%len(coords)][0], coords[(t+i)%len(coords)][1], "#", color_pair=color_pairs[temp_name])
        """
        """
        num = len(coords)
        iterations = abs((t - (num - 1)) % (2 * (num - 1)) - (num - 1))
        for i in range(0, iterations):
            write(stdscr, coords[(i)%len(coords)][0], coords[(i)%len(coords)][1], "#")
        """
        """"""
        num = len(coords)
        iterations_lower = max(0, (t % (2 * num)) - num)
        iterations_upper = min(t % (2 * num), num)
        for i in range(iterations_lower, iterations_upper):
            write(stdscr, coords[(i)%len(coords)][0], coords[(i)%len(coords)][1], "#")
        
        stdscr.refresh()
        return
    
    if state == "HALT":
        write(stdscr, width//2, height//2, "Shutting Down...", allign="center", color_pair=color_pairs["highlight"])
    
    if state == "HELP":
        write(stdscr, width//2, height//2 - 1, "Help Menu", allign="center", color_pair=color_pairs["highlight"])
        write(stdscr, width//2, height//2 + 1, "Press F1 or ESC to return", allign="center")
        write(stdscr, width//2, height//2 + 2, "Use WASD or arrow keys to navigate", allign="center")
        stdscr.refresh()
        return
    
    if state == "ONLINE":
        sidebar_width = 12
        
        if not "y_s" in v:
            v["y_s"] = 0
        if not "y_c" in v:
            v["y_c"] = 0
        if not "last_y_s" in v:
            v["last_y_s"] = -1
        if not "last_y_c" in v:
            v["last_y_c"] = -1
        if not "x" in v:
            v["x"] = 0
        if not "servers" in v:
            v["servers"] = []
        if not "channels" in v:
            v["channels"] = []
        if not "messages" in v:
            v["messages"] = []
        
        if keys.get("LEFT", "UP") in ("PRESSED", "DOWN"):
            v["x"] -= 1
        if keys.get("RIGHT", "UP") in ("PRESSED", "DOWN"):
            v["x"] += 1
        v["x"] = max(0, min(1, v["x"]))    
             
        if keys.get("UP", "UP") in ("PRESSED", "DOWN"):
            if v["x"] == 0:
                v["y_s"] -= 1
            else:
                v["y_c"] -= 1
        if keys.get("DOWN", "UP") in ("PRESSED", "DOWN"):
            if v["x"] == 0:
                v["y_s"] += 1
            else:
                v["y_c"] += 1

        v["y_s"] = max(0, min(v["y_s"], client.num_servers - 1))
        v["y_c"] = max(0, min(v["y_c"], client.num_channels[v["y_s"]] - 1))


        if v["y_s"] != v["last_y_s"]:
            v["y_c"] = 0
        
        if v["y_s"] != v["last_y_s"] or v["y_c"] != v["last_y_c"]:
            v["servers"] = client.get_servers()
            v["channels"] = client.get_channels(v["servers"][v["y_s"]]) if len(v["servers"]) > 0 else []
            v["messages"] = client.get_messages(v["channels"][v["y_c"]]) if len(v["channels"]) > 0 else []
        
        v["last_y_s"] = v["y_s"]
        v["last_y_c"] = v["y_c"]

        for _ in range(height):
            write(stdscr, sidebar_width-1, _, "│")
            
        for _ in range(height):
            write(stdscr, 2*sidebar_width-1, _, "│")
        
        
        
        
        for i, server in enumerate(v["servers"]):
            if i == v["y_s"]:
                if v["x"] == 0:
                    write(stdscr, 0, i, server.name[:sidebar_width-1], color_pair=color_pairs["green_highlight"])
                else:
                    write(stdscr, 0, i, server.name[:sidebar_width-1], color_pair=color_pairs["highlight"])
            else:
                write(stdscr, 0, i, server.name[:sidebar_width-1])
        for i, channel in enumerate(v["channels"]):
            if i == v["y_c"]:
                if v["x"] == 1:
                    write(stdscr, sidebar_width, i, channel.name[:sidebar_width-1], color_pair=color_pairs["green_highlight"])
                else:
                    write(stdscr, sidebar_width, i, channel.name[:sidebar_width-1], color_pair=color_pairs["highlight"])
            else:
                write(stdscr, sidebar_width, i, channel.name[:sidebar_width-1])
        for i, message in enumerate(v["messages"]):
            if i >= height - 10:
                break
            name_len = len(message.author.name)
            write(stdscr, 2*sidebar_width, height - 10 - i, message.author.name + ": ", color_pair=get_sender_name_color_pair(message.author.name, color_pairs))
            write(stdscr, 2*sidebar_width+name_len+2 , height - 10 - i, strip_unrenderable_chars(message.content)[:width-2*sidebar_width-2-name_len])
        

        debug_width = max(0, width - 2*sidebar_width)
        write(stdscr, 2*sidebar_width, height - 4, f"Debug: {v['y_s']}, {v['y_c']}, {v['x']}"[:debug_width])
        write(stdscr, 2*sidebar_width, height - 3, f"{client.num_servers}, {client.num_channels[v['y_s']]}"[:debug_width])
        write(stdscr, 2*sidebar_width, height - 2, f"getch: {keys.get('_getch', None)} ({keys.get('_getch_name', '')})"[:debug_width])
        write(stdscr, 2*sidebar_width, height - 1, f"keys: {keys}"[:debug_width])

        
        stdscr.refresh()
        return





def key_input(stdscr, keys, v):
    key = stdscr.getch()
    keys["_getch"] = key
    if key == -1:
        keys["_getch_name"] = "NO_INPUT"
    else:
        try:
            keys["_getch_name"] = curses.keyname(key).decode("utf-8", errors="replace")
        except Exception:
            keys["_getch_name"] = "UNKNOWN"

    if key in (ord("q"), ord("Q")):
        key_down(keys, "q")
    else:
        key_up(keys, "q")
        
    if key in (curses.KEY_F1,):
        key_down(keys, "F1")
    else:
        key_up(keys, "F1")
    
    if key in (27,):
        key_down(keys, "ESC")
    else:    
        key_up(keys, "ESC")
        
    if key in (curses.KEY_UP, ord("w"), ord("W")):
        key_down(keys, "UP")
    else:
        key_up(keys, "UP")

    if key in (curses.KEY_DOWN, ord("s"), ord("S")):
        key_down(keys, "DOWN")
    else:
        key_up(keys, "DOWN")

    if key in (curses.KEY_LEFT, ord("a"), ord("A")):
        key_down(keys, "LEFT")
    else:
        key_up(keys, "LEFT")

    if key in (curses.KEY_RIGHT, ord("d"), ord("D")):
        key_down(keys, "RIGHT")
    else:
        key_up(keys, "RIGHT")



def next_state(state, last_state, stdscr, keys, client, t, ls, v):
    if state == "HALT":
        curses.endwin()
        exit()

    if keys.get("q", "UP") in ("PRESSED", "DOWN"):
        return "HALT", state, 0
    
    
    if not curses.can_change_color() or not curses.has_colors() or curses.COLORS <= 8:
        if state != "ERROR_NO_COLORS":
            return "ERROR_NO_COLORS", state, 0
        else:
            return "ERROR_NO_COLORS", last_state, ls
        
    if not state == "STARTUP" and not state == "" and not client.is_online:
        if state != "ERROR_OFFLINE":
            return "ERROR_OFFLINE", state, 0
        else:
            return "ERROR_OFFLINE", last_state, ls
    
    if stdscr.getmaxyx()[0] < 24 or stdscr.getmaxyx()[1] < 80:
        if state != "ERROR_TOO_SMALL":
            return "ERROR_TOO_SMALL", state, 0
        else:
            return "ERROR_TOO_SMALL", last_state, ls





    if state == "":
        return "STARTUP", state, 0

    if state == "STARTUP":
        if ls > 120 or client.is_online:
            return "STARTUP_DONE", state, 0

    if state == "STARTUP_DONE":
        if client.is_online:
            return "ONLINE", state, 0
    
    if state == "HELP":
        if keys.get("F1", "UP") in ("PRESSED", "DOWN") or keys.get("ESC", "UP") in ("PRESSED", "DOWN"):
            return last_state, state, 0
    else:
        if keys.get("F1", "UP") in ("PRESSED", "DOWN"):
            return "HELP", state, 0
    
    if state == "ERROR_OFFLINE":
        if client.is_online:
            return last_state, state, 0
    
    if state == "ERROR_TOO_SMALL":
        if stdscr.getmaxyx()[0] >= 24 and stdscr.getmaxyx()[1] >= 80:
            return last_state, state, 0
    
    
    return state, last_state, ls
        
    
        
    
if __name__ == "__main__":
	curses.wrapper(main)
