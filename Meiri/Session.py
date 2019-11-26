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
        self.stype = stype
        self.handle = handle
        self.plugins = {name: True for name in Command.PLUGINS}
        self.extra = None
        self.context = []
        self.args = []

    def InitUserManager(self, userManager):
        self.userManager = userManager

    async def Execute(self, sender, message):
        sender = self.userManager.GetUser(sender)
        await self.Parse(message)
        if self.context:
            command = self.context[-1]
            await command.Execute(sender, self.args)
            if command.completed:
                self.context.pop()

    async def Parse(self, message):
        params = message.text.split(' ')
        if params and params[0].startswith(('.', '/', '-')):
            name = params[0][1:]
            if name == 'syscall':
                self.context.append(Command.GetCommand(name, self))
                self.args = params[1:]
                return
            elif not self.context and (name in Command.SYSTEM or name in self.plugins):
                if name in Command.SYSTEM or self.plugins[name]:
                    self.context.append(Command.GetCommand(name, self))
                    self.args = params[1:]
                else:
                    await self.Send(f'Plugin [{name}] was disabled. please enable it first.')
                return
        self.args = params

    async def Send(self, message, reciever=None):
        raise NotImplementedError