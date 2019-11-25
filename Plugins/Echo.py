# -*- coding: utf-8 -*-

from Meiri import Command

@Command('echo')
class Echo:
    async def Execute(self, sender, args):
        self.Parse(args)
        self.completed = True
        await self.session.Send(self.text)
    
    def Parse(self, args):
        self.text = ' '.join(args)
