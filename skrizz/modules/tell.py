"""
tell.py - Skrizz Tell and Ask Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""

import os
import re
import time
import datetime
import pytz
import random
import threading
from skrizz.tools import Nick

maximum = 4

def loadReminders(fn, lock):
    lock.acquire()
    try:
        result = {}
        f = open(fn)
        for line in f:
            line = line.strip()
            if line:
                try: tellee, teller, verb, timenow, msg = line.split('\t', 4)
                except ValueError: continue # @@ hmm
                result.setdefault(tellee, []).append((teller, verb, timenow, msg))
        f.close()
    finally:
        lock.release()
    return result

def dumpReminders(fn, data, lock):
    lock.acquire()
    try:
        f = open(fn, 'w')
        for tellee in data.iterkeys():
            for remindon in data[tellee]:
                line = '\t'.join((tellee,) + remindon)
                try: f.write((line + '\n').encode('utf-8'))
                except IOError: break
        try: f.close()
        except IOError: pass
    finally:
        lock.release()
    return True

def setup(self):
    fn = self.nick + '-' + self.config.host + '.tell.db'
    self.tell_filename = os.path.join(self.config.dotdir, fn)
    if not os.path.exists(self.tell_filename):
        try: f = open(self.tell_filename, 'w')
        except OSError: pass
        else:
            f.write('')
            f.close()
    self.memory['tell_lock'] = threading.Lock()
    self.memory['reminders'] = loadReminders(self.tell_filename, self.memory['tell_lock'])


def get_user_time(skrizz, nick):
    tz = 'UTC'
    tformat = None
    if skrizz.db and nick in skrizz.db.preferences:
            tz = skrizz.db.preferences.get(nick, 'tz') or 'UTC'
            tformat = skrizz.db.preferences.get(nick, 'time_format')
    if tz not in pytz.all_timezones_set:
        tz = 'UTC'
    return (pytz.timezone(tz.strip()), tformat or '%Y-%m-%d %H:%M:%S %Z')


def f_remind(skrizz, trigger):
    teller = trigger.nick

    verb, tellee, msg = trigger.groups()
    verb = unicode(verb)
    tellee = Nick(tellee.rstrip('.,:;'))
    msg = unicode(msg)

    if not os.path.exists(skrizz.tell_filename):
        return

    if len(tellee) > 20:
        return skrizz.reply('That nickname is too long.')
    if tellee == skrizz.nick:
        return skrizz.reply("I'm here now, you can tell me whatever you want!")
    
    tz, tformat = get_user_time(skrizz, tellee)
    print tellee, tz, tformat
    timenow = datetime.datetime.now(tz).strftime(tformat)
    if not tellee in (Nick(teller), skrizz.nick, 'me'):
        skrizz.memory['tell_lock'].acquire()
        try:
            if not skrizz.memory['reminders'].has_key(tellee):
                skrizz.memory['reminders'][tellee] = [(teller, verb, timenow, msg)]
            else:
                skrizz.memory['reminders'][tellee].append((teller, verb, timenow, msg))
        finally:
            skrizz.memory['tell_lock'].release()

        response = "I'll pass that on when %s is around." % tellee

        skrizz.reply(response)
    elif Nick(teller) == tellee:
        skrizz.say('You can %s yourself that.' % verb)
    else: skrizz.say("Hey, I'm not as stupid as Monty you know!")

    dumpReminders(skrizz.tell_filename, skrizz.memory['reminders'], skrizz.memory['tell_lock']) # @@ tell
f_remind.rule = ('$nick', ['tell', 'ask'], r'(\S+) (.*)')

def getReminders(skrizz, channel, key, tellee):
    lines = []
    template = "%s: %s <%s> %s %s %s"
    today = time.strftime('%d %b', time.gmtime())

    skrizz.memory['tell_lock'].acquire()
    try:
        for (teller, verb, datetime, msg) in skrizz.memory['reminders'][key]:
            if datetime.startswith(today):
                datetime = datetime[len(today)+1:]
            lines.append(template % (tellee, datetime, teller, verb, tellee, msg))

        try: del skrizz.memory['reminders'][key]
        except KeyError: skrizz.msg(channel, 'Er...')
    finally:
        skrizz.memory['tell_lock'].release()
    return lines

def message(skrizz, trigger):

    tellee = trigger.nick
    channel = trigger.sender

    if not os.path.exists(skrizz.tell_filename):
        return

    reminders = []
    remkeys = list(reversed(sorted(skrizz.memory['reminders'].keys())))

    for remkey in remkeys:
        if not remkey.endswith('*') or remkey.endswith(':'):
            if tellee == remkey:
                reminders.extend(getReminders(skrizz, channel, remkey, tellee))
        elif tellee.startswith(remkey.rstrip('*:')):
            reminders.extend(getReminders(skrizz, channel, remkey, tellee))

    for line in reminders[:maximum]:
        skrizz.say(line)

    if reminders[maximum:]:
        skrizz.say('Further messages sent privately')
        for line in reminders[maximum:]:
            skrizz.msg(tellee, line)

    if len(skrizz.memory['reminders'].keys()) != remkeys:
        dumpReminders(skrizz.tell_filename, skrizz.memory['reminders'], skrizz.memory['tell_lock']) # @@ tell
message.rule = r'(.*)'
message.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()
