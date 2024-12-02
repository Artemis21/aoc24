use std::ops::RangeInclusive;

use aoc_runner_derive::aoc;

#[aoc(day2, part1)]
pub fn part1(input: &str) -> usize {
    let mut input = Input(input.as_bytes());
    let mut count = 0;
    loop {
        let mut state = CheckUndamped::new(input.read_int());
        state.push(input.read_int());
        state.push(input.read_int());
        state.push(input.read_int());
        for _ in 0..4 {
            let (num, eol, eof) = input.read_int_sep();
            state.push(num);
            if eof {
                return count + (state.safe() as usize);
            }
            if eol {
                break;
            }
        }
        count += state.safe() as usize;
    }
}

#[aoc(day2, part2)]
pub fn part2(input: &str) -> usize {
    let mut input = Input(input.as_bytes());
    let mut count = 0;
    loop {
        let mut state = CheckDamped::new(input.read_int(), input.read_int());
        state.push(input.read_int());
        state.push(input.read_int());
        for _ in 0..4 {
            let (num, eol, eof) = input.read_int_sep();
            state.push(num);
            if eof {
                return count + (state.safe() as usize);
            }
            if eol {
                break;
            }
        }
        count += state.safe() as usize;
    }
}

struct Input<'a>(&'a [u8]);

const NEWLINE: isize = b'\n' as isize;
const ZERO: isize = b'0' as isize;

impl<'a> Input<'a> {
    fn read_int(&mut self) -> isize {
        unsafe {
            let d1 = *self.0.get_unchecked(0) as isize - ZERO;
            let d2 = *self.0.get_unchecked(1) as isize - ZERO;
            if d2 >= 0 {
                self.0 = &self.0.get_unchecked(3..);
                d1 * 10 + d2
            } else {
                self.0 = &self.0.get_unchecked(2..);
                d1
            }
        }
    }

    fn read_int_sep(&mut self) -> (isize, bool, bool) {
        unsafe {
            let d1 = *self.0.get_unchecked(0) as isize - ZERO;
            if self.0.len() == 1 {
                return (d1, true, true);
            }
            let d2 = *self.0.get_unchecked(1) as isize - ZERO;
            if d2 >= 0 {
                let num = d1 * 10 + d2;
                if self.0.len() == 2 {
                    self.0 = &self.0.get_unchecked(2..);
                    (num, true, true)
                } else {
                    let next = *self.0.get_unchecked(2);
                    self.0 = &self.0.get_unchecked(3..);
                    (num, next == b'\n', false)
                }
            } else {
                self.0 = &self.0.get_unchecked(2..);
                (d1, d2 == NEWLINE - ZERO, false)
            }
        }
    }
}

struct CheckUndamped {
    inc: bool,
    dec: bool,
    last: isize,
}

impl CheckUndamped {
    fn new(first: isize) -> Self {
        Self {
            inc: true,
            dec: true,
            last: first,
        }
    }

    fn safe(&self) -> bool {
        self.inc || self.dec
    }

    fn push(&mut self, next: isize) {
        let diff = next - self.last;
        if self.inc && !(1..=3).contains(&diff) {
            self.inc = false;
        }
        if self.dec && !(-3..=-1).contains(&diff) {
            self.dec = false;
        }
        self.last = next;
    }
}

struct CheckDamped {
    inc: DampingState<1, 3>,
    dec: DampingState<-3, -1>,
}

impl CheckDamped {
    fn new(a: isize, b: isize) -> Self {
        Self {
            inc: DampingState::new(a, b),
            dec: DampingState::new(a, b),
        }
    }

    fn safe(&self) -> bool {
        self.inc.safe() || self.dec.safe()
    }

    fn push(&mut self, next: isize) {
        self.inc.push(next);
        self.dec.push(next);
    }
}

#[derive(Clone, Copy)]
enum DampingState<const MIN: isize, const MAX: isize> {
    /// Everything we've seen so far is safe. Of (before, last) a future number
    /// can follow either, but following 'before' means dropping 'last'.
    TwoGood(isize, isize),
    /// We've been forced to drop a number, but we don't know which of (a, b)
    /// to drop. The other one is what future numbers must follow from.
    ///
    /// Also encodes the state where we've made our decision (a == b).
    TwoBad(isize, isize),
    /// Even after a drop, the sequence was unsafe.
    Unsafe,
}

impl<const MIN: isize, const MAX: isize> DampingState<MIN, MAX> {
    const RANGE: RangeInclusive<isize> = MIN..=MAX;

    fn new(fst: isize, snd: isize) -> Self {
        if Self::RANGE.contains(&(snd - fst)) {
            Self::TwoGood(fst, snd)
        } else {
            Self::TwoBad(fst, snd)
        }
    }

    fn push(&mut self, next: isize) {
        *self = match *self {
            Self::TwoGood(before, last) => {
                if Self::RANGE.contains(&(next - last)) {
                    Self::TwoGood(last, next)
                } else if Self::RANGE.contains(&(next - before)) {
                    Self::TwoBad(last, next)
                } else {
                    Self::TwoBad(last, last)
                }
            }
            Self::TwoBad(a, b) => {
                if Self::RANGE.contains(&(next - a)) || Self::RANGE.contains(&(next - b)) {
                    Self::TwoBad(next, next)
                } else {
                    Self::Unsafe
                }
            }
            Self::Unsafe => Self::Unsafe,
        };
    }

    fn safe(&self) -> bool {
        match *self {
            Self::Unsafe => false,
            _ => true,
        }
    }
}
