-- by Kirill Elagin

gcd_naive :: Int -> Int -> Int
gcd_naive a b = maximum [ d | d <- [1 .. min a b], a `mod` d == 0 && b `mod` d == 0 ]

gcd_fast :: Int -> Int -> Int
gcd_fast a 0 = a
gcd_fast a b = gcd_fast b (a `mod` b)

main :: IO ()
main = do
  [a, b] <- fmap words getLine
  print $ gcd_fast (read a) (read b)
