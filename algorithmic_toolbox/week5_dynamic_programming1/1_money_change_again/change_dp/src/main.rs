use std::io;
use std::cmp;
use std::u32;

const DENOMS: [usize; 3] = [1, 3, 4];

fn get_change(m: u32) -> u32 {
    let m = m as usize;
    if m > 10000 {
        panic!("Array bigger than max allowed 10000")
    }
    let mut changes: [u32; 10000] = [0; 10000];

    for i in 1..=m {
        let mut best: u32 = u32::MAX;
        for &denom in DENOMS.iter() {
            if i >= denom {
                best = cmp::min(changes[i - denom] + 1, best);
                // println!("best: {} | i {} | den {}", best, i, denom);
            }
        }
        changes[i] = best
    }
    // println!("Changes: {:?}", &changes[..m as usize]);
    changes[m]
}


fn main() {
    let mut buffer = String::new();
    io::stdin().read_line(&mut buffer).unwrap();
    let m = buffer.trim().parse::<u32>().unwrap();
    println!("{}", get_change(m));
}
