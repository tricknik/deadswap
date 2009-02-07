""" provide mutex to subtasks with lock file
"""
from sweetpotato.core import TaskAdapter
import logging, fcntl, os

class lock(TaskAdapter):
    """ provide mutex to subtasks with lock file
    """

    locks = {}
    def getLock(self):
        return lock.locks[self.key]
    def runChildTasks(self):
        if 'key' in self.task.properties:
            self.key = self.task.getProperty('key')
        else:
            self.key = '_'.join((str(self.task.taskId), self.task.type))
        if not self.key in lock.locks:
            lock.locks[self.key] = open('/tmp/sweetpotato_%s' % self.key, 'a')
            self.task.log('Created queue %s' % self.key, logging.DEBUG)
        l = self.getLock()
        fcntl.flock(l, fcntl.LOCK_EX)
        TaskAdapter.runChildTasks(self)
        fcntl.flock(l, fcntl.LOCK_UN)
    def run(self):
            l = open('/tmp/sweetpotato_%s' % self.key, 'a')
            l.close()
            os.unlink('/tmp/sweetpotato_%s' %self.key)

