from typing import TypeVar

T = TypeVar("T")


class Vec2d:
    @classmethod
    def from_complex(cls, c: complex) -> "Vec2d":
        return cls(int(c.real), int(c.imag))

    @classmethod
    def from_tuple(cls, t: tuple[int, int]) -> "Vec2d":
        return cls(*t)

    @classmethod
    def from_1d(cls, i: int, width: int) -> "Vec2d":
        return cls(i % width, i // width)

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __add__(self, other: "Vec2d") -> "Vec2d":
        return Vec2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2d") -> "Vec2d":
        return Vec2d(self.x - other.x, self.y - other.y)

    def __mul__(self, other: int) -> "Vec2d":
        return Vec2d(self.x * other, self.y * other)

    def __rmul__(self, other: int) -> "Vec2d":
        return self * other

    def __floordiv__(self, other: int) -> "Vec2d":
        return Vec2d(self.x // other, self.y // other)

    def __neg__(self) -> "Vec2d":
        return Vec2d(-self.x, -self.y)

    def __repr__(self) -> str:
        return f"Vec2d({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vec2d):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def as_complex(self) -> complex:
        return complex(self.x, self.y)

    def as_tuple(self) -> tuple[int, int]:
        return self.x, self.y

    def as_1d(self, width: int) -> int:
        return self.y * width + self.x

    def length(self) -> float:
        return abs(self.as_complex())

    def manhattan(self) -> int:
        return abs(self.x) + abs(self.y)

    def rotate(self, square_angle: int) -> "Vec2d":
        """Rotate by 90 * square_angle degrees."""
        match square_angle % 4:
            case 0:
                return self
            case 1:
                return Vec2d(-self.y, self.x)
            case 2:
                return Vec2d(-self.x, -self.y)
            case 3:
                return Vec2d(self.y, -self.x)
            case _:
                raise ValueError(f"Invalid square_angle: {square_angle}.")

    def index_of(self, field: list[list[T]]) -> T:
        return field[self.y][self.x]

    def set_index(self, field: list[list[T]], value: T) -> None:
        field[self.y][self.x] = value

    def eight_neighbours(self, width: int, height: int) -> list["Vec2d"]:
        return [
            Vec2d(self.x + dx, self.y + dy)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if 0 <= self.x + dx < width and 0 <= self.y + dy < height and (dx or dy)
        ]

    def four_neighbours(self, width: int, height: int) -> list["Vec2d"]:
        return [
            Vec2d(self.x + dx, self.y + dy)
            for dx, dy in ((-1, 0), (0, -1), (1, 0), (0, 1))
            if 0 <= self.x + dx < width and 0 <= self.y + dy < height
        ]


NORTH = Vec2d(0, -1)
EAST = Vec2d(1, 0)
SOUTH = Vec2d(0, 1)
WEST = Vec2d(-1, 0)

LEFT = -1
RIGHT = 1


def motion(raw: str) -> Vec2d:
    return {
        "U": NORTH,
        "D": SOUTH,
        "L": WEST,
        "R": EAST,
        "N": NORTH,
        "E": EAST,
        "S": SOUTH,
        "W": WEST,
        "^": NORTH,
        ">": EAST,
        "v": SOUTH,
        "<": WEST,
    }[raw]
