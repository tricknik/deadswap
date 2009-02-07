""" set a build token for use in property expansions
"""
from sweetpotato.core import TaskAdapter

class token(TaskAdapter):
    """ set a build token for use in property expansions
    """
    def run(self):
        sweetpotato = self.task.sweetpotato
        properties = self.task.properties
        for property in properties:
            sweetpotato.setToken(property, self.task.getProperty(property))
