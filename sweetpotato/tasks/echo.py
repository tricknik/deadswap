from sweetpotato.core import TaskAdapter
""" out to standard logger
"""
class echo(TaskAdapter):
    """ out to standard logger
    """
    def run(self):
        self.task.log(self.task.getProperty('value'))
