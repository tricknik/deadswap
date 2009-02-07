""" sweetpotato module for xhtml taskadapters
"""
if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.abspath(os.curdir))

from sweetpotato.core import TaskAdapter
import os, logging

class htmlElement(TaskAdapter):
    level = 0
    tag = 'html'
    contentProperty = 'value'
    block = True
    blockMode = True
    startWithNewLine = True
    attributeList = ['id','class'] 
    def __init__(self, task):
        self.hasChildElements = False   
        TaskAdapter.__init__(self, task)
    def runChildTasks(self):
        workfile = self.task.getParent('workfile')
        parentTag = self.task.getParentWithAttribute('hasChildElements')
        if hasattr(parentTag.adapter,'hasChildElements') and \
                not parentTag.adapter.hasChildElements:
            workfile.adapter.file.write(">")
            parentTag.adapter.hasChildElements = True
        indent = ""
        attributes = ""
        if self.task.properties:
            elementAttributes = []
            for key in self.task.properties.keys():
                if key in self.attributeList:
                    elementAttributes.append("%s=\"%s\"" % \
                        (key, self.task.getProperty(key)))
            if elementAttributes:
                attributes = " " + " ".join(elementAttributes)
        if self.block or htmlElement.blockMode or self.startWithNewLine:
                indent = "\n" + " " * htmlElement.level
        if self.block:
            htmlElement.level = htmlElement.level + 1
            self.blockMode = True
        workfile.adapter.file.write("%s<%s%s" % (indent, self.tag, attributes))
        htmlElement.blockMode = self.block
        TaskAdapter.runChildTasks(self)
    def run(self):
        parent = self.task.getParent('workfile') 
        value = self.task.getProperty(self.contentProperty)
        indent = ""
        if self.block:
            if value:
                value = value + "\n"
            htmlElement.level = htmlElement.level - 1
            indent = "\n" + " " * htmlElement.level
        if self.hasChildElements:
            parent.adapter.file.write("%s%s</%s>" % (value, indent, self.tag))
        elif value:
            parent.adapter.file.write(">%s%s</%s>" % (value, indent, self.tag))
        else:
            parent.adapter.file.write(" />")

class xhtml(htmlElement):
    """ 
    write xhtml to a working file

    >>> import sys, os
    >>> sys.path.append(os.path.abspath(os.curdir))
    >>> from sweetpotato.core import SweetPotato
    >>> data = '''
    ... sweetpotato:
    ...  test:
    ...   - workfile:
    ...      path: /tmp/test.html 
    ...      overwrite: True
    ...      do:
    ...       - xhtml:
    ...         - head:
    ...           - title: Test Page
    ...         - body:
    ...           - div:
    ...              id: content
    ...              do:
    ...               - h1: A Title
    ...               - h2: A subtitle
    ...               - img:
    ...                  src: someimage.jpg
    ...               - p: Hello World!
    ... '''
    >>> sp = SweetPotato()
    >>> sp.addAdapter(xhtml)
    >>> sp.yaml(data)
    >>> sp.run('test')
    >>> print open('/tmp/test.html').read()
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
     <head>
      <title>Test Page</title>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
     </head>
     <body>
      <div id="content">
       <h1>A Title</h1>
       <h2>A subtitle</h2>
       <img src="someimage.jpg" />
       <p>Hello World!</p>
      </div>
     </body>
    </html>
    <BLANKLINE>
    >>> os.remove('/tmp/test.html')
    """
    attributeList = ['xmlns'] 
    def runChildTasks(self):
        top = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
        self.task.setProperty("xmlns", "http://www.w3.org/1999/xhtml")
        parent = self.task.getParent('workfile')
        parent.adapter.file.write(top)
        htmlElement.runChildTasks(self)

    def run(self):
        htmlElement.run(self)
        parent = self.task.getParent('workfile') 
        parent.adapter.file.write("\n")

           
    class head(htmlElement):
        tag = "head"
        def run(self):
            parent = self.task.getParent('workfile') 
            element = '\n  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
            parent.adapter.file.write(element)
            htmlElement.run(self)
     
        class title(htmlElement):
            tag = "title"
            block = False 

        class meta(htmlElement):
            tag = "meta"
            block = False 
            attributeList = ['name', 'content'] 

        class link(htmlElement):
            tag = "meta"
            block = False 
            attributeList = ['rel', 'href', 'title', 'type'] 

        class style(htmlElement):
            tag = "style"
            attributeList = ['type'] 

        class script(htmlElement):
            tag = "script"
            attributeList = ['type', 'src'] 

    class body(htmlElement):
        tag = "body"

        class table(htmlElement):
            tag = "table"

            class tr(htmlElement):
                tag = "tr"

                class td(htmlElement):
                    tag = "td"

        class div(htmlElement):
            tag = "div"

        class p(htmlElement):
            tag = "p"
            block = False

        class h1(htmlElement):
            tag = "h1"
            block = False

        class h2(h1):
            tag = "h2"

        class h3(h1):
            tag = "h3"

        class h3(h1):
            tag = "h3"

        class h4(h1):
            tag = "h4"

        class img(htmlElement):
            tag = "img"
            attributeList = ['id', 'class', 'src'] 

        class ul(htmlElement):
            tag = "ul"
            class li(htmlElement):
                tag = "li"
                block = False
                contentProperty = "option"
                attributeList = ['id', 'class', 'value'] 

        class ol(ul):
            tag = "ol"

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

