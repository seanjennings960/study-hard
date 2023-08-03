use rusty_rope::rope::{Rope, Node};

fn main() {
    let mut r = Rope::new("helloworld");
    // assert_eq!(r.to_string(), "helloworld");

    r.insert_split(5);
    println!("Successfully split");


    if let Node::NonLeaf(root) = r.root_node() {
        assert_eq!(root.left_node(), Some(&Node::Leaf("hello")));
        if let Some(Node::NonLeaf(child)) = root.right_node() {
            println!("Checking node equals.");
            assert_eq!(child.left_node(), Some(&Node::Leaf("world")));
            assert_eq!(child.right_node(), None);
        } else {
            panic!("got none or leaf for left node: {:?}", root.left_node())
        }
    } else {panic!("got leaf for root node")}
    println!("All good!!")
}
