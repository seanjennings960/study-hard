# python3

from collections import namedtuple

Request = namedtuple("Request", ["arrived_at", "time_to_process"])
Response = namedtuple("Response", ["was_dropped", "started_at"])


class Buffer:
    def __init__(self, size):
        self.size = size
        self.finish_time = []

    def process(self, request):
        while self.finish_time:
            # Clear out any completed packets
            if self.finish_time[0] <= request.arrived_at:
                self.finish_time.pop(0)
            else:
                break

        if len(self.finish_time) < self.size:
            start_time = (self.finish_time[-1] if self.finish_time
                          else request.arrived_at)
            self.finish_time.append(start_time + request.time_to_process)
            return Response(False, start_time)
        else:
            return Response(True, -1)


def process_requests(requests, buf):
    responses = []
    for request in requests:
        responses.append(buf.process(request))
    return responses


def main():
    buffer_size, n_requests = map(int, input().split())
    requests = []
    for _ in range(n_requests):
        arrived_at, time_to_process = map(int, input().split())
        requests.append(Request(arrived_at, time_to_process))

    buf = Buffer(buffer_size)
    responses = process_requests(requests, buf)

    for response in responses:
        print(response.started_at if not response.was_dropped else -1)


if __name__ == "__main__":
    main()
