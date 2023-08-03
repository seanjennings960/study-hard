use std::fmt;
use std::ptr::NonNull;
use std::mem;


type NodePtr<'a> = NonNull<Node<'a>>;

#[derive(PartialEq)]
// #[derive(Debug)]
pub enum Node<'a> {
    Leaf(&'a str),
    NonLeaf(NonLeafNode<'a>),
}

impl<'a> Node<'a> {
    pub fn leaf(s: &'a str) -> NodePtr<'a> {
        Node::Leaf(s).alloc()
    }

    pub fn non_leaf(key: usize, left: Option<NodePtr<'a>>, right: Option<NodePtr<'a>>,
            parent: Option<NodePtr<'a>>) -> NodePtr<'a> {
        Node::NonLeaf (
            NonLeafNode {
                key, left, right, parent
            }
        ).alloc()
    }

    pub fn nl_data(key: usize, left: Option<NodePtr<'a>>,
        right: Option<NodePtr<'a>>) -> NodePtr<'a> {
            Node::non_leaf(key, left, right, None)
    }

    fn alloc(self) -> NodePtr<'a> {
        let b = Box::new(self);
        unsafe {NonNull::new_unchecked(Box::into_raw(b))}
    }

    fn drop(ptr: NodePtr<'a>) {
        unsafe {
            let a = ptr.as_ref();
            println!("{:?}", a);
        }
        println!("Ptr: {:#x}", ptr.as_ptr() as usize);
        unsafe {
            // let b = Box::from_raw(ptr.as_ptr());
            drop(Box::from_raw(ptr.as_ptr()))
        }
    }

    pub fn expect_non_leaf(mut ptr: NodePtr<'a>) -> &mut NonLeafNode<'a> {
        let node = unsafe {ptr.as_mut()};
        match node {
            Node::Leaf(_) => panic!("Expected a non leaf node!"),
            Node::NonLeaf(non_leaf) => non_leaf
        }
    }

    pub fn update_parents(n_ptr: NodePtr<'a>, parent: Option<NodePtr<'a>>) -> &'a Node<'a> {
        let node = Node::expect_non_leaf(n_ptr);
        node.parent = parent;
        if let Some(Node::NonLeaf(_)) = node.left_node() {
            Node::update_parents(node.left.expect(""), Some(n_ptr));
        };
        if let Some(Node::NonLeaf(_)) = node.right_node() {
            Node::update_parents(node.right.expect(""), Some(n_ptr));
        };
        Node::from_ptr(n_ptr)
    }

    pub fn from_ptr(n_ptr: NodePtr<'a>) -> &Node<'a> {
        unsafe {n_ptr.as_ref()}
    }

    pub fn root(mut n_ptr: NodePtr<'a>) -> NodePtr<'a> {
        while let Some(p) = Node::expect_non_leaf(n_ptr).parent {
            n_ptr = p;
        }
        n_ptr
    }

}

// impl Eq for Node {


// }

impl<'a> fmt::Debug for Node<'a> {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Node::Leaf(leaf) => {
                fmt.write_str(&format!("{}", leaf))?;
            }
            Node::NonLeaf(node) => {
                let mut left_node_s = format!("{:?}", node.left_node());
                left_node_s = left_node_s.lines(
                    ).collect::<Vec<&str>>().join("\n\t");
                let mut right_node_s = format!("{:?}", node.right_node());
                right_node_s = right_node_s.lines(
                    ).collect::<Vec<&str>>().join("\n\t");
                let s = format!(
                    "
Node ({:#x})
\tkey: {}
\tparent:{:?}
\tLeft: {}
\tRight: {}",
                    self as *const Node as usize,
                    node.key,
                    node.parent,
                    // "", ""
                    left_node_s,
                    right_node_s,
                );
                // let mut s: String = match &node.left {
                //     None => "".to_string(),
                //     Some(n) => n.borrow().to_string()
                // };
                // if let Some(n) = &node.right {
                //     let right_str = n.borrow().to_string();
                //     s.push_str(&right_str);
                // };
                fmt.write_str(&s)?;
            }
        };
        Ok(())
    }
}

fn insert_split(mut ptr: NodePtr, x: usize) -> NodePtr {
    let node = unsafe {ptr.as_mut()};
    match node {
        Node::Leaf(_) => {
            panic!("Called insert split on leaf node!");
        },
        Node::NonLeaf(non_leaf) => {
            if non_leaf.key == x {
                splay(ptr);
                ptr
            } else {
                let (
                    diff, setting_left,
                    target_child
                ) = if x < non_leaf.key  {
                    (x, true, non_leaf.left_node().expect("Found no left node!!"))
                } else {
                    (x - non_leaf.key, false, non_leaf.right_node().expect(
                        &format!("Found no right node!\nx: {}\n{:?}", x, Node::from_ptr(ptr))))
                };
                match target_child {
                    Node::Leaf(leaf_str) => {
                        // Create new nodes in place of the old.
                        let left = Node::leaf(&leaf_str[..diff]);
                        let right = Node::leaf(&leaf_str[diff..]);
                        let new_node = Node::non_leaf(
                            diff, Some(left), Some(right), Some(ptr)
                        );


                        let node_to_replace;
                        if setting_left {
                            node_to_replace = &mut non_leaf.left;
                        } else {
                            node_to_replace = &mut non_leaf.right;
                        }
                        let old_ptr = mem::replace(
                            node_to_replace, Some(new_node));

                        Node::drop(old_ptr.expect(
                            "Already checked left is some"));
                        splay(new_node);
                        new_node
                    },
                    Node::NonLeaf(_) => {
                        // SAFETY: Since target_child is Some, target_ptr must also be.
                        let target_ptr = if setting_left {
                            non_leaf.left
                        } else {non_leaf.right};
                        print!("Entering recursive split with x: {}\n", diff);
                        insert_split(
                            target_ptr.expect("Definitely some."),
                            diff)
                    },
                }
            }
        }
    }
}

fn set_left<'a>(parent: NodePtr<'a>, left: Option<NodePtr<'a>>) {
    let p = Node::expect_non_leaf(parent);
    let l = left.map(|mut l| {
        unsafe {l.as_mut()}
    });
    // (**parent)
    p.left = left;
    if let Some(Node::NonLeaf(non_leaf_left)) = l {
        non_leaf_left.parent = Some(parent);
    }
}

fn set_right<'a>(parent: NodePtr<'a>, right: Option<NodePtr<'a>>) {
    let p = Node::expect_non_leaf(parent);
    let l = right.map(|mut r| {
        unsafe {r.as_mut()}
    });
    // (**parent)
    p.right = right;
    if let Some(Node::NonLeaf(non_leaf_right)) = l {
        non_leaf_right.parent = Some(parent);
    }
}

fn swap_parents<'a>(old_child: NodePtr<'a>, new_child: NodePtr<'a>) {
    let p_ptr = Node::expect_non_leaf(old_child).parent;
    let p = p_ptr.map(
            |p| {
                Node::expect_non_leaf(p)
        });
    Node::expect_non_leaf(new_child).parent = p_ptr;
    println!("Parent before swap: {:?}", p_ptr.map(|p| Node::from_ptr(p)));
    if let Some(p) = p {
        if p.left == Some(old_child) {
            println!("Setting p left");
            p.left = Some(new_child);
            println!("Parent after swap: {:?}", p_ptr.map(|p| Node::from_ptr(p)));
        } else if p.right == Some(old_child) {
            println!("Setting p right");
            p.right = Some(new_child);
            println!("Parent after swap: {:?}", p_ptr.map(|p| Node::from_ptr(p)));
        } else {panic!("Parent/child relationship broken!")}
    }
}


#[allow(dead_code)]
fn zig<'a>(n_ptr: NodePtr<'a>) {
    let n = Node::expect_non_leaf(n_ptr);
    // Nothing to do if we are already root.
    if n.parent.is_none() { return };

    let p_ptr = n.parent.expect("Unreachable");
    let p = Node::expect_non_leaf(p_ptr);
    assert!(p.parent.is_none(), "Can't zig with grandparent");

    if p.left == Some(n_ptr) {
        println!("Zigging left");
        // We zig left.
        let c = n.right;
        set_left(p_ptr, c);
        set_right(n_ptr, Some(p_ptr));
        p.key -= n.key;
        n.parent = None;
    } else if p.right == Some(n_ptr) {
        println!("Zigging right");
        // We zig right
        let c_ptr = n.left;
        set_right(p_ptr, c_ptr);
        set_left(n_ptr, Some(p_ptr));
        n.key += p.key;
        n.parent = None;
    } else {panic!("Child/parent relation broken")}
}

#[allow(dead_code)]
fn zig_zig<'a>(n_ptr: NodePtr<'a>) {
    // TODO: clean this up so we don't have to go around messing around with
    // both pointers and nonleaf nodes...
    let n = Node::expect_non_leaf(n_ptr);
    let p_ptr = n.parent.expect("Ran zig_zig on root!");
    let p = Node::expect_non_leaf(p_ptr);
    let gp_ptr = p.parent.expect("Must have GP to zig_zig!");
    let gp = Node::expect_non_leaf(gp_ptr);

    if Some(n_ptr) == p.left {
        assert!(Some(p_ptr) == gp.left, "Bad zig-zig case.");
        let d = n.right;
        let e = p.right;
        swap_parents(gp_ptr, n_ptr);
        set_right(n_ptr, Some(p_ptr));
        set_right(p_ptr, Some(gp_ptr));
        set_left(p_ptr, d);
        set_left(gp_ptr, e);
        gp.key -= p.key;
        p.key -= n.key;
    } else if Some(n_ptr) == p.right {
        assert!(Some(p_ptr) == gp.right, "Bad zig-zig case");
        let d = n.left;
        let e = p.left;
        swap_parents(gp_ptr, n_ptr);
        set_left(n_ptr, Some(p_ptr));
        set_left(p_ptr, Some(gp_ptr));
        set_right(p_ptr, d);
        set_right(gp_ptr, e);
        p.key += gp.key;
        n.key += p.key;
    } else {panic!("Parent/child relation broken")}
}

#[allow(dead_code)]
fn zig_zag<'a>(n_ptr: NodePtr<'a>) {
    // TODO: clean this up so we don't have to go around messing around with
    // both pointers and nonleaf nodes...
    let n = Node::expect_non_leaf(n_ptr);
    let p_ptr = n.parent.expect("Ran zig_zig on root!");
    let p = Node::expect_non_leaf(p_ptr);
    let gp_ptr = p.parent.expect("Must have GP to zig_zig!");
    let gp = Node::expect_non_leaf(gp_ptr);

    let left = n.left;
    let right = n.right;
    if Some(n_ptr) == p.right {
        assert!(Some(p_ptr) == gp.left, "Bad zig-zag case!");
        swap_parents(gp_ptr, n_ptr);
        set_left(n_ptr, Some(p_ptr));
        set_right(n_ptr, Some(gp_ptr));
        set_right(p_ptr, left);
        set_left(gp_ptr, right);
        n.key += p.key;
        gp.key -= n.key;
    } else if Some(n_ptr) == p.left {
        assert!(Some(p_ptr) == gp.right, "Bad zig-zag case!");
        swap_parents(gp_ptr, n_ptr);
        set_left(n_ptr, Some(gp_ptr));
        set_right(n_ptr, Some(p_ptr));
        set_left(p_ptr, right);
        set_right(gp_ptr, left);
        p.key -= n.key;
        n.key += gp.key;
    } else {panic!("Parent child relation broken!")}
}

