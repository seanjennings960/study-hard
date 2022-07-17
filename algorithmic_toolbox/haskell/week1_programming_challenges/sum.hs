main = do
    strIn <- getLine
    let intList = [read x :: Int | x <- words strIn]
    print (sum intList) 

