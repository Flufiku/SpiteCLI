import curses
import os
from dotenv import load_dotenv
load_dotenv()

from helpers import *
from spite_discord_client import SpiteDiscordClient










def main(stdscr):
    client = SpiteDiscordClient(os.getenv("DISCORD_BOT_TOKEN"))
    client.run()
    
    state = "STARTUP"
    t = 0
    
    colors = {}
    color_pairs = {}
    
    curses.curs_set(0)
    stdscr.nodelay(True)

    if curses.has_colors() and curses.can_change_color() and curses.COLORS > 8:
        curses.start_color()
        add_color(colors, "grey", (300, 300, 300))
        add_color_pair(color_pairs, "highlight", curses.COLOR_WHITE, colors["grey"])

        add_color(colors, "red", (1000, 0, 0))
        add_color_pair(color_pairs, "red_on_black", colors["red"], curses.COLOR_BLACK)

    while True:
		
        key_input(stdscr)
  
        draw(stdscr, color_pairs)

        state = next_state(state, client, t)
        
        t += 1
        curses.napms(50)




def draw(stdscr, color_pairs={}):
    stdscr.erase()

    height, width = stdscr.getmaxyx()
    
    if width < 80 or height < 24:
        try:
            stdscr.addstr(0, 0, "Window must be at least 80x24.")
            stdscr.addstr(1, 0, f"Current size: {width}x{height}", color_pairs["red_on_black"])
        except curses.error:
            pass
        stdscr.refresh()
        return
        
    if not curses.can_change_color() or not curses.has_colors() or curses.COLORS <= 8:
        try:
            stdscr.addstr(0, 0, "Terminal does not support more than 8 custom colors")
        except curses.error:
            pass
        stdscr.refresh()
        return
    
        
    label = f"{width}*{height}"

    y = height // 2
    x = max(0, (width - len(label)) // 2)
    
    try:
        stdscr.addstr(y, x, label, color_pairs["highlight"])
    except curses.error:
        pass

    stdscr.refresh()



def key_input(stdscr):
    key = stdscr.getch()
    if key in (ord("q"), ord("Q")):
        curses.endwin()
        exit()



def next_state(state, client, t):
    if not state == "STARTUP" and not client.is_online:
        return "OFFLINE"


    if state == "STARTUP":
        if t > 20:
            return "STARTUP_DONE"

    if state == "STARTUP_DONE":
        if client.is_online:
            return "ONLINE"
    
    elif state == "OFFLINE":
        if client.is_online:
            return "ONLINE"
    
    
    return state 
        
    
        
    
if __name__ == "__main__":
	curses.wrapper(main)
