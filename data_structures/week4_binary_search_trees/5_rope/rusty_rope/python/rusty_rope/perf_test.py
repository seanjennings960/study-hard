import itertools
import logging
import time

import numpy as np

# from rope import Rope
from rusty_rope import Rope
from rusty_rope.lib import process_rust_naive


logging.basicConfig(level=logging.INFO)


def gen_random_ops(n, n_ops):
    start = np.random.randint(n, size=n_ops)
    end = np.random.randint(start, n)
    insert = np.random.randint(n - (end - start))
    return start, end, insert

def process_rope(s, ops):
    r = Rope(s)
    for i, j, k in ops:
        r.process(i, j, k)
    return str(r)

def cut_and_paste(s, i, j, k):
    left, cut, right = s[:i], s[i:j + 1], s[j + 1:]
    merged = left + right
    return merged[:k] + cut + merged[k:]

def process_naive(s, ops):
    for (i, j, k) in ops:
        s = cut_and_paste(s, i, j, k)
    return s

def time_function(f, *args):
    start_time = time.monotonic()
    result = f(*args)
    duration = time.monotonic() - start_time
    logging.info(f"{f.__name__} took {duration} seconds")
    return duration, result


def run_test(test_cases):
    naive_times = {}
    rope_times = {}
    rust_times = {}
    for (s, ops) in test_cases:
        logging.info("Running test for string length: "
                     f"{len(s)} | n_ops: {len(ops)}")

        naive_times[(len(s), len(ops))], res_naive = time_function(
            process_naive, s, ops
        )
        rope_times[(len(s), len(ops))], res_rope = time_function(
            process_rope, s, ops
        )
        rust_times[(len(s), len(ops))], res_rust = time_function(
            process_rust_naive, s, ops, False
        )

        logging.info("Naive and rope equalivalent: "
                     f"{res_naive == res_rope}")
        logging.info("Naive and rust equivalent: "
                     f"{res_naive == res_rust}")
    return naive_times, rope_times, rust_times

def main():
    np.random.seed(1)
    # n_ops = [10, 100, 1000, int(1e4), int(1e5)]
    n_ops = [int(3e3)]
    string_lengths = [1e6]
    string_base = "hellosup!!"

    test_cases = [
        (string_base * int(str_len / len(string_base)),
            list(zip(*gen_random_ops(str_len, n_op))))
        for str_len, n_op in itertools.product(string_lengths, n_ops)
    ]
    naive_times, rope_times, rust_times = run_test(test_cases)
    print("Naive - rope")
    for key in naive_times:
        diff = naive_times[key] - rope_times[key]
        print(f"{key}: {diff}")
    print("Naive - rust")
    for key in naive_times:
        diff = naive_times[key] - rust_times[key]
        print(f"{key}: {diff}")



if __name__ == "__main__":
    main()
