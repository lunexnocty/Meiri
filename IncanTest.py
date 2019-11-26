# -*- coding: utf-8 -*-

from Meiri import User, Session, SessionType, Message, UserManager, meiri
from Plugins import *

UserManager.SetSuperUsers('lunex')

async def onMessage(args):
    session = MySession('G@0')
    sender = MyUser(args[0])
    message = Message(args[1])
    await meiri.OnMessage(session, sender, message)

class MyUser(User):
    def __init__(self, userstr):
        user = userstr.split('#')
        uid = user[0]
        name = user[1] if len(user) > 1 else uid
        super().__init__(uid, name)
    
class MySession(Session):
    def __init__(self, sid):
        def GetMetaData(sid):     
            stype = None
            handle = None
            if 'G' in sid:
                stype = SessionType.GROUP
            elif 'F' in sid:
                stype = SessionType.FRIEND
            elif 'T' in sid:
                stype = SessionType.TEMPORARY
            handle = sid.split('@')[1]
            return stype, handle
        stype, handle = GetMetaData(sid)
        super().__init__(stype, handle)
    
    async def Send(self, message, reciever=None):
        print(f'{self.sid}:', message)

'''机器人逻辑本地测试脚本：
输入至少包括三项：
    第一项为Session信息，格式为：stype@sid, stype有'G', 'F', 'T'，sid为任意标识符
    第二项为发送者的用户信息，格式为：uid#name, uid为任意标识符，name为用户的名字(可为空)
    第三项为正式发送的内容
如果觉得控制台输入很麻烦，可以从文件读取输入，自行更改下面的代码即可
Eg：
    $ G@10001 123456#lunex -echo Hello, Ameya, Meiri!
'''


async def main():
    ins = input('> ')
    while(ins != 'quit'):
        await onMessage(ins.split(' ', 1))
        ins = input('> ')

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()