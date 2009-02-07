from collections import deque
import yaml, re, logging

class TaskAdapter:
    """ Base TaskAdapter module
        All new task types require an
        adapter that extends this class
   """
    def __init__(self, task):
        self.task = task
    def runChildTasks(self):
        for task in self.task.tasks:
            task.run()
        if hasattr(self, "run"):
            self.run()


class Task:
    """ Process control task
    """
    taskCount = 0
    def __init__(self, sweetpotato, parent, type, data):
        Task.taskCount = Task.taskCount + 1
        self.taskId = Task.taskCount
        self.tasks = deque()
        self.properties = {}
        self.sweetpotato = sweetpotato
        self.parent = parent
        self.type = str(type)
        self.adapter = TaskAdapter(self)
        self.log("creating task %s with type %s" % 
                (self.taskId, self.type), logging.DEBUG)
        self.read("value", data)

    def read(self, property, data):
        if hasattr(data,"popitem"):
            self.readDict(data)
        elif hasattr(data,"pop"):
            self.readList(data, property)
        else:
            self.setProperty(property, data)

    def setProperty(self, property, value):
        if self.properties.has_key(property):
            if hasattr(self.properties[property],"appendleft"):
                self.properties[property].append(value)
            else:
                value = deque((self.properties[property], value))
                self.properties[property] = value
        else:
            self.properties[property] = value

    def readDict(self, data):
        while data:
            key, value = data.popitem()
            if hasattr(value, "pop"):
                self.readList([{key:value}])
            else:
                self.setProperty(key, value)

    def readList(self, data, property="value"):
        while data:
            value = data.pop()
            if hasattr(value, "popitem"):
                itemkey, itemdata = value.items()[0]
                if hasattr(itemdata, 'append') \
                        and not hasattr(itemdata[0], 'pop'):
                    self.readList(itemdata, itemkey)
                else:
                    self.addChildTask(value)
            else:
                self.setProperty(property, value)

    def addChildTask(self, value, property="value"):
        if hasattr(value, "popitem"):
            itemkey, itemvalue = value.popitem()
            child = Task(self.sweetpotato, self, itemkey, itemvalue)
            self.tasks.appendleft(child)
            if (value):
                raise Exception, "Only 1 key alowed in Task"
        else:
            raise Exception, "Task must be {key: value}"

    def getParent(self, parentType):
        parent = self.parent
        while parentType != parent.type:
            parent = parent.parent
        return parent

    def getParentWithAttribute(self, attribute):
        parent = self.parent
        while parent.parent and not hasattr(parent.adapter, attribute):
            parent = parent.parent
        return parent

    def loadAdapter(self):
        module = None
        parent = self.parent
        while parent:
            if hasattr(parent.adapter, self.type):
                module = parent.adapter
                self.adapter = getattr(module, self.type)(self)
                self.log("%s loaded from %s" % (self.type, parent.type), logging.DEBUG)
                break
            parent = parent.parent
        if not module: 
            if self.type in globals():
                self.adapter = globals()[self.type](self)
                self.log("%s loaded from globals" % self.type, logging.DEBUG)
            else:
                module = self.importModule(self.type)
                self.adapter = getattr(module, self.type)(self)

    def importModule(self, type):
        from copy import copy
        module = None
        for name in self.sweetpotato.modules:
            fromList = self.sweetpotato.modules[name]
            nameList = copy(fromList)
            nameList.append(type)
            taskModule = ".".join(nameList)
            try:
                module =  __import__(taskModule, fromlist=fromList)
                self.log("%s loaded from %s" % (type, fromList), logging.DEBUG)
                break
            except ImportError:
                module = None
                self.log("%s not in %s" % (type, fromList), logging.DEBUG)
        if not module:
            raise Exception, "Unable to load %s" % type
        return module

    def log(self, message, level=logging.INFO):
        self.sweetpotato.log(message, self, level)

    def expand(self, value):
        key = value.groups()[0].strip().lower()
        if key in self.sweetpotato.tokens:
            token = self.sweetpotato.tokens[key]    
        else:
            token = None
        return u'%s' % token

    def expandValue(self, value):
        expanded = value
        if hasattr(value,'islower'):
            expanded = re.sub(self.sweetpotato.regex, self.expand, value)
        return expanded

    def getProperty(self, key):
        if key in self.properties:
            if hasattr(self.properties[key],"islower"):
                property = self.properties[key]
                expanded = self.expandValue(property)
            elif hasattr(self.properties[key],"append"):
                expanded = deque()
                for item in  self.properties[key]:
                    expandedItem = self.expandValue(item)
                    if expandedItem:
                        expanded.appendleft(expandedItem)
            else:
                expanded = self.properties[key]
        else:
            expanded = ''
        return expanded

    def run(self):
        if self.parent:
            self.loadAdapter()
        self.adapter.runChildTasks()

    def __str__(self):
        task = self
        typePath = deque([self.type])
        while task and task.parent:
            task = task.parent
            if task.adapter:
                typePath.appendleft(task.type)
            task = task.parent
        strType = ".".join(typePath)
        return strType


