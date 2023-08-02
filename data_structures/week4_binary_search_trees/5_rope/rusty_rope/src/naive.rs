pub fn cut_and_paste(a: &str, i: usize, j: usize, k: usize) -> String {
    let left = String::from(&a[..i]);
    let cut = String::from(&a[i..j+1]);
    let right = String::from(&a[j+1..]);
    let mut merged = left + &right;
    // a.replace_range(i..j + 1, "");
    merged.insert_str(k, &cut);
    merged
}


pub fn cut_and_paste_mut(a: &mut String, i: usize,
                         j: usize, k: usize) {
    let cut: String = a.drain(i..j + 1).collect();
    a.insert_str(k, &cut);
}


#[cfg(test)]
mod tests {
    use crate::naive;
    #[test]
    fn test_cut_and_paste() {
        let mut s = "helloworld".to_string();
        let result = "ohellworld";
        let s_out = naive::cut_and_paste(&s, 0, 3, 1);
        assert_eq!(s_out, result);

        naive::cut_and_paste_mut(&mut s, 0, 3, 1);
        assert_eq!(s, result);
    }
}
