use std::fmt;
use std::ptr::NonNull;
use std::mem;


type NodePtr<'a> = NonNull<Node<'a>>;

#[derive(PartialEq)]
#[derive(Debug)]
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

    fn alloc(self) -> NodePtr<'a> {
        let b = Box::new(self);
        unsafe {NonNull::new_unchecked(Box::into_raw(b))}
    }

    fn drop(ptr: NodePtr<'a>) {
        unsafe {
            let a = ptr.as_ref();
            println!("{}", a);
        }
        println!("Ptr: {:#x}", ptr.as_ptr() as usize);
        unsafe {
            // let b = Box::from_raw(ptr.as_ptr());
            drop(Box::from_raw(ptr.as_ptr()))
        }
    }
}

// impl Eq for Node {


// }

impl<'a> fmt::Display for Node<'a> {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Node::Leaf(leaf) => {
                fmt.write_str(&format!("{}", leaf))?;
            }
            Node::NonLeaf(node) => {
                let s = format!(
                    "Node ({})\n\tLeft: {:?}\n\tRight: {:?}",
                    node.key,
                    node.left_node().map(|left| left.to_string()),
                    node.right_node().map(|right| right.to_string()),
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

fn insert_split(mut ptr: NodePtr, x: usize) -> Option<NodePtr> {
    let node = unsafe {ptr.as_mut()};
    match node {
        Node::Leaf(_) => {
            panic!("Called insert split on leaf node!");
        },
        Node::NonLeaf(non_leaf) => {
            if non_leaf.key == x {
                Some(ptr)
            } else {
                let (
                    diff, setting_left,
                    target_child
                ) = if x < non_leaf.key  {
                    (x, true, non_leaf.left_node().expect("Found no left node!!"))
                } else {
                    (non_leaf.key - x, false, non_leaf.right_node().expect(
                        "Found no right node!"))
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
                        Some(new_node)
                    },
                    Node::NonLeaf(_) => {
                        // SAFETY: Since target_child is Some, target_ptr must also be.
                        let target_ptr = if setting_left {
                            non_leaf.left
                        } else {non_leaf.right};
                        insert_split(
                            target_ptr.expect("Definitely some."),
                            diff)
                    },
                }
            }
        }
    }
}
#[allow(dead_code)]
#[derive(PartialEq)]
#[derive(Debug)]
pub struct NonLeafNode<'a> {
    parent: Option<NodePtr<'a>>,
    left: Option<NodePtr<'a>>,
    right: Option<NodePtr<'a>>,
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

    // pub fn set_left(&mut self, n:  NodePtr<'a>) {
    //     self.left = Some(n)
    // }

    // pub fn set_right(&mut self, n:  NodePtr<'a>) {
    //     self.right = Some(n)
    // }


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

    pub fn insert_split(&mut self, x: usize) {
        insert_split(self.root, x);
    }

    pub fn root_node(&self) -> &Node<'a> {
        unsafe {self.root.as_ref()}
    }

    // fn root_node_mut(&mut self) -> &mut Node<'a> {
    //     unsafe {self.root.as_mut()}
    // }

    // fn iter(&self) -> Iterator<'a> {

    // }

    // pub fn insert_split(n: NodePtr<'a>, x: usize
    //         ) -> Result<NodePtr<'a>, String> {
    //     let a = *n.borrow();

        // match *a {
        //     Node::NonLeaf(non_leaf) => {
        //         if x == non_leaf.key {
        //             return Ok(n.clone())
        //         }
        //         let new_index = if x > non_leaf.key {
        //             x - non_leaf.key
        //         } else {x};
        //         let target_child = if x > non_leaf.key {
        //             non_leaf.right
        //         } else {non_leaf.left};

        //         match target_child {
        //             None => Err(format!("Index {} out of range!", x)),
        //             Some(child) => {
        //                 match *child.borrow_mut() {  
        //                     Node::NonLeaf(right_non_leaf) => Rope::insert_split(
        //                         child, new_index),
        //                     Node::Leaf(s_right) => {
        //                         let n_new = Node::non_leaf(new_index);
        //                         let n_mut = n_new.borrow_mut();
        //                         n_mut.set_left(Node::leaf(&s_right[..new_index]));
        //                         n_mut.set_right(Node::leaf(&s_right[new_index..]));
        //                         n.borrow_mut().set_right(n_new);
        //                         Ok(n_new)

        //                     }
        //                 }
        //             }
        //         }
        //     },
        //     Node::Leaf(_) => Err(String::from("Can only split at non-leaf nodes"))
        // }
    // }
}


// TODO: drop nodes
// impl<'a> Drop for Rope<'a> {

// }
impl<'a> fmt::Display for Rope<'a> {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        fmt.write_str(&self.root_node().to_string())
    }
}

#[cfg(test)]
mod tests {
    use crate::rope::Rope;
    use crate::rope::Node;

    #[test]
    fn test_rope() {
        let a = "helloworld";
        let mut r = Rope::new(a);
        // assert_eq!(r.to_string(), "helloworld");

        r.insert_split(5);

        
        if let Node::NonLeaf(root) = r.root_node() {
            if let Some(Node::NonLeaf(child)) = root.left_node() {
                assert_eq!(child.left_node(), Some(&Node::Leaf("hello")));
                assert_eq!(child.right_node(), Some(&Node::Leaf("world")));
            } else {panic!("got none or leaf for left node: {:?}", root.left_node())}
        } else {panic!("got leaf for root node")}



    }
}
