import asyncio
import os
import threading
from typing import Any

import discord
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
import uvicorn

load_dotenv()


class DiscordBridge:
	def __init__(self, token: str):
		self.token = token
		self.is_ready = False

		intents = discord.Intents.default()
		intents.message_content = True
		self.client = discord.Client(intents=intents)

		@self.client.event
		async def on_ready() -> None:
			self.is_ready = True

	def run(self) -> threading.Thread:
		thread = threading.Thread(
			target=self.client.run,
			kwargs={"token": self.token},
			daemon=True,
		)
		thread.start()
		return thread

	def _require_ready_loop(self) -> asyncio.AbstractEventLoop:
		loop = getattr(self.client, "loop", None)
		if not self.is_ready or loop is None or not loop.is_running():
			raise HTTPException(status_code=503, detail="Discord client is not ready")
		return loop

	def get_servers(self) -> list[dict[str, Any]]:
		loop = self._require_ready_loop()

		async def _collect() -> list[dict[str, Any]]:
			return [{"id": guild.id, "name": guild.name} for guild in self.client.guilds]

		try:
			future = asyncio.run_coroutine_threadsafe(_collect(), loop)
			return future.result(timeout=5)
		except Exception as exc:
			raise HTTPException(status_code=502, detail=f"Failed to read servers: {exc}") from exc

	def get_channels(self, server_id: int) -> list[dict[str, Any]]:
		loop = self._require_ready_loop()

		async def _collect() -> list[dict[str, Any]]:
			guild = self.client.get_guild(server_id)
			if guild is None:
				return []

			channels: list[dict[str, Any]] = []
			for channel in guild.channels:
				if hasattr(channel, "history") and channel.type in (
					discord.ChannelType.text,
					discord.ChannelType.news,
					discord.ChannelType.public_thread,
					discord.ChannelType.private_thread,
				):
					channels.append({"id": channel.id, "name": channel.name})
			return channels

		try:
			future = asyncio.run_coroutine_threadsafe(_collect(), loop)
			return future.result(timeout=5)
		except Exception as exc:
			raise HTTPException(status_code=502, detail=f"Failed to read channels: {exc}") from exc

	def get_messages(self, channel_id: int, limit: int = 100) -> list[dict[str, Any]]:
		loop = self._require_ready_loop()

		async def _collect() -> list[dict[str, Any]]:
			channel = self.client.get_channel(channel_id)
			if channel is None or not hasattr(channel, "history"):
				return []

			messages: list[dict[str, Any]] = []
			async for message in channel.history(limit=limit):
				msg_dict = {
					"id": message.id,
					"content": message.content,
					"author": {"id": message.author.id, "name": message.author.name},
					"created_at": message.created_at.isoformat() if message.created_at else None,
				}
				if message.reference:
					reference_data: dict[str, Any] = {
						"message_id": message.reference.message_id,
						"channel_id": message.reference.channel_id,
						"guild_id": message.reference.guild_id,
					}
					resolved = getattr(message.reference, "resolved", None)
					if resolved is None and message.reference.channel_id and message.reference.message_id:
						ref_channel = self.client.get_channel(message.reference.channel_id)
						if ref_channel is not None and hasattr(ref_channel, "fetch_message"):
							try:
								resolved = await ref_channel.fetch_message(message.reference.message_id)
							except Exception:
								resolved = None
					if resolved is not None and hasattr(resolved, "author"):
						reference_data["resolved"] = {
							"id": getattr(resolved, "id", None),
							"content": getattr(resolved, "content", ""),
							"author": {
								"id": getattr(getattr(resolved, "author", None), "id", None),
								"name": getattr(getattr(resolved, "author", None), "name", "unknown"),
							},
						}
					msg_dict["reference"] = reference_data
				if message.attachments:
					msg_dict["attachments"] = [
						{"id": a.id, "filename": a.filename, "size": a.size, "url": a.url}
						for a in message.attachments
					]
				messages.append(msg_dict)
			return messages

		try:
			future = asyncio.run_coroutine_threadsafe(_collect(), loop)
			return future.result(timeout=8)
		except Exception as exc:
			raise HTTPException(status_code=502, detail=f"Failed to read messages: {exc}") from exc


token = os.getenv("DISCORD_BOT_TOKEN")
if not token:
	raise RuntimeError("DISCORD_BOT_TOKEN is missing in proxy_src/.env")

bridge = DiscordBridge(token)
app = FastAPI(title="SpiteCLI Discord Proxy")


@app.on_event("startup")
def startup() -> None:
	bridge.run()


@app.get("/get_servers")
def get_servers() -> list[dict[str, Any]]:
	return bridge.get_servers()


@app.get("/get_channels/{server}")
def get_channels(server: int) -> list[dict[str, Any]]:
	return bridge.get_channels(server)


@app.get("/get_messages/{channel}")
def get_messages(channel: int, limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, Any]]:
	return bridge.get_messages(channel, limit)


if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)