class SweetPotato:
    """ Process control instance
    """
    regex = re.compile("\{\{([^}]+)\}\}")

    def __init__(self, options={}):
        self.modules = {"core": ["sweetpotato", "tasks"]}
        self.options = options
        self.tokens = {}
        if hasattr(self.options, "tokens") and \
                self.options.tokens:
            for token in self.options.tokens:
                (key, value) = token.split("=")
                self.setToken(key, value.strip())
            del self.options.tokens
        logLevel = logging.INFO
        if hasattr(self.options, "log_level"):
            if "error" == self.options.log_level:
                logLevel = logging.ERROR
            elif "warning" == self.options.log_level:
                logLevel = logging.WARNING
            elif "info" == self.options.log_level:
                logLevel = logging.INFO
            elif "debug" == self.options.log_level:
                logLevel = logging.DEBUG
        if hasattr(self.options, "file"):
            file = options.file
            self.open(file)
        self.targets = {}
        self.startTime = None
        self.loggers = {}
        logging.basicConfig(level=logLevel,
            format='%(asctime)s %(name)-12s %(levelname)-5s %(message)s',
            datefmt='%m-%d %H:%M')

    def addAdapter(self, adapterClass):
        globals()[adapterClass.__name__] = adapterClass

    def loadExtension(self, name, fromList):
        self.modules[name] = fromList

    def open(self, buildfile):
        yamlData = yaml.load(open(buildfile))
        self.load(yamlData)

    def yaml(self, yamlStream):
        yamlData = yaml.load(yamlStream)
        self.load(yamlData)

    def load(self, data):
        self.buildData = data["sweetpotato"]

    def setToken(self, key, value):
        self.tokens[key.strip().lower()] = value

    def getTarget(self, target):
        if not self.targets.has_key(target):
            self.targets[target] = \
                Task(self, None, "target", self.buildData[target])
            del self.buildData[target]
        return self.targets[target]

    def log(self, message, task=None, level=logging.INFO):
        loggerKey = 'sweetpotato'    
        if hasattr(task,'type'):
            loggerKey = "%s:%s" % (task.type, task.taskId)
        if not loggerKey in self.loggers:
            self.loggers[loggerKey] = logging.getLogger(loggerKey)
        self.loggers[loggerKey].log(level, message)

    def require(self, targetName):
        if not targetName in self.targets:
            target = self.getTarget(targetName)
            self.log("Loading %s" % targetName.title(), level=logging.DEBUG)
            target.run()
            self.log("%s Loaded" % targetName.title(), level=logging.DEBUG)

    def run(self,targetName):
        self.log("Starting %s " % targetName.title(), level=logging.DEBUG)
        target = self.getTarget(targetName)
        target.run()
        self.log("%s Ended" % targetName.title(), level=logging.DEBUG)

def _test():
    import doctest
    doctest.testfile('core.doctest')

if __name__ == "__main__":
        _test()

