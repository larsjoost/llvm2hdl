from messages import Messages


class InstanceStatistics:

    def __init__(self):
        self.statistics = {}
        self.msg = Messages()

    def increment(self, element):
        try:
            self.statistics[element] = self.statistics[element] + 1
        except KeyError:
            self.statistics[element] = 1

    def print(self):
        self.msg.note("Instance statistics:")
        for i in self.statistics.keys():
            self.msg.note(f"{i}: {str(self.statistics[i])}")