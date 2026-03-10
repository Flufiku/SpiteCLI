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
    
    curses.curs_set(0)
    stdscr.nodelay(True)

    if curses.has_colors() and curses.can_change_color() and curses.COLORS > 8:
        curses.start_color()
        add_color(colors, "grey", (300, 300, 300))
        add_color_pair(color_pairs, "highlight", curses.COLOR_WHITE, colors["grey"])

        add_color(colors, "red", (1000, 0, 0))
        add_color_pair(color_pairs, "error", colors["red"], curses.COLOR_BLACK)

    while True:
		
        state, last_state, ls = next_state(state, last_state, stdscr, keys, client, t, ls)
  
        key_input(stdscr, keys)
  
        draw(state, last_state, stdscr, client, t, ls, colors, color_pairs, keys)

        
        t += 1
        ls += 1
        curses.napms(20)




def draw(state, last_state, stdscr, client, t, ls, colors, color_pairs, keys):
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
        write(stdscr, width//2, height//2, "Help Menu", allign="center", color_pair=color_pairs["highlight"])
        write(stdscr, width//2, height//2 + 1, "Press F1 or ESC to return", allign="center")
        stdscr.refresh()
        return
    
    if state == "ONLINE":
        write(stdscr, width//2, height//2, "Online", allign="center", color_pair=color_pairs["highlight"])
        
        for _ in range(height):
            write(stdscr, 9, _, "│")
            
        for _ in range(height):
            write(stdscr, 19, _, "│")
        """
        servers = client.get_servers()
        channels = client.get_channels(servers[0]) if len(servers) > 0 else []
        messages = client.get_messages(channels[0]) if len(channels) > 0 else []
        
        
        
        for i, server in enumerate(servers):
            write(stdscr, 0, i, server.name[:9])
        for i, channel in enumerate(channels):
            write(stdscr, 10, i, channel.name[:9])
        for i, message in enumerate(messages):
            name_len = len(message.author.name)
            write(stdscr, 20, i, message.author.name)
            write(stdscr, 20+name_len, i, ": " + message.content[:width-22-name_len])
        """

        debug_width = max(0, width - 20)
        write(stdscr, 20, height - 2, f"getch: {keys.get('_getch', None)} ({keys.get('_getch_name', '')})"[:debug_width])
        write(stdscr, 20, height - 1, f"keys: {keys}"[:debug_width])
            
        
        stdscr.refresh()
        return





def key_input(stdscr, keys):
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



def next_state(state, last_state, stdscr, keys, client, t, ls):
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
