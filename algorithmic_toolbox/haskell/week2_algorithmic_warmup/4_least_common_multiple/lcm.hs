-- by Kirill Elagin

lcm_naive :: Int -> Int -> Integer
lcm_naive a b = minimum [ l | l <- [1 .. a' * b'], l `mod` a' == 0 && l `mod` b' == 0 ]
  where
    a' = fromIntegral a :: Integer
    b' = fromIntegral b :: Integer

gcd_fast :: Int -> Int -> Int
gcd_fast a 0 = a
gcd_fast a b = gcd_fast b (a `mod` b)

lcm_fast :: Int -> Int -> Integer
lcm_fast a b = (quot a' gcd) * b'
  where
    a' = fromIntegral a :: Integer
    b' = fromIntegral b :: Integer
    gcd = fromIntegral (gcd_fast a b) :: Integer
    

main :: IO ()
main = do
  [a, b] <- fmap words getLine
  print $ lcm_fast (read a) (read b)
