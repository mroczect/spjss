import queue
import threading
from collections.abc import Callable
from typing import Any

_stop = threading.Event()


def reset_stop() -> None:
    _stop.clear()


def request_stop() -> None:
    _stop.set()


def should_stop() -> bool:
    return _stop.is_set()


def run(
    fn: Callable[..., Any], out: "queue.Queue", *args, **kwargs
) -> threading.Thread:
    def body() -> None:
        try:
            out.put(("ok", fn(*args, **kwargs)))
        except BaseException as e:
            out.put(("err", e))

    t = threading.Thread(target=body, daemon=True)
    t.start()
    return t
