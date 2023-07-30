mod naive;

use pyo3::prelude::*;

#[pyfunction]
fn process_rust_naive(
        s: &str, ops: Vec<(usize, usize, usize)>,
        mutable: bool) -> PyResult<String> {
    let mut s_out = s.to_string();
    for (i, j, k) in ops {
        if mutable {
            naive::cut_and_paste_mut(&mut s_out, i, j, k);
        }
        else {
            s_out = naive::cut_and_paste(&s_out, i, j, k);
        }
    }
    Ok(s_out)
}

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name="lib")]
fn rusty_rope(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(process_rust_naive, m)?)?;
    Ok(())
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