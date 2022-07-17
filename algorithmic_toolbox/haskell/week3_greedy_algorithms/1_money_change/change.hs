-- by Kirill Elagin

demon_list = [10, 5, 1]

get_change :: Int -> Int
get_change 0 = 0
get_change m = 1 + get_change (m - max_coin)
  where
    max_coin = get_max_coin demon_list m

get_max_coin :: [Int] -> Int -> Int
get_max_coin [] m = error "Coins don't evenly match"
get_max_coin demons m = if m - head demons >= 0 
    then head demons else get_max_coin (tail demons) m


main :: IO ()
main = do
  [m] <- fmap words getLine
  print $ get_change (read m)
