// use rusty_rope::linked_list::List;
use rusty_rope::rope::{Rope, Node};

fn main() {

    // let a = String::from("helloworld!!");
    // let r = Rope::new(&a);
    // // a.push_str("supsupsup");

    // println!("{}", r.to_string());
    // println!("Hello World!");
    // let mut a = List::<i32>::new();
    // a.push(10);
    // a.push(20);
    // a.push(30);
    // println!("A tail is {}", a.tail().expect("").value);
    let a = "helloworld";
    let mut r = Rope::new(a);
    // assert_eq!(r.to_string(), "helloworld");

    r.insert_split(5);
    println!("Successfully split");

    
    if let Node::NonLeaf(root) = r.root_node() {
        if let Some(Node::NonLeaf(child)) = root.left_node() {
            println!("Checking node equals.");
            assert_eq!(child.left_node(), Some(&Node::Leaf("hello")));
            assert_eq!(child.right_node(), Some(&Node::Leaf("world")));
        } else {
            println!("got bad left node.");
            // panic!("got none or leaf for left node: {:?}", root.left_node())
        }
    } else {panic!("got leaf for root node")}
}
