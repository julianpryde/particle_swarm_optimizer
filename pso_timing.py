from time import perf_counter


class PSOTiming:
    def __init__(self):
        # self.functions = []
        self._time = None
        self._start = None

    def start(self):
        self._start = perf_counter()

    def end(self):
        self._time = perf_counter() - self._start
        # self.functions.append(function_name)

    def report(self):
        print("Total time: " + str(self._time) + "seconds")
