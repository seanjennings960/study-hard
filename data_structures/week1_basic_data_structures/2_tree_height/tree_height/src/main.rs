use std::io;
use std::rc::Rc;
use std::cell::RefCell;
use std::collections::VecDeque;
use std::cmp::max;
use std::mem;
// use std::any::type_name;


#[derive(Debug)]
struct Node {
    value: i32,
    children: Vec<Rc<RefCell<Node>>>,
}


impl Node {
    pub fn new(value: i32) -> Self {
        let children = Vec::new();
        Node { value, children }
    }

    pub fn add_child(&mut self, next: Node) {
        self.children.push(
            Rc::new(RefCell::new(next)));
    }

    pub fn add_child_ref(&mut self, next: &Rc<RefCell<Node>>) {
        self.children.push(Rc::clone(next));
    }
}


impl Drop for Node {
    fn drop(&mut self) {
        // println!("dropping node {}", self.value);
    }
}



struct Tree { root: Rc<RefCell<Node>> }

impl Tree {
    pub fn from_stdin() -> Self {
        let (parents, mut nodes) = create_nodes();
        update_children(&parents, &nodes);

        // for n in nodes.iter() {
        //     let n = n.borrow();
        //     println!("{}: {}", n.value, n.children.len());
        // }

        let root = nodes.swap_remove(find_root(&parents));
        Tree { root }
    }

    pub fn height(&self) -> u32 {
        let mut queue: VecDeque<(u32, Rc<RefCell<Node>>)> = VecDeque::new();
        queue.push_back((1, Rc::clone(&self.root)));
        let mut max_level = 0;
        while let Some(tup) = queue.pop_front() {
            let (level, n) = tup;
            let n = n.borrow();
            max_level = max(level, max_level);
            // println!("level n | {} {}", level, n.value);
            for c in n.children.iter() {
                let new_c = Rc::clone(c);
                queue.push_back((level + 1, new_c));
            }
        }
        max_level
    }
}


impl Drop for Tree {
    fn drop(&mut self) {
        let mut stack: Vec<Rc<RefCell<Node>>> = Vec::new();
        // println!("Root node: {}", self.root.borrow().value);
        // println!("Root ref count: {}", Rc::strong_count(&self.root));

        let empty_n = Rc::new(RefCell::new(Node::new(1)));
        let first = mem::replace(&mut self.root, empty_n);
        // println!("First ref count: {}", Rc::strong_count(&first));
        stack.push(first);

        while let Some(rc) = stack.pop() {
            // println!("Tree dealloc on node {}", rc.borrow().value);
            // println!("Remaining pointers {}", Rc::strong_count(&rc));
            if let Ok(n) = Rc::try_unwrap(rc) {
                let mut n = n.borrow_mut();

                stack.append(&mut n.children)
            } else {
                // println!("Hit still living RC");
                break;
            }

        }
    }
}

#[derive(Debug)]
enum Parent {
    Root,
    Child(usize),
}


impl Parent {
    pub fn from_numeric(s: &str) -> Self {
        if s == "-1" {
            Parent::Root
        } else {
            Parent::Child(
                s.parse::<usize>().unwrap()
            )
        }
    }

    pub fn from_string(s: &str) -> Vec<Self> {
        let s = s.trim_end();
        s.split(' ').map(Parent::from_numeric).collect()
    }
}


// fn get_type_name<T>(_: &T) -> &str {
//     type_name::<T>()
// }


fn simple_prints(print: bool) {
    if !print {
        return
    }
    let n1 = Node::new(1); // ----------------------------| Node 1 in scope
    // let c1 = Vec::new();
    // let n1 = Node { value: 1, children: c1 };
    let c2 = vec![Rc::new(RefCell::new(n1))];  //         | Node 1 moved
    // println!("Node1: {:?}", n1);                       | This causes an error since n1 is have
    // been moved.
    let mut n2 = Node { value: 10 , children: c2};
    n2.add_child(Node::new(200));
    let n3 = &n2.children[0];
    // let n3 = Node::new(300);

    println!("Node: {:?}", n2);
    println!("n1: {:?}", n3);
}


fn read_stdin() -> Vec<Parent> {
    let mut buf = String::new();
    io::stdin().read_line(&mut buf).unwrap();
    buf.clear();
    io::stdin().read_line(&mut buf).unwrap();
    Parent::from_string(&buf)
}

fn create_nodes() -> (Vec<Parent>, Vec<Rc<RefCell<Node>>>) {
    // let parents: Vec<Parent> = vec![
    //     Parent::Root, Parent::Child(0), Parent::Child(1),
    //     Parent::Child(0), Parent::Child(0)];
    let parents = read_stdin();

    let nodes = parents.iter().enumerate()
        .map(|i| Rc::new(RefCell::new(
                    Node::new(i.0 as i32))))
        .collect();
    (parents, nodes)
}

fn update_children(
        parents: &Vec<Parent>,
        nodes: &Vec<Rc<RefCell<Node>>>) {
    for (i, p) in parents.iter().enumerate() {
        let c = &nodes[i];
        // println!("{}: {:?}", i, p);
        // println!("node {:?}", c);
        match *p {
            Parent::Root => (),
            Parent::Child(p_i) => {
                let p = &nodes[p_i];
                // println!("Parent: {:?}", p);
                // println!("Parenttype: {}", get_type_name(p));
                let mut p = p.borrow_mut();
                // println!("Parent2: {}", get_type_name(&p));
                p.add_child_ref(c);
            },
        }
    }
}

fn find_root(parents: &Vec<Parent>) -> usize {
    let mut root: Option<usize> = None;
    for (i, p) in parents.iter().enumerate() {
        match p {
            Parent::Root => {
                if root.is_none() {
                    root = Some(i)
                } else {
                    panic!("Multiple values of root found")
                }
            },
            _ => (),
        }
    }
    root.expect("No root found")
}


fn main() {
    // println!("Starting program!!!!");
    simple_prints(false);
    // println!("Root: {:?}", r.borrow());
    let t = Tree::from_stdin();
    println!("{}", t.height());

}
