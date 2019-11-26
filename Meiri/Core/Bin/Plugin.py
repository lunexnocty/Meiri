# -*- coding: utf-8 -*-

from Meiri import Command, meiri, SessionType
from enum import Enum, unique

@Command('plugin', True)
class Plugin:
    @unique
    class Option(Enum):
        ENABLE = 1
        DISABLE = 2
        STATUS = 3
        HELP = 4
    
    def __init__(self):
        self.option = None
        self.plugin = None
        self.helpdoc = '[on] 启用插件\n[off] 禁用插件\n[status] 查看插件状态'
    
    async def Execute(self, sender, args):
        if sender.Authority():
            self.Parse(args)
            if self.option is self.Option.ENABLE:
                if self.plugin in self.session.plugins:
                    self.session.plugins[self.plugin] = True
                    await self.session.Send(f'插件[{self.plugin}]已启用')
                else:
                    await self.session.Send(f'Plugin [{self.plugin}] not found.')
            elif self.option is self.Option.DISABLE:
                if self.plugin in self.session.plugins:
                    self.session.plugins[self.plugin] = False
                    await self.session.Send(f'插件[{self.plugin}]已禁用')
                else:
                    await self.session.Send(f'Plugin [{self.plugin}] not found.')
            elif self.option is self.Option.STATUS:
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
        elif args[0] in ['on', 'enable']:
            self.option = self.Option.ENABLE
            self.plugin = args[1] if len(args) > 1 else None
        elif args[0] in ['off', 'disable']:
            self.option = self.Option.DISABLE
            self.plugin = args[1] if len(args) > 1 else None
        elif args[0] in ['status']:
            self.option = self.Option.STATUS
        elif args[0] in ['help', '-h', '--help']:
            self.option = self.Option.HELP
        else:
            self.Option = None
