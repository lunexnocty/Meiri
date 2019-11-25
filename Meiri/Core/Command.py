# -*- coding: utf-8 -*-

class Command:
    PLUGINS = {}
    SYSTEM = {}
    def __init__(self, name, isSysCmd=False):
        self.name = name
        self.isSysCmd = isSysCmd
        
    
    def __call__(self, cls):
        self.cls = cls
        cls.session = None
        cls.completed = False
        cls.GetName = lambda _ : self.name
        if self.isSysCmd:
            self.SYSTEM[self.name] = cls
        else:
            self.PLUGINS[self.name] = cls
        def wrapper(*args, **kwargs):
            cls(*args, **kwargs)
        return wrapper

    @classmethod
    def GetCommand(cls, name, session):
        command = None
        if name in cls.SYSTEM:
            command = cls.SYSTEM[name]()
        elif name in cls.PLUGINS:
            command = cls.PLUGINS[name]()
        command.session = session
        return command

'''单元测试代码

@Command('test')
class Test:
    pass

if __name__ == '__main__':
    print(Command.PLUGINS)
    t1 = Command.GetCommand('test')
    t2 = Command.GetCommand('test')
    t2.completed = True
    print(t1.completed, t2.completed)

# '''