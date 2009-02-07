""" remove an empty directory
"""
from sweetpotato.core import TaskAdapter
import logging, os

class rmdir(TaskAdapter):
    """ unlink a directory
    """
    def run(self):
            path = self.task.getProperty('value')
            try:
                os.rmdir(path)
            except:
                pass

