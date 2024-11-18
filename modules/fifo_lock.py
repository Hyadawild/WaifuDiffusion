import threading
import collections


class FIFOLock:
    """
    A lock that grants access to threads in a first-in, first-out (FIFO) order.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._queue_lock = threading.Lock()  # Protects access to the queue.
        self._waiting_threads = collections.deque()

    def acquire(self, blocking=True):
        """
        Acquire the lock in FIFO order.
        
        :param blocking: If False, returns immediately if the lock is unavailable.
        :return: True if the lock was acquired, False otherwise (only if blocking is False).
        """
        with self._queue_lock:
            # Try to acquire the main lock immediately.
            if self._lock.acquire(False):
                return True
            if not blocking:
                return False

            # Otherwise, add the thread to the waiting queue.
            release_event = threading.Event()
            self._waiting_threads.append(release_event)

        # Wait until this thread is signaled.
        release_event.wait()
        self._lock.acquire()
        return True

    def release(self):
        """
        Release the lock and notify the next thread in the queue, if any.
        """
        with self._queue_lock:
            if self._waiting_threads:
                # Wake up the next thread in the queue.
                next_event = self._waiting_threads.popleft()
                next_event.set()

        self._lock.release()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
