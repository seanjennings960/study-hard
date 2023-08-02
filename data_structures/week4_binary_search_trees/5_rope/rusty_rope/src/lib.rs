mod naive;
pub mod linked_list;
// mod rope;

use pyo3::prelude::*;
// use rope::Rope;

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

// #[allow(dead_code)]
// fn process_rust_rope(s: &str, _ops: Vec<(usize, usize, usize)>)
// -> PyResult<String> {
//     let _r = Rope::new(s);
//     Ok("Hello".to_string())
// }

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