#[derive(Debug)]
enum SplayOperation {
    Zig, ZigZag, ZigZig
}

fn choose_zig<'a>(n_ptr: NodePtr<'a>) -> SplayOperation {
    let n = Node::expect_non_leaf(n_ptr);
    let p_ptr = n.parent.expect("n must have parent!");
    let p = Node::expect_non_leaf(p_ptr);
    let maybe_gp_ptr = p.parent;
    println!("n_ptr: {:?}\np_ptr{:?}\ngp_ptr{:?}", n_ptr, p_ptr, maybe_gp_ptr);

    match maybe_gp_ptr {
        None => SplayOperation::Zig,
        Some(gp_ptr) => {
            let gp = Node::expect_non_leaf(gp_ptr);
            if Some(p_ptr) == gp.left && Some(n_ptr) == p.left {
                SplayOperation::ZigZig
            } else if Some(p_ptr) == gp.right && Some(n_ptr) == p.left {
                SplayOperation::ZigZag
            } else if Some(p_ptr) == gp.left && Some(n_ptr) == p.right {
                SplayOperation::ZigZag
            } else if Some(p_ptr) == gp.right && Some(n_ptr) == p.right {
                SplayOperation::ZigZig
            } else { panic!("Parent/child relations broken!") }
        }
    }
}

