from typing import Any, Callable

from game_messages import Message


class Item:

    def __init__(self, use_function: Callable = None, targeting: bool = False,
                 targeting_message: Message = None, **kwargs: Any) -> None:
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.function_kwargs = kwargs
