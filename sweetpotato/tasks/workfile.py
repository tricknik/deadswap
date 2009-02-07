""" sweetpotato module for workfile task adapter
"""

from sweetpotato.core import TaskAdapter
import os, logging


class workfile(TaskAdapter):
    """ sweetpotato task adapter for manipulating files
    """

    def runChildTasks(self):
        """ open working file for child tasks
        """
        self.path = self.task.getProperty("path")
        update = True
        mode = 'w'
        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        elif os.path.exists(self.path):
            if not os.path.isfile(self.path):
                raise Exception, "work file can not be a directory"
            if self.task.getProperty("append"):
                mode = 'a'
            else:
                divert =  self.task.getProperty("divert")
                backup =  self.task.getProperty("backup")
                if divert:
                    self.path = '.'.join((self.path, divert))
                    self.task.log("diverting to %s" % self.path, logging.DEBUG)
                elif backup:
                    dst = '.'.join((self.path, backup))
                    while os.path.exists(dst):
                        self.task.log("%s exists!" % dst, logging.WARNING)
                        dst = '.'.join((dst, backup))
                    os.rename(self.path, dst)
                    self.task.log("backup to %s" % dst, logging.DEBUG)
                else:
                    update = False
                    self.task.log("file %s exists" % self.path, logging.DEBUG)
        if update or self.task.getProperty("overwrite"):
            self.task.log("open file %s (%s)" % (self.path, mode), logging.DEBUG)
            self.file = open(self.path, mode)
            TaskAdapter.runChildTasks(self)
        else:
            self.task.log("%s: nothing to do" % self.path, logging.INFO)

    def run(self):
        self.file.close()

    class write(TaskAdapter):
        """ write data to working file
        """
        def run(self):
            data = self.task.getProperty("value")
            parent = self.task.getParent("workfile")
            parent.adapter.file.write(data.encode("UTF-8"))
