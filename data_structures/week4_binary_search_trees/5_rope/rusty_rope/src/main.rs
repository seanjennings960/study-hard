// use rusty_rope::linked_list::List;
use rusty_rope::rope::{Rope, Node};


fn test_rope() {
    let a = "helloworld";
    let mut r = Rope::new(a);

    // Zig left -> right
    let n = r.insert_split(5);
    let exp = Node::update_parents(
        Node::nl_data(
            5,
            Some(Node::leaf("hello")),
            Some(Node::nl_data(
                5,
                Some(Node::leaf("world")),
                None)),
        ), None);
    assert_eq!(Node::from_ptr(n), exp);

    let n = r.insert_split(7);
    let exp = Node::update_parents(
        Node::nl_data(
            7,
            Some(Node::nl_data(
                5,
                Some(Node::leaf("hello")),
                Some(Node::leaf("wo")),
            )),
            Some(Node::nl_data(
                3,
                Some(Node::leaf("rld")),
                None)),
        ), None);
    assert_eq!(Node::from_ptr(n), exp);

    let n = Node::expect_non_leaf(n).right.expect(
        "Missing right node");
    r.splay(n);
    // Zig right -> left
    let pre_zig_zig = Node::update_parents(
        Node::nl_data(
            10,
            Some(Node::nl_data(
                7,
                Some(Node::nl_data(
                    5,
                    Some(Node::leaf("hello")),
                    Some(Node::leaf("wo"))
                )),
                Some(Node::leaf("rld")),
            )),
            None,
        ), None);

    assert_eq!(Node::from_ptr(n), pre_zig_zig);
    let n = Node::expect_non_leaf(n
        ).left.expect("missing left");
    let n = Node::expect_non_leaf(n
        ).left.expect("missing left");
    r.splay(n);

    let exp = Node::update_parents(
        Node::nl_data(
            5,
            Some(Node::leaf("hello")),
            Some(Node::nl_data(
                2,
                Some(Node::leaf("wo")),
                Some(Node::nl_data(
                    3,
                    Some(Node::leaf("rld")),
                    None
                ))
            )),
        ), None);
    assert_eq!(Node::from_ptr(n), exp);

    let n = Node::expect_non_leaf(n
        ).right.expect("missing right");
    let n = Node::expect_non_leaf(n
        ).right.expect("missing right");
    r.splay(n);
    assert_eq!(Node::from_ptr(n), pre_zig_zig);

    let n = r.insert_split(6);
    let exp = Node::update_parents(
        Node::nl_data(
            6,
            Some(Node::nl_data(
                5,
                Some(Node::leaf("hello")),
                Some(Node::leaf("w"))
            )),
            Some(Node::nl_data(
                4,
                Some(Node::nl_data(
                    1,
                    Some(Node::leaf("o")),
                    Some(Node::leaf("rld")),
                )),
                None,
            ))
        ), None);
    assert_eq!(Node::from_ptr(n), exp);

}
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
    // let a = "helloworld";
    // let mut r = Rope::new(a);
    // // assert_eq!(r.to_string(), "helloworld");

    // r.insert_split(5);
    // println!("Successfully split");


    // if let Node::NonLeaf(root) = r.root_node() {
    //     if let Some(Node::NonLeaf(child)) = root.left_node() {
    //         println!("Checking node equals.");
    //         assert_eq!(child.left_node(), Some(&Node::Leaf("hello")));
    //         assert_eq!(child.right_node(), Some(&Node::Leaf("world")));
    //     } else {
    //         println!("got bad left node.");
    //         // panic!("got none or leaf for left node: {:?}", root.left_node())
    //     }
    // } else {panic!("got leaf for root node")}
    test_rope()
}
