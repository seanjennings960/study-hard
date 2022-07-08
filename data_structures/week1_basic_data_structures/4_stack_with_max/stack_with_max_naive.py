#python3
import sys

class StackWithMax():
    def __init__(self):
        self._stack = []
        self._max_stack = []

    def Push(self, a):
        self._stack.append(a)
        if self._max_stack:
            new_max = max(self._max_stack[-1], a)
        else:
            new_max = a
        self._max_stack.append(new_max)

    def Pop(self):
        assert(len(self._stack))
        self._stack.pop()
        self._max_stack.pop()

    def Max(self):
        if not self._max_stack:
            raise ValueError('no elements in stack')
        return self._max_stack[-1]


if __name__ == '__main__':
    stack = StackWithMax()

    num_queries = int(sys.stdin.readline())
    for _ in range(num_queries):
        query = sys.stdin.readline().split()

        if query[0] == "push":
            stack.Push(int(query[1]))
        elif query[0] == "pop":
            stack.Pop()
        elif query[0] == "max":
            print(stack.Max())
        else:
            assert(0)
