# -*- coding: utf-8 -*-

from Meiri import Command

@Command('echo')
class Echo:
    def Execute(self, sender, args):
        self.Parse(args)
        self.session.Send(self.text)
        self.completed = True
    
    def Parse(self, args):
        self.text = ' '.join(args)
