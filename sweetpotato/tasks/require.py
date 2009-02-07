""" run a target only if it has not been run before
"""

from sweetpotato.core import TaskAdapter

class require(TaskAdapter):
    """ run a target only if it has not been run before
    """
    def run(self):
        target = self.task.getProperty('value')
        self.task.sweetpotato.require(target)
