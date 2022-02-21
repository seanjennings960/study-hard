use std::io;
use std::cmp;
use std::u32;

const DENOMS: [u32; 3] = [1, 3, 4];

fn get_change(m: u32) -> u32 {
    if m > 10000 {
        panic!("Array bigger than max allowed 10000")
    }
    let mut changes: [u32; 10000] = [0; 10000];

    for i in 1..=m {
        let mut best: u32 = u32::MAX;
        for &denom in DENOMS.iter() {
            if i >= denom {
                let ind = (i - denom) as usize;
                best = cmp::min(changes[ind] + 1, best);
                // println!("best: {} | i {} | den {}", best, i, denom);
            }
        }
        changes[i as usize] = best
    }
    // println!("Changes: {:?}", &changes[..m as usize]);
    changes[m as usize]
}


fn main() {
    let mut buffer = String::new();
    io::stdin().read_line(&mut buffer).unwrap();
    let m = buffer.trim().parse::<u32>().unwrap();
    println!("{}", get_change(m));
}
