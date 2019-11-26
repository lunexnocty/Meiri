# -*- coding: utf-8 -*-

from Meiri import Command, meiri, SessionType

@Command('syscall', True)
class Syscall:
    async def Execute(self, sender, args):
        if args[0] in Command.SYSTEM:
            command = Command.GetCommand(args[0], self.session)
            sender.isAdmin = True
            await command.Execute(sender, args[1:])
            sender.isAdmin = False
            self.completed = command.completed
        else:
            await self.session.Send(f'Command {args[0]} not found.')
            self.completed = True