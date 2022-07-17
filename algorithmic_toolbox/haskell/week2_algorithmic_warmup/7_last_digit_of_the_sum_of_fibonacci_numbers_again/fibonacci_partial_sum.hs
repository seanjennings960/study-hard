-- by Kirill Elagin

fibonacci_partial_sum_naive :: Integer -> Integer -> Int
fibonacci_partial_sum_naive from to = let (a', b', _) = helper (0, 1, 0) from
                                          (_, _, s) = helper (a', b', a') (to - from)
                                      in s
  where
    helper (a, b, s) 0 = (a, b, s `mod` 10)
    helper (a, b, s) i = helper (b, a + b, s + b) (i - 1)


fibonacci_partial_sum :: Integer -> Integer -> Int
fibonacci_partial_sum from to = (sum_to - sum_from) `mod` 10
  where
    sum_to = fibonacci_sum to
    sum_from = fibonacci_sum (from - 1)


fibonacci_sum :: Integer -> Int
fibonacci_sum n =  (integer_sum + sum (take input_mod cycle_list)) `mod` 10
  where 
    actual_n = n + 1
    cycle_list = get_cycle_list 10
    cycle_num = toInteger $ length cycle_list
    input_quot = quot actual_n cycle_num
    input_mod = fromInteger $ mod actual_n cycle_num 
    integer_sum = fromInteger $ (input_quot * toInteger (sum cycle_list)) `mod` 10 

get_inf_fib_list :: Int -> [Int]
get_inf_fib_list m = [init0, init1] ++ more_fib init0 init1 m
  where 
    init0 = 0
    init1 = 1
    more_fib a b m = let sum_ab = (a + b) `mod` m
                     in [sum_ab] ++ more_fib b sum_ab m


get_cycle_list :: Int -> [Int]
get_cycle_list m = let cycle_num = find_cycle_start m in take cycle_num (get_inf_fib_list m)


find_cycle_start :: Int -> Int
-- Use tail of fib list so the first occurence of [0 1 1] is skipped.
find_cycle_start m = find_sublist (tail fib_list) [0, 1, 1] + 1
  where fib_list = get_inf_fib_list m

find_sublist :: [Int] -> [Int] -> Int
find_sublist a b = if (take (length b) a) == b then 0 else 1 + find_sublist (tail a) b 


main :: IO ()
main = do
  [from, to] <- fmap words getLine
  print $ fibonacci_partial_sum (read from) (read to)
