# -*- coding: utf-8 -*-

from Meiri import Command

@Command('set')
class Set:
    async def Execute(self, sender, args):
        self.Parse(args)
        if self.option == 'name':
            await self.session.Send(f'已将{sender.name}的名字变更为{self.value}')
            sender.SetName(self.value)
        self.completed = True
    
    def Parse(self, args):
        self.option = args[0] if args else None
        self.value = args[1] if len(args) > 1 else None
        