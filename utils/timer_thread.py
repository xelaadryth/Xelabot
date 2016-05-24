import time


class Timer:
    """
    A timer that can be canceled.
    """
    active_timers = set()

    def __init__(self, duration, callback):
        self.callback = callback

        # When we're done we set this
        self.start_time = time.time()
        self.duration = duration

        Timer.active_timers.add(self)

    def is_complete(self):
        """
        Tells you if the timer has completed.
        :return: Function - The Function callback specified at creation if the timer has finished, or
                            None if the timer has not yet completed
        """
        if self.start_time + self.duration < time.time():
            return self.callback

        return None

    @staticmethod
    def check_timers():
        """
        Check to see if any timers completed and activate their callbacks and remove ones that are completed.
        Then, run all timer callbacks that have completed successfully.
        """
        callbacks = []
        remaining_timers = set()
        for timer in Timer.active_timers:
            callback = timer.is_complete()
            if callback:
                callbacks.append(callback)
            else:
                remaining_timers.add(timer)
        Timer.active_timers = remaining_timers

        for callback in callbacks:
            callback()

    def cancel(self):
        """
        Cancel the timer.
        """
        Timer.active_timers.discard(self)

    def remaining(self):
        """
        Get the remaining timer time.
        :return: int - The remaining time in seconds
        """
        return int(self.start_time + self.duration - time.time())

    def set(self, duration):
        """
        Resets the timer with a new duration.
        :param duration: float - How much time to set the timer to
        """
        self.start_time = time.time()
        self.duration = duration
