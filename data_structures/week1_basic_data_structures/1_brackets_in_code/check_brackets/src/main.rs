use std::io;


#[derive(Debug)]
struct Bracket {
    char_: char,
    position: usize,
}



fn find_mismatch(in_: String) -> Option<usize> {
    let mut stack = Vec::new();

    for (i, x) in in_.chars().enumerate() {
        if "{[(".contains(x) {
            stack.push(
                Bracket { char_: x, position: i }
            );
        }

        if "}])".contains(x) {
            if stack.is_empty() {
                return Some(i)
            }
            let top = stack.pop().unwrap().char_;
            if (top == '(' && x != ')') ||
               (top == '{' && x != '}') ||
               (top == '[' && x != ']') {
                return Some(i)
            }
        }
    }
    if stack.is_empty() {
        return None
    }
    return Some(stack[0].position)
}


fn main() -> io::Result<()> {
    let mut buffer = String::new();
    io::stdin().read_line(&mut buffer)?;
    let output = find_mismatch(buffer);

    match output {
        Some(pos) => println!("{}", pos + 1),
        None => println!("Success")
    }
    Ok(())
}
