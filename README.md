# SpiteCLI
SpiteCLI is a Terminal UI for browsing Discord Channels and DMs. 


It is only meant for bots, since controlling real accounts is against Discord TOS.


# Install Instructions

1. If on Windows, install the `curses` package using ```pip install windows-curses```

2. Install API proxy dependencies with ```pip install -r proxy_src/requirements.txt```

3. Install TUI dependencies with ```pip install -r src/requirements.txt```

4. Create `proxy_src/.env` with `DISCORD_BOT_TOKEN=`

5. Start the proxy API from `proxy_src`:
	- ```uvicorn main:app --reload```

6. Optional: set `SPITE_PROXY_URL` for the TUI (default is `http://127.0.0.1:8000`)