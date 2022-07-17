findElement :: Eq a => a -> [a] -> Int
findElement x [] = -1
findElement x list = if head list == x 
    then 0 
    else 
        if rest == -1
        then -1
        else 1 + rest
        where rest = findElement x (tail list)

secondMax :: [Int] -> Int 
secondMax [] = error "Must be longer than 0" 
secondMax [x] = error "Must be longer than 1" 
secondMax xs 
    | max_index == 0 = maximum end_list 
    | max_index == (length xs - 1) = maximum start_list
    | otherwise = max (maximum start_list) (maximum end_list)
    where max_index = findElement (maximum xs) xs
          start_list = take max_index xs
          end_list = drop (max_index + 1) xs
    

maxProduct :: [Int] -> Int 
maxProduct [] = error "Need at least 2 inputs"
maxProduct [x] = error "Need at least 2 inputs"
maxProduct xs = maximum xs * secondMax xs

main = do
    -- Throw out first line; we don't need number of integers.
    strIn <- getLine
    strIn <- getLine
    let intList = [read x :: Int | x <- words strIn]
    print (maxProduct intList)
