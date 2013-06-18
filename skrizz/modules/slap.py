"""
slap.py - Slap Module
Copyright 2009, Michael Yanovich, yanovich.net
Copyright 2013, Bryan Chain, http://www.bryanchain.com

"""

import random
from skrizz.module import commands


@commands('slap', 'slaps')
def slap(skrizz, trigger):
    """.slap <target> - Slaps <target>"""
    text = trigger.group().split()
    if len(text) < 2 or text[1].startswith('#'):
        return
    if text[1] == skrizz.nick:
        if (trigger.nick not in skrizz.config.admins):
            text[1] = trigger.nick
        else:
            text[1] = 'itself'
    if text[1] in skrizz.config.admins:
        if (trigger.nick not in skrizz.config.admins):
            text[1] = trigger.nick
    verb = random.choice(('slaps', 'kicks', 'destroys', 'annihilates', 'punches', 'roundhouse kicks', 'pwns', 'owns'))
    skrizz.write(['PRIVMSG', trigger.sender, ' :\x01ACTION', verb, text[1], '\x01'])
