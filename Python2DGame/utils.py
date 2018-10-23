from typing import Iterable, Tuple

def pairs(elements: Iterable[object]) -> Iterable[Tuple[object, object]]:
    """
    returns the pairs of neighbouring elements in the iterable.
    ```
    pairs([1,2,3]) -> (1,2), (2,3)
    """
    previous = None
    for i, obj in enumerate(elements):
        if i != 0:
            yield previous, obj
        previous = obj