use std::io;
use std::rc::Rc;
use std::cell::{RefCell};
use std::collections::VecDeque;


struct Node<'a> {
    value: i32,
    children: Vec<&'a Node<'a>>
}

impl<'a> Node<'a> {
    pub fn new(value: i32) -> Self {
        let children = Vec::new();
        Self { value, children }
    }

    pub fn add_child(&mut self, c: &'a Node) {
        self.children.push(c);
    }

    pub fn height(&self) -> u32 {
        let mut q: VecDeque<(u32, &Node)> = VecDeque::new();
        let mut level = 1;
        q.push_back((level, self));

        while !q.is_empty() {
            let out = q.pop_front().unwrap();
            level = out.0;
            let n = out.1;

            for c in n.children.iter() {
                q.push_back((level + 1, c));
            }
        }
        level


        // if self.children.is_empty() {
        //     return 1
        // }
        // self.children.iter()
        //     .map(|node| node.borrow().height())
        //     .max().unwrap() + 1
    }
}

struct Tree<'a> {
    root: &'a Node<'a>,
    nodes: Vec<Node<'a>>,
    //size: u32,
}

enum Parent {
    Root,
    Child(usize),
}


impl Parent {
    pub fn from_string(s: &str) -> Self {
        let s = s.trim_end();
        if s == "-1" {
            Parent::Root
        } else {
            Parent::Child(s.parse().unwrap())
        }
    }
}


impl<'a> Tree<'a> {
    pub fn from_stdin() -> Result<Self, io::Error> {
        // First line size
        let mut buffer = String::new();
        io::stdin().read_line(&mut buffer)?;
        let size = buffer.trim_end().parse::<u32>().expect("Unexpectd value");

        // Second line node values
        buffer.clear();
        io::stdin().read_line(&mut buffer)?;
        let parents: Vec<_> = buffer
            .split(' ')
            .map(|s| Parent::from_string(s))
            .collect();
        let mut nodes: Vec<_> = (0..size)
            .map(|i| Node::new(i as i32))
            .collect();

        let mut root: Option<&Node> = None;
        for (i, p) in parents.iter().enumerate() {
            match p {
                Parent::Root => {
                    if root.is_some() {
                        panic!("Multiple roots found");
                    }
                    root = Some(&nodes[i]);
                },
                Parent::Child(p_i) => {
                    // let n_c = Rc::clone(&nodes[i]);
                    // let n_p = &mut nodes[*p_i];
                    nodes[*p_i].add_child(&nodes[i]);
                }
            }
        }
        let root: &Node = root.expect("No root found!");
        Ok(Tree {root, nodes})
    }

    pub fn height(&self) -> u32 {
        self.root.height()
    }
}

fn main() {
    let tree = Tree::from_stdin().unwrap();
    println!("{}", tree.height());
}
