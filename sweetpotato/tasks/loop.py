from sweetpotato.core import TaskAdapter
import time

class loop(TaskAdapter):
    def runChildTasks(self):
        while True:
            TaskAdapter.runChildTasks(self)
            time.sleep(23);
