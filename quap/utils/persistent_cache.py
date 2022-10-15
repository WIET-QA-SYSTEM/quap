from typing import TypeVar, Callable
from functools import wraps
from pathlib import Path
import shelve


_T = TypeVar('_T')


def persistent_cache(name: str, cache_dir: str = '.cache'):
    cache_dir = Path(cache_dir).resolve()

    shelf = shelve.open(cache_dir / name, writeback=True)
    shelf_key = name
    cache = shelf.get(shelf_key, dict())

    def wrapper(func: Callable[..., _T]) -> Callable[..., _T]:
        @wraps(func)
        def inner(*args, **kwargs):
            key = tuple(args) + tuple(kwargs.values())
            if key in cache:
                return cache[key]  # fixme does not work with non-str objects

            result = func(*args, **kwargs)

            cache[key] = result
            shelf[shelf_key] = cache
            shelf.sync()

            return result
        return inner
    return wrapper
