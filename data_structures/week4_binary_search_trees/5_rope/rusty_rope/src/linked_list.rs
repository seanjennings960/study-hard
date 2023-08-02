
use std::ptr::NonNull;
// use std::mem;


#[allow(dead_code)]
pub struct Link<T> {
    pub value: T,
    next: Option<NonNull<Link<T>>>
}


#[allow(dead_code)]
impl<T> Link<T> {
    pub fn new(value: T) -> Link<T> {
        Link{value, next: None}
    }

    pub fn new_with_link(value: T, next: &Link<T>) -> Link<T> {
        Link {
            value, next: Some(NonNull::from(next))
        }
    }
}

pub struct List<T> {
    head: Option<NonNull<Link<T>>>
}

#[allow(dead_code)]
impl<T> List<T> {
    pub fn new() -> List<T> {
        List {head: None}
    }

    pub fn head(&self) -> Option<&Link<T>> {
        self.head.map(|h| unsafe {h.as_ref()})
    }

    pub fn head_mut(&mut self) -> Option<&mut Link<T>> {
        self.head.map(|mut h| unsafe {h.as_mut()})
    }

    pub fn tail(&self) -> Option<&Link<T>> {
        self.head().map(|mut link| {
            loop {
                link = match link.next {
                    Some(next) => unsafe {
                        next.as_ref()
                    },
                    None => break link
                }
            }
        })
    }

    pub fn tail_mut(&mut self) -> Option<&mut Link<T>> {
        self.head_mut().map(|mut link| {
            loop {
                link = match link.next {
                    Some(mut next) => unsafe {
                        next.as_mut()
                    },
                    None => break link
                }
            }
        })
    }

    fn add_link(&self, value: T) -> NonNull<Link<T>> {
        let b = Box::new(Link::new(value));
        NonNull::new(Box::into_raw(b)).expect("Allocation failed??")
    }

    pub fn push(&mut self, value: T) {
        let new_link = Some(self.add_link(value));
        match self.tail_mut() {
            Some(tail) => {
                tail.next = new_link;
            },
            None => {
                self.head = new_link;
            }
        }

    }

}

impl<T> Drop for List<T> {
    fn drop(&mut self) {
        let mut next = self.head;
        loop {
            match next {
                Some(non_null) => {
                    // Safety: a given node contains the only raw pointer to the next.
                    let mut node = unsafe {
                        Box::from_raw(non_null.as_ptr())
                    };
                    next = node.as_mut().next;
                    drop(node);
                },
                None => break
            };
        }
    }
}


#[cfg(test)]
mod tests {
    use crate::linked_list::List;

    #[test]
    fn test_linked_list() {
        let mut li = List::new();
        li.push(0);
        li.push(10);
        li.push(20);
        li.push(30);

        let head = li.head().expect("No head!");
        assert_eq!(head.value, 0);
        assert_eq!(li.tail().expect("No tail!").value, 30);

        li.tail_mut().map(|tail| {tail.value = 35});
        assert_eq!(li.tail().expect("No tail!").value, 35);
        // assert!(head.next.is_none());

        // a.push(20);
        // assert_eq!(a.head.next.expect("next not filled").value, 20)

    }

}
