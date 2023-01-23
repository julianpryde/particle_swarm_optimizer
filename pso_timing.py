from time import perf_counter


class PSOTiming:
    def __init__(self):
        # self.functions = []
        self.time = None
        self._start = None

    def start(self):
        self._start = perf_counter()

    def end(self):
        self.time = perf_counter() - self._start

    def report(self):
        return "Total time: " + str(self.time) + " seconds"
