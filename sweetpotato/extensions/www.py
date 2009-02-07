""" sweetpotato module for xhtml taskadapters
"""
if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.abspath(os.curdir))

from sweetpotato.core import TaskAdapter
import os, logging
from lxml.html import parse, tostring

class www(TaskAdapter):
    def __init__(self, task):
        self.selectlist = []
        TaskAdapter.__init__(self, task)

    def runChildTasks(self):
        url = self.task.getProperty('url')
        self.doc = parse(url).getroot() 
        TaskAdapter.runChildTasks(self)

    def run(self):
        sweetpotato = self.task.sweetpotato                
        for select in self.selectlist:
            if select:
                (token, selector) = select.items()[0]
                xml = []
                for element in self.doc.cssselect(selector):
                    xml.append(tostring(element,method="xml",encoding=unicode))
                sweetpotato.setToken(token, u"/n".join(xml))

    class select(TaskAdapter):
        def run(self):
            parent = self.task.getParentWithAttribute('doc')
            selectlist = parent.adapter.selectlist
            properties = self.task.properties
            for select in properties:
                selectlist.append({select: properties[select]})
        
