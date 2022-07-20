use std::io;
use tree_height::{Tree};


fn from_numeric(s: &str) -> Option<usize> {
    if s == "-1" {
        None
    } else {
        Some(s.parse::<usize>().unwrap())
    }
}


fn from_string(s: &str) -> Vec<Option<usize>> {
    let s = s.trim_end();
    s.split(' ').map(from_numeric).collect()
}


fn read_stdin() -> Vec<Option<usize>> {
    let mut buf = String::new();
    io::stdin().read_line(&mut buf).unwrap();
    buf.clear();
    io::stdin().read_line(&mut buf).unwrap();
    from_string(&buf)
}

fn main() {
    let parents = read_stdin();
    let t = Tree::from_parents(&parents, 0);
    println!("{}", t.height());

}
