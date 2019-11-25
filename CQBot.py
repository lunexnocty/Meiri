# -*- coding: utf-8 -*-

from aiocqhttp import CQHttp

from Meiri import User, Session, SessionType, Message, UserManager
from Meiri import meiri, asyncfunction

CQBot = CQHttp(api_root='http://127.0.0.1:5700/', access_token='AmeyaMeiri', secret='AmeyaMeiri')

UserManager.SetSuperUsers('2692327749')

@CQBot.on_message()
async def handle_msg(context):
    sender = CQUser(context['sender']['user_id'], name=context['sender']['nickname'])
    session = CQSession(context)
    data = context['message']
    message = Message(data, sender=sender)
    meiri.Shell(session, message)

@CQBot.on_request('group', 'friend')
async def handle_request(context):
    return {'approve': True}

class CQUser(User):
    def __init__(self, uid, name='unknown', sex='female', age=17):
        super().__init__(uid, name)
        self.sex = sex
        self.age = age
    
class CQSession(Session):
    def __init__(self, kwargs):
        def GetMetaData(context):
            stype = kwargs.get('message_type')
            handle = None
            if stype == 'group':
                stype = SessionType.GROUP
                handle = kwargs.get('group_id')
            elif stype == 'discuss':
                stype = SessionType.GROUP
                handle = kwargs.get('discuss_id')
            elif stype == 'private':
                stype = SessionType.FRIEND
                handle = kwargs.get('user_id')
            return stype, handle

        stype, handle = GetMetaData(kwargs)
        super().__init__(stype, handle)
        self.extra = kwargs
    
    @asyncfunction
    def Send(self, message, reciever=None):
        at_user = False
        context = self.extra 
        if self.stype == SessionType.GROUP:
            if reciever:
                context['user_id'] = reciever.uid
                at_user = True
            context['message_type'] = 'group'
            context['group_id'] = self.handle
        elif self.stype == SessionType.FRIEND or self.stype == SessionType.TEMPORARY:
            context['message_type'] = 'private'
            context['user_id'] = self.handle
        import asyncio
        newLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(newLoop)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(CQBot.send(context, message=message, at_sender=at_user))
        loop.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1 or sys.argv[1] == 'start':
        meiri.Run()
        CQBot.run(host='127.0.0.1', port=8080)
    elif sys.argv[1] == 'stop':
        meiri.Stop()
    elif sys.argv[1] == 'restart':
        meiri.Stop()
        meiri.Run()