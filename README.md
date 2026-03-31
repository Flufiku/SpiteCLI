# SpiteCLI
SpiteCLI is a Terminal UI for browsing Discord Channels and DMs of Discord Bots. 


It is only meant for bots, since controlling real accounts is against Discord TOS.



# How to use:
* To start the program, double click the `.exe` file downloaded from the releases tab. (see install instructions below).
* Wait until the Client connects to the proxy server.
* Navigate between channels and servers using the arrow keys.
* Press `F1` for the help menu with all controls.

# Install Instructions from Release

1. Download the latest release from the releases tab.
2. Run the `.exe` file.
3. Thats it, enjoy.

# Install Instructions from Source

1. If on Windows, install the `curses` package using ```pip install windows-curses```

2. Install API proxy dependencies with ```pip install -r proxy_src/requirements.txt```

3. Install TUI dependencies with ```pip install -r src/requirements.txt```

4. Create `proxy_src/.env` with `DISCORD_BOT_TOKEN=`

5. Start the proxy API from `proxy_src`:
	- ```uvicorn main:app --reload```

6. Optional: set `SPITE_PROXY_URL` for the TUI (default is `http://127.0.0.1:8000`)