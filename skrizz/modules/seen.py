# -*- coding: utf8 -*-
"""
seen.py - Skrizz Seen Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright 2012, Elad Alfassa <elad@fedoraproject.org>
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""

import time
import datetime
import pytz
from skrizz.tools import Ddict, Nick
from skrizz.module import command, rule, priority

seen_dict = Ddict(dict)


def get_user_time(skrizz, nick):
    tz = 'UTC'
    tformat = None
    if skrizz.db and nick in skrizz.db.preferences:
            tz = skrizz.db.preferences.get(nick, 'tz') or 'UTC'
            tformat = skrizz.db.preferences.get(nick, 'time_format')
    if tz not in pytz.all_timezones_set:
        tz = 'UTC'
    return (pytz.timezone(tz.strip()), tformat or '%Y-%m-%d %H:%M:%S %Z')


@command('seen')
def seen(skrizz, trigger):
    """Reports when and where the user was last seen."""
    if not trigger.group(2):
        skrizz.say(".seen <nick> - Reports when <nick> was last seen.")
        return
    nick = Nick(trigger.group(2).strip())
    if nick in seen_dict:
        timestamp = seen_dict[nick]['timestamp']
        channel = seen_dict[nick]['channel']
        message = seen_dict[nick]['message']

        tz, tformat = get_user_time(skrizz, trigger.nick)
        saw = datetime.datetime.fromtimestamp(timestamp, tz)
        timestamp = saw.strftime(tformat)

        msg = "I last saw %s at %s on %s, saying %s" % (nick, timestamp, channel, message)
        skrizz.say(str(trigger.nick) + ': ' + msg)
    else:
        skrizz.say("Sorry, I haven't seen %s around." % nick)


@rule('(.*)')
@priority('low')
def note(skrizz, trigger):
    if trigger.sender.startswith('#'):
        nick = Nick(trigger.nick)
        seen_dict[nick]['timestamp'] = time.time()
        seen_dict[nick]['channel'] = trigger.sender
        seen_dict[nick]['message'] = trigger
