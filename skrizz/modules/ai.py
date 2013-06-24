"""
ai.py - Artificial Intelligence Module
Copyright 2009-2011, Michael Yanovich, yanovich.net
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""
import random
import time

random.seed()
limit = 3


def goodbye(skrizz, trigger):
    byemsg = random.choice(('Bye', 'Goodbye', 'Seeya', 'Auf Wiedersehen', 'Au revoir', 'Ttyl'))
    punctuation = random.choice(('!', ' '))
    skrizz.say(byemsg + ' ' + trigger.nick + punctuation)
goodbye.rule = r'(?i)$nickname\:\s+(bye|goodbye|seeya|cya|ttyl|g2g|gnight|goodnight)'
goodbye.thread = False
goodbye.rate = 30


def ty(skrizz, trigger):
    human = random.uniform(0, 9)
    time.sleep(human)
    mystr = trigger.group()
    mystr = str(mystr)
    if (mystr.find(" no ") == -1) and (mystr.find("no ") == -1) and (mystr.find(" no") == -1):
        skrizz.reply("You're welcome.")
ty.rule = '(?i).*(thank).*(you).*(skrizz|$nickname).*$'
ty.priority = 'high'
ty.rate = 30


def ty2(skrizz, trigger):
    ty(skrizz, trigger)
ty2.rule = '(?i)$nickname\:\s+(thank).*(you).*'
ty2.rate = 30


def ty4(skrizz, trigger):
    ty(skrizz, trigger)
ty4.rule = '(?i).*(thanks).*(skrizz|$nickname).*'
ty4.rate = 40


def yesno(skrizz, trigger):
    rand = random.uniform(0, 5)
    text = trigger.group()
    text = text.split(":")
    text = text[1].split()
    time.sleep(rand)
    if text[0] == 'yes':
        skrizz.reply("no")
    elif text[0] == 'no':
        skrizz.reply("yes")
yesno.rule = '(skrizz|$nickname)\:\s+(yes|no)$'
yesno.rate = 15


def ping_reply(skrizz, trigger):
    text = trigger.group().split(":")
    text = text[1].split()
    if text[0] == 'PING' or text[0] == 'ping':
        skrizz.reply("PONG")
ping_reply.rule = '(?i)($nickname|skrizz)\:\s+(ping)\s*'
ping_reply.rate = 30


def love(skrizz, trigger):
    skrizz.reply("I love you too.")
love.rule = '(?i)i.*love.*(skrizz|$nickname).*'
love.rate = 30


def love2(skrizz, trigger):
    skrizz.reply("I love you too.")
love2.rule = '(?i)(skrizz|$nickname)\:\si.*love.*'
love2.rate = 30


def love3(skrizz, trigger):
    skrizz.reply("I love you too.")
love3.rule = '(?i)(skrizz|$nickname)\,\si.*love.*'
love3.rate = 30


def f_lol(skrizz, trigger):
    randnum = random.random()
    if 0 < randnum < limit:
        respond = ['haha', 'lol', 'rofl']
        randtime = random.uniform(0, 9)
        time.sleep(randtime)
        skrizz.say(random.choice(respond))
f_lol.rule = '(haha!?|lol!?)$'
f_lol.priority = 'high'


def f_bye(skrizz, trigger):
    respond = ['bye!', 'bye', 'see ya', 'see ya!']
    skrizz.say(random.choice(respond))
f_bye.rule = '(g2g!?|bye!?)$'
f_bye.priority = 'high'


def f_heh(skrizz, trigger):
    randnum = random.random()
    if 0 < randnum < limit:
        respond = ['hm']
        randtime = random.uniform(0, 7)
        time.sleep(randtime)
        skrizz.say(random.choice(respond))
f_heh.rule = '(heh!?)$'
f_heh.priority = 'high'


def f_really(skrizz, trigger):
    randtime = random.uniform(10, 45)
    time.sleep(randtime)
    skrizz.say(str(trigger.nick) + ": " + "Yes, really.")
f_really.rule = r'(?i)$nickname\:\s+(really!?)'
f_really.priority = 'high'

def f_friday(skrizz, trigger):
    randtime = random.uniform(0, 7)
    time.sleep(randtime)
    skrizz.say("Time to get drunk!")
f_friday.rule = '(?i).*friday.*'
f_friday.priority = 'high'

def wb(skrizz, trigger):
    skrizz.reply("Thank you!")
wb.rule = '^(wb|welcome\sback).*$nickname\s'

if __name__ == '__main__':
    print __doc__.strip()
