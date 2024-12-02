use std::{collections::HashMap, hash::{BuildHasher, Hasher}};

use aoc_runner_derive::aoc;

#[aoc(day1, part1)]
pub fn part1(input: &str) -> i32 {
    let mut xs = Vec::with_capacity(1000);
    let mut ys = Vec::with_capacity(1000);
    let bytes = input.as_bytes();
    for i in (0..bytes.len()).step_by(14) {
        xs.push(read_int(bytes, i));
        ys.push(read_int(bytes, i + 8));
    }
    xs.sort_unstable();
    ys.sort_unstable();
    xs.into_iter()
        .zip(ys.into_iter())
        .map(|(a, b)| (a - b).abs())
        .sum()
}

#[aoc(day1, part2)]
pub fn part2(input: &str) -> i32 {
    let mut xs = Vec::with_capacity(1000);
    let mut ys = HashMap::with_capacity_and_hasher(1000, BuildIdHasher);
    let bytes = input.as_bytes();
    for i in (0..bytes.len()).step_by(14) {
        xs.push(read_int(bytes, i));
        let y = read_int(bytes, i + 8);
        ys.entry(y).and_modify(|x| *x += 1).or_insert(1);
    }
    xs.into_iter().map(|x| x * ys.get(&x).unwrap_or(&0)).sum()
}

fn read_int(bytes: &[u8], offset: usize) -> i32 {
    unsafe {
        10000 * *bytes.get_unchecked(offset) as i32
            + 1000 * *bytes.get_unchecked(offset + 1) as i32
            + 100 * *bytes.get_unchecked(offset + 2) as i32
            + 10 * *bytes.get_unchecked(offset + 3) as i32
            + *bytes.get_unchecked(offset + 4) as i32
            - 11111 * b'0' as i32
    }
}

struct BuildIdHasher;

impl BuildHasher for BuildIdHasher {
    type Hasher = IdHasher;

    fn build_hasher(&self) -> Self::Hasher {
        IdHasher(0)
    }
}

struct IdHasher(u64);

impl Hasher for IdHasher {
    fn finish(&self) -> u64 {
        self.0
    }

    fn write(&mut self, _: &[u8]) {
        unimplemented!("we're only going to hash i32s")
    }

    fn write_i32(&mut self, i: i32) {
        self.0 = i as u64;
    }
}
