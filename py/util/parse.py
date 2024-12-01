import parse

import re
from typing import Callable, TypeVar, Any


T = TypeVar("T")
Parser = Callable[[str], T]

def paras(inner: Parser[T]) -> Parser[list[T]]:
    return lambda raw: list(map(inner, raw.split("\n\n")))


def indents(inner: Parser[T]) -> Parser[list[T]]:
    """Parses indented blocks, like this:
    
    ```
    this is all
      part of the
      first block
    but this is
      all part of
      the second
    ```

    Which becomes:

    ```
    [
        "this is all\n  part of the\n  first block",
        "but this is\n  all part of\n  the second",
    ]
    ```
    """
    def parse(raw: str) -> list[T]:
        buffer = ""
        indent: int | None = None
        blocks: list[T] = []
        for line in raw.splitlines(keepends=True):
            if not blocks:  # first line of input
                buffer = line
            elif indent is None:  # second line of block
                indent = next((i for i, c in enumerate(line) if c != " "))
            elif line[:indent].isspace():  # further lines of block
                buffer += line
            else:  # new block
                blocks.append(inner(buffer.rstrip()))
                buffer = line
                indent = None
        blocks.append(inner(buffer.rstrip()))
        return blocks
    return parse


def lines(inner: Parser[T]) -> Parser[list[T]]:
    return lambda raw: list(map(inner, raw.splitlines()))


def words(inner: Parser[T]) -> Parser[list[T]]:
    return lambda raw: list(map(inner, raw.split()))


def chars(inner: Parser[T]) -> Parser[list[T]]:
    return lambda raw: list(map(inner, raw))


def split(sep: str, inner: Parser[T]) -> Parser[list[T]]:
    return lambda raw: list(map(inner, raw.split(sep)))


def sentence(format: str) -> Parser[Any]:
    """Parse using the `parse` module.

    This uses a specification like a format string.

    For example, `sentence("The {item} scores {points:d}")` will parse
    `"The apple scores 5"` into `{"item": "apple", "points": 5}`.
    """
    parser = parse.compile(format)
    return lambda raw: parser.parse(raw)


def switch(cases: dict[str, tuple[str, Parser[T]]]) -> Parser[tuple[str, T]]:
    """Select a parser based on which regex matches.

    For example, `switch({"F(.+)": ("f", int), "T(.)": ("t", turn)})` will parse
    `"F12"` into `("f", 12)` and `"TR"` into `("t", 1)` (right turn is 1).
    """
    def parse(raw: str) -> tuple[str, T]:
        for pattern, (tag, parser) in cases.items():
            match = re.match(pattern, raw)
            if match is not None:
                try:
                    capture = match.group(1)
                except IndexError:
                    capture = match.group(0)
                return (tag, parser(capture))
        raise ValueError(f"Failed to parse '{raw}'.")
    return parse


def tags(tags: dict[str, T]) -> Parser[T]:
    """Parse a tag from a dictionary.

    For example, `tags({"#": 1, ".": 0})` will parse `"#"` into `1` and `"."` into `0`.
    """
    def parse(raw: str) -> T:
        try:
            return tags[raw]
        except KeyError:
            raise ValueError(f"Failed to parse '{raw}'.")
    return parse


def field(tile: Parser[T]) -> Parser[list[list[T]]]:
    """Parse a map of characters into a 2D array of values.

    For example, `map(tags({".": 0, "#": 1, "?": 2}))` will parse this:

    ```txt
    #..
    .?.
    ..#
    ```

    Into this:

    ```
    [ [1, 0, 0],
      [0, 2, 0],
      [0, 0, 1] ]
    ```
    """
    return lines(chars(tile))


def const(value: T) -> Parser[T]:
    return lambda _: value


def pair(inner: Parser[T], sep: str = ",") -> Parser[tuple[T, T]]:
    def parse(raw: str) -> tuple[T, T]:
        a, b = raw.split(sep)
        return inner(a), inner(b)
    return parse


def triple(inner: Parser[T], sep: str = ",") -> Parser[tuple[T, T, T]]:
    def parse(raw: str) -> tuple[T, T, T]:
        a, b, c = raw.split(sep)
        return inner(a), inner(b), inner(c)
    return parse


def ints(raw: str) -> list[int]:
    return list(map(int, re.findall(r"-?\d+", raw)))


def turn(raw: str) -> int:
    return {"L": -1, "R": 1}[raw]
