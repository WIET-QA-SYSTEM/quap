from typing import TypeVar, Callable
from functools import wraps
from pathlib import Path
import shelve
import os


_T = TypeVar('_T')


def persistent_cache(name: str, cache_dir: str = '.cache', skip_self: bool = False):
    os.makedirs(cache_dir, exist_ok=True)
    shelf = shelve.open(os.path.join(cache_dir, name), flag='c', writeback=True)
    shelf_key = name
    print('shelf', list(shelf.keys()), name)
    cache = shelf.get(shelf_key, dict())
    print('after getting shelf by key')

    def wrapper(func: Callable[..., _T]) -> Callable[..., _T]:
        @wraps(func)
        def inner(*args, **kwargs) -> _T:
            cache_key_args = args[1:] if skip_self else args
            key = tuple(cache_key_args) + tuple(kwargs.values())
            print('cache', cache, key, cache.get(key, None))
            if key in cache:
                return cache[key]  # fixme does not work with non-str objects

            result = func(*args, **kwargs)

            cache[key] = result
            shelf[shelf_key] = cache
            shelf.sync()

            return result
        return inner
    return wrapper
