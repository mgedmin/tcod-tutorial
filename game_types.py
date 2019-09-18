from typing import Any, Dict, List, Tuple, cast

import tcod


UserAction = Dict[str, Any]
ActionResult = Dict[str, Any]
ActionResults = List[ActionResult]


def cast_to_color(color: tcod.Color) -> Tuple[int, int, int]:
    return cast(Tuple[int, int, int], color)
