import re
import math
import cmath
from collections import deque, defaultdict, Counter
from functools import cache, reduce, partial
from itertools import (
    combinations, permutations, product, count, cycle,
    islice, chain, takewhile, dropwhile, accumulate, groupby,
)

import advent_of_code_ocr
import parse

from util import (
    get_input, submit,
    paras, indents, lines, words, chars, split,
    sentence, switch, tags, field,
    const, pair, triple, ints, turn, motion,
    Vec2d,
)

r = get_input(25)



part = 1

submit(25, part, x)
