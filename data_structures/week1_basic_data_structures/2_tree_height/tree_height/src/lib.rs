// in lib.rs
// pub mod second;

use std::rc::Rc;
use std::cell::RefCell;
use std::collections::VecDeque;
use std::cmp::max;


type Link<T> = Rc<RefCell<Node<T>>>;

#[derive(Debug)]
struct Node<T> {
    value: T,
    children: Vec<Link<T>>,
}


impl<T> Node<T> {
    pub fn new(value: T) -> Self {
        Node { value, children: Vec::new() }
    }

    pub fn add_child_ref(&mut self, next: &Link<T>) {
        self.children.push(Rc::clone(next));
    }
}


pub struct Tree<T> { root: Option<Link<T>> }

impl<T> Tree<T>
    where T: Copy
{
    pub fn from_parents(parents: &Vec<Option<usize>>, fill: T) -> Self {
        if parents.len() == 0 { return Self { root: None } }
        let mut nodes = (0..parents.len())
            .map(|_| Rc::new(RefCell::new(
                        Node::new(fill))))
            .collect();
        update_children(&parents, &nodes);

        let root = nodes.swap_remove(find_root(&parents));
        Self { root: Some(root) }
    }

    pub fn height(&self) -> u32 {
        let mut queue: VecDeque<(u32, Link<T>)> = VecDeque::new();
        if self.root.is_none() { return 0 }
        queue.push_back((1, Rc::clone(self.root.as_ref().unwrap())));
        let mut max_level = 0;
        while let Some((level, n)) = queue.pop_front() {
            let n = n.borrow();
            max_level = max(level, max_level);
            for c in n.children.iter() {
                let new_c = Rc::clone(c);
                queue.push_back((level + 1, new_c));
            }
        }
        max_level
    }
}


impl<T> Drop for Tree<T> {
    fn drop(&mut self) {
        let mut stack: Vec<Link<T>> = Vec::new();

        let root = self.root.take();
        if root.is_none() { return }
        stack.push(root.unwrap());

        while let Some(rc) = stack.pop() {
            if let Ok(n) = Rc::try_unwrap(rc) {
                let mut n = n.borrow_mut();

                stack.append(&mut n.children)
            } else {
                break;
            }

        }
    }
}


fn update_children<T>(
        parents: &Vec<Option<usize>>,
        nodes: &Vec<Link<T>>) {
    for (i, &p) in parents.iter().enumerate() {
        let c = &nodes[i];
        p.map(|p_i| {
                let p = &nodes[p_i];
                let mut p = p.borrow_mut();
                p.add_child_ref(c);
            }
        );
    }
}


fn find_root(parents: &Vec<Option<usize>>) -> usize {
    let mut root: Option<usize> = None;
    for (i, p) in parents.iter().enumerate() {
        match p {
            None => {
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


#[cfg(test)]
mod tests {
    use super::*;

    fn long_vec(n: u32) -> Vec<Option<usize>>{
        let mut out = vec![None];
        out.append(&mut (0..n - 1).map(|x| Some(x as usize)).collect());
        out

    }
    #[test]
    fn from_parents() {
        let args: Vec<(Vec<Option<usize>>, u32)> = vec![
            (vec![None, Some(0), Some(0), Some(0),
                  Some(2), Some(4)], 4),
            (long_vec(100_000), 100_000),
            (Vec::new(), 0)
        ];
        for (parents, height) in args.iter() {
            let t = Tree::from_parents(parents, 0);
            assert_eq!(t.height(), *height);
        }
    }

    #[test]
    #[should_panic]
    fn no_root() {
        let parents = vec![Some(1), Some(2), Some(3), Some(4), Some(5)];
        let _ = Tree::from_parents(&parents, 0);
    }


}