fn splay<'a>(n_ptr: NodePtr<'a>) {
    // let node = Node::from_ptr(n_ptr);
    // println!("Beginning splay at Node:\n{:?}", node);
    if Node::expect_non_leaf(n_ptr).parent.is_none() {
        // Our work here is done.
        return
    }
    println!("Beginning splay at Node:{:#x}", n_ptr.as_ptr() as usize);
    println!("Node:\n{:?}", Node::from_ptr(Node::root(n_ptr)));
    // println!("parent node is:{:?}", Node::expect_non_leaf(n_ptr).parent);
    let op = choose_zig(n_ptr);
    println!("Running op: {:?}", op);
    match op {
        SplayOperation::Zig => zig(n_ptr),
        SplayOperation::ZigZig => zig_zig(n_ptr),
        SplayOperation::ZigZag => zig_zag(n_ptr),
    }
    println!("Completed splay:\n{:?}", Node::from_ptr(Node::root(n_ptr)));
    // println!("Completed splay op now with Node:\n{:?}", node);
    // Continue to splay until n is root!
    splay(n_ptr)
}


#[allow(dead_code)]
#[derive(Debug)]
pub struct NonLeafNode<'a> {
    parent: Option<NodePtr<'a>>,
    pub left: Option<NodePtr<'a>>,
    pub right: Option<NodePtr<'a>>,
    key: usize,
}



