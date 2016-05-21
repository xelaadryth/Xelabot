import threading


class TimerThread():
    """
    A timer that can be canceled.
    """
    def __init__(self, duration, callback):
        self.callback = callback

        # When we're done we set this
        self.complete_event = threading.Event()

        # If we want to cancel the thread, we set this
        self.cancel_event = threading.Event()

        # Making self.time_left thread-safe with a mutex
        self.lock = threading.Lock()
        self.time_left = duration

        # Start the thread
        self.thread = threading.Thread(target=self.run_timer)
        self.thread.daemon = True
        self.thread.start()

    def run_timer(self):
        """
        The thread's execution; based on wake-able sleeps and thus not that accurate.
        """
        self.lock.acquire()
        while self.time_left > 0 and not self.cancel_event.is_set():
            self.lock.release()
            # If the stop event gets set we wake up immediately
            self.cancel_event.wait(1)
            self.lock.acquire()
            self.time_left -= 1
        self.lock.release()
        self.complete_event.set()

    def is_complete(self):
        """
        If timer completes successfully, calls the callback given to it. Note that this happens in the main thread, not
        the created daemon thread.
        :return: bool - True if the timer has ticked to 0 or has been canceled
        """
        if self.complete_event.is_set():
            if not self.cancel_event.set():
                self.callback()
            return True
        else:
            return False

    def cancel(self):
        """
        Cancel the timer.
        """
        self.cancel_event.set()
        self.thread.join()

    def remaining(self):
        """
        Get the remaining timer time.
        :return: int - The remaining time
        """
        self.lock.acquire()
        time_left = self.time_left
        self.lock.release()
        return time_left

    def set(self, duration):
        """
        Set the remaining timer time.
        :param duration: int - How much time to set the timer to
        """
        self.lock.acquire()
        self.time_left = duration
        self.lock.release()
