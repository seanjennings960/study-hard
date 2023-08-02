use rusty_rope::linked_list::List;

fn main() {

    println!("Hello World!");
    let mut a = List::<i32>::new();
    a.push(10);
    a.push(20);
    a.push(30);
    println!("A tail is {}", a.tail().expect("").value);
}
