use aoc_runner_derive::aoc;

#[aoc(day2, part1)]
pub fn part1(input: &str) -> usize {
    let mut input = Input(input.as_bytes());
    let mut count = 0;
    loop {
        let mut last = input.read_int();
        let mut inc = true;
        let mut dec = true;
        for _ in 0..3 {
            let num = input.read_int();
            let diff = num - last;
            if inc && !(1..=3).contains(&diff) {
                inc = false;
            }
            if dec && !(-3..=-1).contains(&diff) {
                dec = false;
            }
            last = num;
        }
        for _ in 0..4 {
            let (num, eol, eof) = input.read_int_sep();
            let diff = num - last;
            if inc && !(1..=3).contains(&diff) {
                inc = false;
            }
            if dec && !(-3..=-1).contains(&diff) {
                dec = false;
            }
            if eof {
                if inc || dec {
                    count += 1;
                }
                return count;
            }
            if eol {
                break;
            }
            last = num;
        }
        if inc || dec {
            count += 1;
        }
    }
}

#[aoc(day2, part2)]
pub fn part2(input: &str) -> usize {
    let mut input = Input(input.as_bytes());
    let mut count = 0;
    loop {
        let mut state = TestState::new(input.read_int(), input.read_int());
        state.push(input.read_int());
        state.push(input.read_int());
        for _ in 0..4 {
            let (num, eol, eof) = input.read_int_sep();
            state.push(num);
            if eof {
                if !state.is_known_unsafe() {
                    count += 1;
                }
                return count;
            }
            if eol {
                break;
            }
        }
        if !state.is_known_unsafe() {
            count += 1;
        }
    }
}

struct Input<'a>(&'a [u8]);

const SPACE: isize = b' ' as isize;
const NEWLINE: isize = b'\n' as isize;
const ZERO: isize = b'0' as isize;

impl<'a> Input<'a> {
    fn read_int(&mut self) -> isize {
        unsafe {
            let num = *self.0.get_unchecked(0) as isize - ZERO;
            let next = *self.0.get_unchecked(1) as isize;
            match next {
                SPACE | NEWLINE => {
                    self.0 = &self.0.get_unchecked(2..);
                    num
                }
                _ => {
                    let num = num * 10 + next - ZERO;
                    self.0 = &self.0.get_unchecked(3..);
                    num
                }
            }
        }
    }

    fn read_int_sep(&mut self) -> (isize, bool, bool) {
        unsafe {
            let num = *self.0.get_unchecked(0) as isize - ZERO;
            if self.0.len() == 1 {
                return (num, true, true);
            }
            let next = *self.0.get_unchecked(1) as isize;
            match next {
                SPACE => {
                    self.0 = &self.0.get_unchecked(2..);
                    (num, false, false)
                }
                NEWLINE => {
                    self.0 = &self.0.get_unchecked(2..);
                    (num, true, false)
                }
                _ => {
                    let num = num * 10 + next - ZERO;
                    if self.0.len() == 2 {
                        (num, true, true)
                    } else if *self.0.get_unchecked(2) == b'\n' {
                        self.0 = &self.0.get_unchecked(3..);
                        (num, true, false)
                    } else {
                        self.0 = &self.0.get_unchecked(3..);
                        (num, false, false)
                    }
                }
            }
        }
    }
}

enum State {
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

struct TestState {
    inc: State,
    dec: State,
}

impl TestState {
    fn new(a: isize, b: isize) -> Self {
        let inc = if (1..=3).contains(&(b - a)) {
            State::TwoGood(a, b)
        } else {
            State::TwoBad(a, b)
        };
        let dec = if (-3..=-1).contains(&(b - a)) {
            State::TwoGood(a, b)
        } else {
            State::TwoBad(a, b)
        };
        Self { inc, dec }
    }

    fn is_known_unsafe(&self) -> bool {
        match (&self.inc, &self.dec) {
            (State::Unsafe, State::Unsafe) => true,
            _ => false,
        }
    }

    fn push(&mut self, next: isize) {
        self.inc = match self.inc {
            State::TwoGood(before, last) => {
                if (1..=3).contains(&(next - last)) {
                    State::TwoGood(last, next)
                } else if (1..=3).contains(&(next - before)) {
                    State::TwoBad(last, next)
                } else {
                    State::TwoBad(last, last)
                }
            },
            State::TwoBad(a, b) => {
                if (1..=3).contains(&(next - a)) || (1..=3).contains(&(next - b)) {
                    State::TwoBad(next, next)
                } else {
                    State::Unsafe
                }
            },
            State::Unsafe => State::Unsafe,
        };
        self.dec = match self.dec {
            State::TwoGood(before, last) => {
                if (-3..=-1).contains(&(next - last)) {
                    State::TwoGood(last, next)
                } else if (-3..=-1).contains(&(next - before)) {
                    State::TwoBad(last, next)
                } else {
                    State::TwoBad(last, last)
                }
            },
            State::TwoBad(a, b) => {
                if (-3..=-1).contains(&(next - a)) || (-3..=-1).contains(&(next - b)) {
                    State::TwoBad(next, next)
                } else {
                    State::Unsafe
                }
            },
            State::Unsafe => State::Unsafe,
        };
    }
}
