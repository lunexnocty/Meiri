# -*- coding: utf-8 -*-

from Meiri import Command, meiri, Session, SessionType
from datetime import date
from time import sleep
from random import randint, choice, shuffle
from enum import Enum, unique

@Command('incan')
class Incan:
    def __init__(self):
        self.status = IncanStatus.READY
        self.members = {}
        self.round = 0
        self.route = []
        self.deck = Deck()
        self.monsters = []
        self.artifact = 0
        self.temples = Deck('Temple')
        
        self.helpdoc = '指令列表: \n<start/run> 开始新的一轮\n<join> 加入游戏\n<go/back> 前进/撤退\n<next> 进入下一轮.\n<exit/quit> 退出'
        self.ruledoc = '规则介绍(不知道怎么简短的介绍，有人有想法可以私发给我.)'
        self.greeting = '欢迎用语，可以玩了.（感觉要改设定，谁想个故事背景我编进去？）'
        self.version = 'version 2.0.0'
        

    def GetOption(self, option):
        if option in ['begin']:
            return Option.GAMESTART
        elif option in ['version', '-v', '--version']:
            return Option.VERSION
        elif option in ['help', '-h', '--help']:
            return Option.HELP
        elif option in ['rule', 'document', 'doc']:
            return Option.RULE
        elif option in ['join']:
            return Option.JOINGAME
        elif option in ['go', 'forward']:
            return Option.FORWARD
        elif option in ['back', 'retreat', 'escape']:
            return Option.RETREAT
        elif option in ['next']:
            return Option.NEXTROUND
        elif option in ['status']:
            return Option.STATUS
        elif option in ['start', 'run']:
            return Option.ROUNDSTART
        elif option in ['exit', 'quit']:
            return Option.EXIT
        else:
            return None

    def InitPlayer(self, player):
        treasures = {
            'Turquoise': {
                'number': 0,
                'value': 1
            },
            'Obsidian': {
                'number': 0,
                'value': 5
            },
            'Gold': {
                'number': 0,
                'value': 10
            },
            'Artifact': {
                'number': 0,
                'value': 5
            }
        }
        from copy import deepcopy
        self.members[player.uid] = {
            'status': 0,
            'name': player.name,
            'treasures': treasures,
            'income': deepcopy(treasures)
        }

    def Execute(self, sender, args):
        self.Parse(args)
        if self.status == IncanStatus.READY:
            self.Ready(sender)
        elif self.status == IncanStatus.INQUEUE:
            self.InQueue(sender)
        elif self.status == IncanStatus.GAMING and sender.uid in self.members:
            self.Gaming(sender)
        elif self.status is IncanStatus.INTERVAL and sender.uid in self.members:
            self.Interval(sender)
    
    def Interval(self, sender):
        if self.option == Option.EXIT:
            self.session.Send('游戏结束~下次再见~')
            self.completed = True
        elif self.option == Option.HELP:
            self.session.Send(self.helpdoc)
        elif self.option == Option.RULE:
            self.session.Send(self.ruledoc)
        elif self.option == Option.VERSION:
            self.session.Send(self.version)
        elif self.option is Option.NEXTROUND:
            self.status = IncanStatus.GAMING
            self.session.Send(f'第{self.round+1}轮：{self.temples.Draw().name}')

    def InQueue(self, sender):
        if self.option == Option.EXIT:
            self.session.Send('游戏结束~下次再见~')
            self.completed = True
        elif self.option == Option.HELP:
            self.session.Send(self.helpdoc)
        elif self.option == Option.RULE:
            self.session.Send(self.ruledoc)
        elif self.option == Option.VERSION:
            self.session.Send(self.version)
        elif self.option == Option.JOINGAME:
            self.InitPlayer(sender)
            self.session.Send(f'<{sender.name}>加入了小队，当前小队共{len(self.members)}人。')
        elif self.option == Option.ROUNDSTART:
            self.status = IncanStatus.GAMING
            self.session.Send(f'第1轮：{self.temples.Draw().name}')
            meiri.AddListening(self.session.sid, [Session.GetSessionId(SessionType.FRIEND, uid) for uid in self.members])
        elif self.option == Option.STATUS:
            self.session.Send(self.GetTeamInfo())

    def Ready(self, sender):
        if self.option == Option.HELP:
            self.session.Send(self.helpdoc)
            self.completed = True
        elif self.option == Option.RULE:
            self.session.Send(self.ruledoc)
            self.completed = True
        elif self.option == Option.VERSION:
            self.session.Send(self.version)
            self.completed = True
        elif self.option == Option.GAMESTART:
            self.status = IncanStatus.INQUEUE
            self.InitPlayer(sender)
            self.session.Send(self.greeting)

    def Gaming(self,sender):
        if self.option == Option.FORWARD and self.members[sender.uid]['status'] == 0:
            self.members[sender.uid]['status'] = 1
        elif self.option == Option.RETREAT and self.members[sender.uid]['status'] == 0:
            self.members[sender.uid]['status'] = 2
        elif self.option == Option.STATUS:
            self.session.Send(self.GetGameStatus())

        if self.CheckTurnEnd():
            self.DoRetreat()
            for uid in self.members:
                if self.members[uid]['status'] == 1:
                    self.members[uid]['status'] = 0
                elif self.members[uid]['status'] == 2:
                    self.members[uid]['status'] = 3
            adventures = [uid for uid in self.members if self.members[uid]['status'] == 0]
            if adventures:
                card = self.deck.Draw()
                if card.ctype is Card.Type.MONSTER:
                    if card.name in self.monsters:
                        for uid in adventures:
                            for jewel in self.members[uid]['treasures'].values():
                                jewel['number'] = 0
                        self.session.Send(f'<{">, <".join([self.members[uid]["name"] for uid in adventures])}>被驱逐出神殿，一无所获.')
                        self.deck = Deck()
                        self.deck.Remove(card.name)
                        self.EnterNextRound()
                    else:
                        self.monsters.append(card.name)
                        self.session.Send(f'发现了来自<{card.name}>的警告.')
                elif card.ctype is Card.Type.JEWEL:
                    self.session.Send(f'发现了宝石<{card.name}>{card.number}枚')
                    num = len(adventures)
                    for uid in adventures:
                        self.members[uid]['treasures'][card.name]['number'] += card.number // num
                    card.number = card.number % num
                    self.route.append(card)
                elif card.ctype is Card.Type.ARTIFACT:
                    self.route.append(card)
                    self.session.Send(f'发现了遗物<{card.name}>.')
            else:
                self.deck = Deck()
                self.EnterNextRound()

    def EnterNextRound(self):
        self.monsters.clear()
        self.route.clear()
        for i in range(self.artifact):
            self.deck.DrawArtifact()
        for uid in self.members:
            self.members[uid]['status'] = 0
            for name in self.members[uid]['treasures']:
                self.members[uid]['income'][name]['number'] += self.members[uid]['treasures'][name]['number']
                self.members[uid]['treasures'][name]['number'] = 0
        self.round += 1
        if self.round == 5:
            self.Clearing()
        else:
            self.status = IncanStatus.INTERVAL
            self.session.Send('本轮冒险完成，是否进入下一座神殿？')

    def Clearing(self):
        winner = {'name': None, 'value': 0}
        for uid, member in self.members.items():
            income = 0
            for name, jewel in member['income'].items():
                income += jewel['number'] * jewel['value']
            if income > winner['value'] and income != 0:
                winner['name'] = member['name']
                winner['value'] = income
        self.session.Send(f'<{winner["name"]}>是最后的胜利者.')
        self.completed = True

    def DoRetreat(self):
        runaways = [uid for uid in self.members if self.members[uid]['status'] == 2]
        num = len(runaways)
        if num == 0:
            return
        for card in self.route:
            for uid in runaways:
                self.members[uid]['treasures'][card.name]['number'] += card.number // num
            if card.ctype is Card.Type.ARTIFACT and num == 1:
                self.artifact += 1
                if self.artifact > 2:
                    self.members[uid]['treasures'][card.name]['value'] = 10
            card.number = card.number % num
        self.session.Send(f'<{">, <".join([self.members[uid]["name"] for uid in runaways])}>放弃了冒险.')      

    def GetTeamInfo(self):
        return f'队伍玩家有：<{">, <".join([self.members[uid]["name"] for uid in self.members])}>'

    def GetGameStatus(self):
        status = '角色状态：'
        for uid in self.members:
            status += f'<{self.members[uid]["name"]}> {self.members[uid]["status"]}\n'
        if self.monsters:
            status += f'警告：\n<{">, <".join(self.monsters)}>'
        else:
            status += f'目前没有收到任何警告.'
        return status[:-1]

    def CheckTurnEnd(self):
        for uid in self.members:
            if self.members[uid]['status'] == 0:
                return False
        return True

    def Parse(self, args):
        option = args[0].lower() if args else 'begin'
        self.option = self.GetOption(option)


