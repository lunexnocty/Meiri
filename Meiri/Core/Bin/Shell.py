# -*- coding: utf-8 -*-

from Meiri import Command, meiri, SessionType
from enum import Enum, unique

@Command('shell', True)
class Shell:
    @unique
    class Option(Enum):
        RESTART = 1
        STATUS = 2
        PLUGINS = 3
        HELP = 4

    def __init__(self):
        self.option = None
        self.helpdoc = 'restart\t重启会话\nstatus\t查看会话状态\nplugins\t查看插件列表'

    async def Execute(self, sender, args):
        if sender.Authority():
            self.Parse(args)
            if self.option is self.Option.RESTART:
                while len(self.session.context) > 1:
                    self.session.context.pop(0)
                await self.session.Send('重启成功.')
            elif self.option is self.Option.STATUS:
                if len(self.session.context) > 1:
                    await self.session.Send(f'当前所运行的插件有: [{"], [".join([cmd.GetName() for cmd in self.session.context[:-1]])}]')
                else:
                    await self.session.Send('当前无插件运行.')
            elif self.option is self.Option.PLUGINS:
                plugins = '插件列表:\n'
                for name in self.session.plugins:
                    plugins += f'{name}: '
                    if self.session.plugins[name]:
                        plugins += 'enabled\n'
                    else:
                        plugins += 'disabled\n'
                await self.session.Send(plugins)
            elif self.option is self.Option.HELP:
                await self.session.Send(self.helpdoc)
            else:
                await self.session.Send('无法识别的指令')
        else:
            await self.session.Send('权限不足')    
        self.completed = True

    def Parse(self, args):
        if not args:
            self.option = self.Option.HELP
        elif args[0] in ['restart']:
            self.option = self.Option.RESTART
        elif args[0] in ['status']:
            self.option = self.Option.STATUS
        elif args[0] in ['plugins']:
            self.option = self.Option.PLUGINS
        elif args[0] in ['help', '-h', '--help']:
            self.option = self.Option.HELP
        else:
            self.Option = None