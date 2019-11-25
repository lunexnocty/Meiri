# -*- coding: utf-8 -*-

from Meiri import Command, meiri, SessionType
from time import sleep

@Command('notice', True)
class Notice:
    async def Execute(self, sender, args):
        if sender.AuthorityCheck():
            self.Parse(args)
            for session in meiri.sessions.values():
                if session.stype == SessionType.GROUP:
                    await session.Send(self.text)
                    sleep(2)
        else:
            await self.session.Send('权限不足')
        self.completed = True
    
    def Parse(self, args):
        self.text = ' '.join(args)