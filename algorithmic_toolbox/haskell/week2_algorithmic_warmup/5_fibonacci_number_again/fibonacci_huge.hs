import Control.Monad (forM)
-- by Kirill Elagin

get_fib_mod_list :: Integer -> Int -> [Int]
get_fib_mod_list 0 m = [0]
get_fib_mod_list 1 m = [0, 1 `mod` m]
get_fib_mod_list n m = last_list ++ [(a + b) `mod` m]
  where
    last_list = get_fib_mod_list (n - 1) m
    a:b:rest = reverse last_list

get_fibonacci_huge_naive :: Integer -> Int -> Int
get_fibonacci_huge_naive n m = helper (0, 1) n
  where
    helper (a, _) 0 = a `mod` m
    helper (a, b) i = helper (b, a + b) (i - 1)

print_naive_and_list :: Integer -> Int -> IO ()
print_naive_and_list n m = do
  print $ "n m: " ++ show n ++ " " ++ show m
  print $ get_fibonacci_huge_naive n m
  let fib_list = get_inf_fib_list m
  print $ take (fromInteger n) fib_list
  print $ "Cycle Index: " ++ show (find_cycle_start (tail fib_list) [0, 1, 1])

get_inf_fib_list :: Int -> [Int]
get_inf_fib_list m = [init0, init1] ++ more_fib init0 init1 m
  where 
    init0 = 0
    init1 = 1
    more_fib a b m = let sum_ab = (a + b) `mod` m
                     in [sum_ab] ++ more_fib b sum_ab m

get_fibonacci_huge :: Integer -> Int -> Int
get_fibonacci_huge n m = fib_list !! (fromInteger(n `mod` cycle))
  where
    fib_list = get_inf_fib_list m
    -- Use tail of fib list so the first occurence of [0 1 1] is skipped.
    cycle = toInteger $ (find_cycle_start (tail fib_list) [0, 1, 1]) + 1


find_cycle_start :: [Int] -> [Int] -> Int
find_cycle_start a b = if (take (length b) a) == b then 0 else 1 + find_cycle_start (tail a) b 


main = do
  -- let input = [(30, a) | a <- [2..10]]
  -- print $ input
  -- forM input $ uncurry print_naive_and_list

  [n, m] <- fmap words getLine
  print $ get_fibonacci_huge (read n) (read m)
