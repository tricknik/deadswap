""" unlink a file
"""
from sweetpotato.core import TaskAdapter
import logging, os

class unlink(TaskAdapter):
    """ unlink a file
    """
    def run(self):
            path = self.task.getProperty('value')
            try:
                os.unlink(path)
            except:
                if os.path.exists(path):
                    raise Exception, "Unlink Failed: %s" % path
                else:
                    pass
