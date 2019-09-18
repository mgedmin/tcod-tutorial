import textwrap
from typing import List

import tcod


class Message:

    def __init__(self, text: str, color: tcod.Color = tcod.white) -> None:
        self.text = text
        self.color = color


class MessageLog:

    def __init__(self, x: int, width: int, height: int) -> None:
        self.messages: List[Message] = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self, message: Message) -> None:
        # Split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room for the
            # new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Message object, with the text and the color
            self.messages.append(Message(line, message.color))
