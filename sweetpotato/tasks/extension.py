""" load task adapter extension
"""
from sweetpotato.core import TaskAdapter
import logging

class extension(TaskAdapter):
    def run(self):
        name = self.task.getProperty('name')
        fromList = list(self.task.getProperty('from'))
        self.task.log('loading %s' % '.'.join(fromList), logging.DEBUG)
        self.task.sweetpotato.loadExtension(name, fromList)
