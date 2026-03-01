import discord
import threading


class SpiteDiscordClient():
    
    def __init__(self, token):
        self.token = token
        self.is_online = False
        
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        
        @self.client.event
        async def on_ready():
            print(f'Logged in as {self.client.user}')
            self.is_online = True
            
            
    def run(self):
        thread = threading.Thread(
            target=self.client.run,
            kwargs={"token": self.token},
            daemon=True,
        )
        thread.start()
        return thread