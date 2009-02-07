""" database interface module
"""
from sweetpotato.core import TaskAdapter
import logging

class db(TaskAdapter):
    """ database interface module
        defines a connection to a data source  
    """

    types = {}
    class read(TaskAdapter):
        def __init__(self, task):
            self.fieldlist = []
            TaskAdapter.__init__(self, task)

        def run(self):
            parent = self.task.getParent("db")
            type = parent.properties["type"]
            sweetpotato = self.task.sweetpotato                
            for row in db.types[type](self.task):
                self.setTokens(row)
                if "target" in self.task.properties:
                    target = self.task.getProperty("target")
                    sweetpotato.run(target)

        def setTokens(self, row):
            sweetpotato = self.task.sweetpotato                
            for field in self.fieldlist:
                if field:
                    (name, token) = field.items()[0]
                    if name in row:
                        self.task.log("setting %s to %s" % (token, row[name]), \
                                logging.DEBUG)
                        sweetpotato.setToken(token, row[name])

        class fields(TaskAdapter):
            def run(self):
                parent = self.task.getParent("read")
                fieldlist = parent.adapter.fieldlist
                properties = self.task.properties
                for field in properties:
                    self.task.log("map field %s to %s" % (field, properties[field]), \
                            logging.DEBUG)
                    fieldlist.append({field: properties[field]})

def dbSweetpotato(task):
        import yaml
        parent = task.getParent("db")
        path = parent.getProperty("path")
        task.log("reading from %s" % path, logging.DEBUG)
        data = yaml.load(open(path))
        for row in data[task.properties["root"]]:
            yield row

def dbMoinCategory(task):
        from lxml.html import parse
        from urlparse import urlsplit
        parent = task.getParent("db")
        url = parent.getProperty("url")
        moin_url = '://'.join(urlsplit(url)[0:2])
        task.log("reading from %s" % moin_url)
        doc = parse(url).getroot()
        for link in doc.cssselect('#content ol li a'):
            page = link.attrib['href'].split('?')[0]
            name = page.split('/').pop()
            title = link.text_content();
            row = {'url': '%s%s' % (moin_url, page),
                   'name': name,
                   'title': title}
            yield row

def dbDir(task):
        import os
        parent = task.getParent("db")
        path = parent.getProperty("path")
        task.log("listing %s" % path, logging.DEBUG)
        if os.path.isdir(path):
            for item in os.listdir(path):
                row = {'name': item}
                yield row

def dbFile(task):
        import os
        parent = task.getParent("db")
        path = parent.getProperty("path")
        task.log("reading %s" % path, logging.DEBUG)
        if os.path.isfile(path):
            file = open(path)
            content = file.read()
            row = {'path': path,
                   'name': os.path.basename(path),
                   'content': content.strip()
            }
            yield row

def dbDirShift(task):
        import os, time
        parent = task.getParent("db")
        path = parent.getProperty("path")
        age = parent.getProperty("age")
        if age:
            mature = time.time() - float(age) * 60
        task.log("shifting %s" % path, logging.DEBUG)
        if os.path.isdir(path):
            row = None
            first = None
            for item in os.listdir(path):
                mtime = os.path.getmtime('/'.join((path,item)))
                if not first or mtime < first:
                    if not age or mtime < mature:
                        first = mtime
                        row = {'name': item}
            if row:
                yield row

def dbSmsInbox(task):
        parent = task.getParent("db")
        delete = task.getProperty("delete")
        prefix = task.getProperty("prefix")
        if prefix:
            prefixLength = len(prefix)
        task.log("reading from inbox", logging.DEBUG)
        import gammu
        sm = gammu.StateMachine()
        sm.ReadConfig()
        sm.Init()
        status = sm.GetSMSStatus()
        remain = status['SIMUsed'] + status['PhoneUsed']
        start = True
        while remain > 0:
            if start:
                sms = sm.GetNextSMS(Start = True, Folder = 0)
                start = False
            else:
                sms = sm.GetNextSMS(Location = sms[0]['Location'], Folder = 0)
            remain = remain - 1
            for m in sms:
                message = {'id': str(m['DateTime']), 
                       'text': m['Text'], 
                       'caller_id_number': m['Number']}
                if delete:
                    sm.DeleteSMS(0, m['Location'])
                if not prefix or prefix == message['caller_id_number'][:prefixLength]:
                    yield message

db.types["sweetpotato"] = dbSweetpotato
db.types["moincategory"] = dbMoinCategory
db.types["dir"] = dbDir
db.types["file"] = dbFile
db.types["dirshift"] = dbDirShift
db.types["smsinbox"] = dbSmsInbox

