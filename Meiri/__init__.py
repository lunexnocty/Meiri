# -*- coding: utf-8 -*-

from Meiri.UserManager import UserManager, User
from Meiri.Session import Session, SessionType
from Meiri.Core.Command import Command
from Meiri.Message import Message

class Meiri:
    def __init__(self):
        self.sessions = {}
        self.route = {}
    
    def GetSession(self, session):
        sid = session.sid
        if sid in self.sessions:
            self.sessions[sid].extra = session.extra
        else:
            session.InitUserManager(UserManager())
            self.sessions[sid] = session
            if sid not in self.route:
                self.route[sid] = [sid]
        return self.sessions[sid]
    
    def OnMessage(self, session, sender, message):
        for sid in self.route[self.GetSession(session).sid]:
            self.sessions[sid].Execute(sender, message)
    
    def AddListening(self, sid, sids):
        from collections import Iterable
        if isinstance(sids, Iterable):
            for key in sids:
                if key not in self.route:
                    self.route[key] = [key]
                self.route[key].append(sid)
        elif isinstance(sids, Session):
            self.route[sids].append(sids)
    
    def RemoveListening(self, sid):
        self.route = {key: [ssid for ssid in self.route[key] if ssid != sid or key == sid] for key in self.route }


meiri = Meiri()

__all__ = [User, Session, SessionType, Message, Command, meiri]


from Meiri.Core.Bin import *