impl<'a> NonLeafNode<'a> {
    pub fn right_node(&self, ) -> Option<&Node<'a>>{
        self.right.map(|ptr| {
            unsafe {ptr.as_ref()}
        })
    }

    pub fn left_node(&self, ) -> Option<&Node<'a>>{
        self.left.map(|ptr| {
            unsafe {ptr.as_ref()}
        })
    }
}

impl<'a> PartialEq for NonLeafNode<'a> {
    fn eq(&self, other: &Self) -> bool {
        if self.key != other.key { return false }
        if !(self.left_node() == other.left_node()) { return false }
        return self.right_node() == other.right_node()


        // let left_equal = match self.left_node() {
        //     None => other_left.is_none(),
        //     Some(Node::Leaf(s)) => {
        //         if let Some(Node::Leaf(s_other)) = other_left {
        //             s == s_other
        //         } else { false }
        //     },
        //     Some(Node::NonLeaf(non_leaf)) => {
        //         if let Some(Node::NonLeaf(non_leaf_other)) = other_left {
        //             non_leaf_other ==
        //         }
        //     }
        // }
    }
}


pub struct Rope<'a> {
    root: NodePtr<'a>,
}

// struct TreeIter<'a>(Option<Node<'a>>);

// impl<'a> Iterator for TreeIter<'a> {
//     type Item = &'a str;

//     fn next(&mut self) -> Option<Self::Item> {
//         self.0.take().map(|node| {

//         })
//     }
// }


impl<'a> Rope<'a> {
    pub fn new(s: &'a str) -> Rope<'a> {
        let leaf = Node::leaf(&s[..]);
        let root = Node::non_leaf(
            s.len(), Some(leaf), None, None);
        Rope {
            root: root,
        }
    }

    pub fn insert_split(&mut self, x: usize) -> NodePtr<'a> {
        let new_root = insert_split(self.root, x);
        self.root = new_root;
        self.root
    }

    pub fn root_node(&self) -> &Node<'a> {
        unsafe {self.root.as_ref()}
    }

    pub fn splay(&mut self, n_ptr: NodePtr<'a>) {
        splay(n_ptr);
        self.root = n_ptr;
    }

}


// TODO: drop nodes
// impl<'a> Drop for Rope<'a> {

// }
impl<'a> fmt::Debug for Rope<'a> {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        fmt.write_str(&format!("{:?}", self.root_node()))
    }
}

#[cfg(test)]
mod tests {
    use crate::rope::Rope;
    use crate::rope::Node;

    #[test]
    fn test_splay() {
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

        let n = r.insert_split(8);
        let exp = Node::update_parents(
            Node::nl_data(
                8,
                Some(Node::nl_data(
                    6,
                    Some(Node::nl_data(
                        5,
                        Some(Node::leaf("hello")),
                        Some(Node::leaf("w")),
                    )),
                    Some(Node::nl_data(
                        1,
                        Some(Node::leaf("o")),
                        Some(Node::leaf("r")),
                    ))
                )),
                Some(Node::nl_data(
                    2,
                    Some(Node::leaf("ld")),
                    None,
                ))
            ), None);
        assert_eq!(Node::from_ptr(n), exp);









    }
}
