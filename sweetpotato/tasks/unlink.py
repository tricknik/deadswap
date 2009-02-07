""" unlink a file
"""
from sweetpotato.core import TaskAdapter
import logging, os

class unlink(TaskAdapter):
    """ unlink a file
    """
    def run(self):
            path = self.task.getProperty('value')
            os.unlink(path)

