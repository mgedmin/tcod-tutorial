from typing import Any, Optional

from game_messages import Message
from game_types import ItemFunction


class Item:

    def __init__(
        self, use_function: Optional[ItemFunction] = None,
        targeting: bool = False, targeting_message: Optional[Message] = None,
        **kwargs: Any
    ) -> None:
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.function_kwargs = kwargs
