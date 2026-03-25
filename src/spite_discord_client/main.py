import threading
import time
from types import SimpleNamespace

import requests


class SpiteDiscordClient():
    
    def __init__(self, base_url):
        self.base_url = (base_url or "http://127.0.0.1:8000").rstrip("/")
        self.is_online = False

        self.num_servers = 0
        self.num_channels = []
        self._polling = False
        self._poll_thread = None
            

    def run(self):
        if self._polling:
            return self._poll_thread

        self._polling = True

        def poll_status():
            while self._polling:
                try:
                    servers = self.get_servers()
                    self.is_online = True
                    self.num_servers = len(servers)
                    self.num_channels = [len(self.get_channels(server)) for server in servers]
                except Exception:
                    self.is_online = False
                    self.num_servers = 0
                    self.num_channels = []
                time.sleep(1.0)

        self._poll_thread = threading.Thread(target=poll_status, daemon=True)
        self._poll_thread.start()
        return self._poll_thread

    def _get(self, path, params=None):
        response = requests.get(f"{self.base_url}{path}", params=params, timeout=3)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _to_server(server_data):
        return SimpleNamespace(id=server_data["id"], name=server_data["name"])

    @staticmethod
    def _to_channel(channel_data):
        return SimpleNamespace(id=channel_data["id"], name=channel_data["name"])

    @staticmethod
    def _to_message(message_data):
        author = message_data.get("author", {})
        return SimpleNamespace(
            id=message_data.get("id"),
            content=message_data.get("content", ""),
            author=SimpleNamespace(
                id=author.get("id"),
                name=author.get("name", "unknown")
            ),
            created_at=message_data.get("created_at"),
        )
    
    def get_servers(self):
        data = self._get("/get_servers")
        return [self._to_server(server_data) for server_data in data]
    
    def get_channels(self, server):
        if server is None:
            return []
        data = self._get(f"/get_channels/{server.id}")
        return [self._to_channel(channel_data) for channel_data in data]
    
    def get_messages(self, channel, limit=100):
        if channel is None:
            return []

        try:
            data = self._get(f"/get_messages/{channel.id}", params={"limit": limit})
            return [self._to_message(message_data) for message_data in data]
        except Exception:
            return []