double_me x = x + x

double_us x y = 2*x + 2*y

boomBang xs = [if x == 10 then "BANG" else "BOOM" | x <- xs, even x]

main = do
    putStrLn "Hello World"

lucky :: (Integral a) => a -> String
lucky 7 = "LUCKY NUMBER SEVEN"
lucky x = "Better luck next time."

sum' :: (Num a) => [a] -> a 
sum' [] = 0
sum' x = sum' (init x) + last x 

throwErrorIfNot1 :: (Integral a) => a -> a
throwErrorIfNot1 1 = 0
throwErrorIfNot1 x = error "Anything that isn't one is an error."

addConstant :: (Num a) => a -> [a] -> [a]
addConstant y [] = []
addConstant y (x:xs) = [x + y] ++ addConstant y xs

mean xs = sum xs / length xs
