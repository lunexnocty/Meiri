# -*- coding: utf-8 -*-

class User:
    def __init__(self, uid, name='unknown'):
        self.uid = str(uid)
        self.name = name
        self.isAdmin = False
        if self.uid in UserManager.GetSuperUsers():
            self.isAdmin = True

    def GetUID(self):
        return self.uid
    def SetName(self, name):
        self.name = name
    def GetName(self):
        return self.name
    def AuthorityCheck(self):
        return self.isAdmin

    def AddAttr(self, name, value=None):
        self.__dict__[name] = value
    
    def AddMethod(self, name, method):
        self.__dict__[name] = method
    

class UserManager:
    _superUsers = []
    def __init__(self):
        self.users = {}
    
    @classmethod
    def GetSuperUsers(cls):
        return cls._superUsers
    
    @classmethod
    def SetSuperUsers(cls, value):
        if type(value) == list:
            for uid in value:
                cls._superUsers.append(uid)
        else:
            cls._superUsers.append(value)
    
    def GetUser(self, user) -> User:
        uid = user.uid
        if uid not in self.users:
            self.users[uid] = user
        return self.users[uid]
    
    def GetUserById(self, uid) -> User:
        return None if uid not in self.users else self.users[uid]
    
    def SetAdmin(self, uid) -> bool:
        if uid not in self.users:
            return False
        self.users[uid]._isAdmin = True
        return True
    
    def UnsetAdmin(self, uid) -> bool:
        if uid not in self.users:
            return False
        self.users[uid]._isAdmin = False
        return True