@unique
class IncanStatus(Enum):
    READY = 0,
    INQUEUE = 1,
    GAMING = 3,
    INTERVAL = 4,

@unique
class Option(Enum):
    FORWARD = 1,
    RETREAT = 2,
    STATUS = 3,
    VERSION = 4,
    RULE = 5,
    HELP = 6,
    GAMESTART = 7,
    ROUNDSTART = 8,
    JOINGAME = 9,
    NEXTROUND = 0,
    EXIT = 10

class Card:
    class Type(Enum):
        TEMPLE = 0,
        JEWEL = 1,
        MONSTER = 2,
        ARTIFACT = 3
        def ToString(self):
            if self is self.TEMPLE:
                return 'Temple'
            elif self is self.JEWEL:
                return 'Jewel'
            elif self is self.MONSTER:
                return 'Monster'
            elif self is self.ARTIFACT:
                return 'Artifact'
            else:
                raise ValueError

    def __init__(self, ctype, name=None, number=1, value=0):
        self.ctype = ctype
        self.name = name if name else ctype.ToString()
        self.number = number
        self.value = value

class Deck:
    def __init__(self, ctype='Quest'):
        self.cardset = []
        if ctype == 'Quest':
            for i in range(5):
                self.cardset.append(Card(Card.Type.JEWEL, 'Gold', number=randint(10, 15), value=10))
                self.cardset.append(Card(Card.Type.JEWEL, 'Obsidian', number=randint(10, 15), value=5))
                self.cardset.append(Card(Card.Type.JEWEL, 'Turquoise', number=randint(10, 15), value=1))
                self.cardset.append(Card(Card.Type.ARTIFACT, value=5))
            for i in range(3):
                self.cardset.append(Card(Card.Type.MONSTER, 'Viper'))
                self.cardset.append(Card(Card.Type.MONSTER, 'Spider'))
                self.cardset.append(Card(Card.Type.MONSTER, 'Mummy'))
                self.cardset.append(Card(Card.Type.MONSTER, 'Flame'))
                self.cardset.append(Card(Card.Type.MONSTER, 'Collapse'))
        elif ctype == 'Temple':
            self.cardset.append(Card(Card.Type.TEMPLE, '第一神殿'))
            self.cardset.append(Card(Card.Type.TEMPLE, '第二神殿'))
            self.cardset.append(Card(Card.Type.TEMPLE, '第三神殿'))
            self.cardset.append(Card(Card.Type.TEMPLE, '第四神殿'))
            self.cardset.append(Card(Card.Type.TEMPLE, '第五神殿'))
        shuffle(self.cardset)

    def Draw(self):
        card = choice(self.cardset)
        self.cardset.remove(card)
        return card
    
    def Remove(self, name):
        self.cardset = [card for card in self.cardset if card.name != name]
    
    def DrawArtifact(self):
        card = choice(self.cardset)
        while card.ctype is not Card.Type.ARTIFACT:
            card = choice(self.cardset)
        self.cardset.remove(card)
        return card

    def DrawJewel(self):
        card = choice(self.cardset)
        while card.ctype is not Card.Type.JEWEL:
            card = choice(self.cardset)
        self.cardset.remove(card)
        return card