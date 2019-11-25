# -*- coding: utf-8 -*-

from enum import Enum, unique
from Meiri.Core.Command import Command

@unique
class SessionType(Enum):
    TEMPORARY = 0
    FRIEND = 1
    GROUP = 2

class Session:
    sid = None
    context = None

    @staticmethod
    def GetSessionId(stype, handle):
        sids = {
            SessionType.TEMPORARY: 'Temporary@',
            SessionType.FRIEND: 'Friend@',
            SessionType.GROUP: 'Group@'
        }
        if stype in sids:
            return sids[stype] + str(handle)
        return 'Unknown@' + str(handle)

    def __init__(self, stype, handle):
        self.sid = self.GetSessionId(stype, handle)
        self.plugins = {name: True for name in Command.PLUGINS}
        self.extra = None
        self.command = None
        self.enabled = True
        self.args = []

    def InitUserManager(self, userManager):
        self.userManager = userManager

    async def Execute(self, sender, message):
        sender = self.userManager.GetUser(sender)
        if self.command:
            await self.command.Execute(sender, message.text.split(' '))
            if self.command.completed:
                self.command = None
        else:
            self.Parse(message)
            if self.command:
                name = self.command.GetName()
                if name in Command.SYSTEM or self.plugins[self.command.GetName()]:
                    await self.command.Execute(sender, self.args)
                    if self.command.completed:
                        self.command = None
                else:
                    await self.Send(f'Plugin <{self.command}> disabled. please enable it first.')
    
    def Parse(self, message):
        params = message.text.split(' ')
        if params and params[0].startswith(('.', '/', '-')):
            name = params[0][1:]
            if name in Command.SYSTEM or name in Command.PLUGINS:
                self.command = Command.GetCommand(name, self)
                self.args = params[1:]

    async def Send(self, message, reciever=None):
        raise NotImplementedError