import discord
import threading
import asyncio


class SpiteDiscordClient():
    
    def __init__(self, token):
        self.token = token
        self.is_online = False
        
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        
        self.num_servers = 0
        self.num_channels = []
        
        @self.client.event
        async def on_ready():
            print(f'Logged in as {self.client.user}')
            self.is_online = True
            self.num_servers = len(self.get_servers())
            self.num_channels = [len(self.get_channels(server)) for server in self.get_servers()]
            

    def run(self):
        thread = threading.Thread(
            target=self.client.run,
            kwargs={"token": self.token},
            daemon=True,
        )
        thread.start()
        return thread
    
    def get_servers(self):
        return self.client.guilds
    
    def get_channels(self, server):
        if server is None:
            return []
        return [channel for channel in server.channels if hasattr(channel, "history") and channel.type in (discord.ChannelType.text, discord.ChannelType.forum)]
    
    def get_messages(self, channel, limit=100):
        if channel is None or not hasattr(channel, "history"):
            return []

        loop = getattr(self.client, "loop", None)
        if loop is None or not loop.is_running():
            return []

        async def collect_messages():
            results = []
            async for message in channel.history(limit=limit):
                results.append(message)
            return results

        try:
            future = asyncio.run_coroutine_threadsafe(collect_messages(), loop)
            return future.result(timeout=2)
        except Exception:
            return []