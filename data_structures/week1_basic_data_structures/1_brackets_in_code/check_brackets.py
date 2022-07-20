# python3

from collections import namedtuple

Bracket = namedtuple("Bracket", ["char", "position"])


def are_matching(left, right):
    return (left + right) in ["()", "[]", "{}"]


def find_mismatch(text):
    stack = []
    for i, char in enumerate(text):
        if char in "([{":
            stack.append(Bracket(char, i))

        if char in ")]}":
            if not stack:
                return i
            top = stack.pop().char
            if ((top == '(' and char != ')') or
                    (top == '[' and char != ']') or
                    (top == '{' and char != '}')):
                return i

    first = None
    while stack:
        first = stack.pop()
    if first is not None:
        return first.position
    return first


def main():
    text = input()
    mismatch = find_mismatch(text)
    if mismatch is None:
        print('Success')
    else:
        print(mismatch + 1)
    # Printing answer, write your code here


if __name__ == "__main__":
    main()
