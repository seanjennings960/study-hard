# python3


class MaxQueue:
    def __init__(self):
        self._queue = []
        self._max_queue = []

    def enqueue(self, a):
        self._queue.append(a)
        while self._max_queue and self._max_queue[-1] < a:
            # Remove all values in max queue that are less than
            # a. This will result in a monotonically decreasing
            # max queue. Thus, a single comparison where the tail
            # of the queue is >= or equal to a is sufficient to terminate
            # this loop.
            self._max_queue.pop()
        self._max_queue.append(a)

    def dequeue(self):
        if not self._queue:
            raise valueError('Queue is empty')
        new_value = self._queue.pop(0)
        if self._max_queue[0] == new_value:
            self._max_queue.pop(0)
        return new_value

    def max(self):
        if not self._max_queue:
            raise ValueError('Queue is empty!')
        return self._max_queue[0]

    def __str__(self):
        return str(self._queue)



def max_sliding_window_naive(sequence, m):
    n = len(sequence)
    maximums = []
    queue = MaxQueue()
    for i in range(m):
        queue.enqueue(sequence[i])

    for i in range(m, n):
        maximums.append(queue.max())
        queue.dequeue()
        queue.enqueue(sequence[i])
    maximums.append(queue.max())

    return maximums

if __name__ == '__main__':
    n = int(input())
    input_sequence = [int(i) for i in input().split()]
    assert len(input_sequence) == n
    window_size = int(input())

    print(*max_sliding_window_naive(input_sequence, window_size))

