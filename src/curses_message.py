import discord
import curses
from curses_helpers import get_sender_name_color_pair, strip_unrenderable_chars, write


def _display_name(author):
    if author is None:
        return "unknown"
    return strip_unrenderable_chars(getattr(author, "name", author)) or "unknown"


def _message_content(message):
    if message is None:
        return ""
    return strip_unrenderable_chars(getattr(message, "content", ""))

class SpiteMessage:
    def __init__(self, message: discord.message.Message, width: int):
        self.message = message
        self.content = _message_content(message)
        self.author = _display_name(getattr(message, "author", None))

        message_reference = getattr(message, 'reference', None)
        self.ref_message = getattr(message_reference, "resolved", None) if message_reference else None
        self.ref_message_author = _display_name(getattr(self.ref_message, "author", None)) if self.ref_message else None
        self.ref_message_content = _message_content(self.ref_message) if self.ref_message else ""
        self.attachments = getattr(message, 'attachments', [])
        
        self.render_size = self.calculate_render_size(width)
        
    def calculate_render_size(self, width):
        message_text_list = self._get_message_text_lines(width - len(self.author) - 2)
        
        num_lines = len(message_text_list)
        num_lines += len(self.attachments)  # Each attachment takes one line
        if self.ref_message:
            num_lines += 1  # Reference message takes one line
        return num_lines
    
    def render(self, stdscr, x, y, width, color_pairs):
        # Render reference message if exists
        if self.ref_message:
            write(stdscr, x, y, "↱", color_pair=color_pairs.get("grey_text"))
            write(stdscr, x+1, y, f"{self.ref_message_author[:width-1]}:", color_pair=get_sender_name_color_pair(self.ref_message_author, color_pairs))
            write(stdscr, x+1+len(self.ref_message_author), y, f" {self.ref_message_content[:width-1-len(self.ref_message_author)]}", color_pair=color_pairs.get("grey_text"))
            y += 1
        
        # Render author and content
        message_text_list = self._get_message_text_lines(width)
        
        
        write(stdscr, x, y, f"{self.author}: ", color_pair=get_sender_name_color_pair(self.author, color_pairs))
        write(stdscr, x+len(self.author)+2, y, f"{message_text_list[0][:width-len(self.author)-2]}")
        for line in message_text_list[1:]:
            y += 1
            write(stdscr, x, y, line[:width])
        
        
        # Render attachments
        for attachment in self.attachments:
            y += 1
            write(stdscr, x, y, f"[Attachment: {attachment.filename}]", color_pair=color_pairs.get("grey_text"))
            
    def _get_message_text_lines(self, width):
        message_lines = [line for line in self.content.split('\n')]
        message_text_list = []
        
        first_shorter_line = True
        for line in message_lines:
            if first_shorter_line and len(line) > width - len(self.author) - 2:
                message_text_list.append(line[:-len(self.author)-2])
                line = line[-len(self.author)-2:]
            while len(line) > width:
                message_text_list.append(line[:width])
                line = line[width:]
            message_text_list.append(line)
            first_shorter_line = False
        
        return message_text_list