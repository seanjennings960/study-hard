# python3

from collections import namedtuple
import heapq

AssignedJob = namedtuple("AssignedJob", ["worker", "started_at"])


class ThreadWorker:
    def __init__(self, id_, free_at):
        self.id_ = id_
        self.free_at = free_at

    def start_new_job(self, job):
        self.free_at += job

    def __lt__(self, other):
        if self.free_at < other.free_at:
            return True
        return self.free_at == other.free_at and self.id_ < other.id_

    def __le__(self, other):
        if self.free_at < other.free_at:
            return True
        return self.free_at == other.free_at and self.id_ <= other.id_

    def __gt__(self, other):
        if self.free_at > other.free_at:
            return True
        return self.free_at == other.free_at and self.id_ > other.id_

    def __ge__(self, other):
        if self.free_at > other.free_at:
            return True
        return self.free_at == other.free_at and self.id_ >= other.id_


    def __eq__(self, other):
        return self.free_at == other.free_at and self.id_ == other.id_

    def __str__(self):
        return f'Worker(id_={self.id_}, free_at={self.free_at})'

    def __repr__(self):
        return f'Worker(id_={self.id_}, free_at={self.free_at})'


def assign_jobs(n_workers, jobs):
    # TODO: replace this code with a faster algorithm.
    result = []
    workers = [ThreadWorker(i, 0) for i in range(n_workers)]
    heapq.heapify(workers)  # We should already be a heap...
    for job in jobs:
        # Get who's ready next.
        next_worker = workers[0]
        # Record job.
        result.append(AssignedJob(
            next_worker.id_, next_worker.free_at))
        # Update free time and add back to the queue.
        next_worker = ThreadWorker(next_worker.id_, next_worker.free_at + job)
        heapq.heappushpop(workers, next_worker)
    return result


def main():
    n_workers, n_jobs = map(int, input().split())
    jobs = list(map(int, input().split()))
    assert len(jobs) == n_jobs

    assigned_jobs = assign_jobs(n_workers, jobs)

    for job in assigned_jobs:
        print(job.worker, job.started_at)


if __name__ == "__main__":
    main()
