# -*- coding: utf8 -*-
"""
announce.py - Send a message to all channels
Copyright 2013, Elad Alfassa, <elad@fedoraproject.org>
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""
from skrizz.module import command, example

@command('announce')
@example('.announce Some important message here')
def announce(bot, trigger):
    """
    Send an announcement to all channels the bot is in
    """
    if not trigger.admin:
        bot.reply('Sorry, I can\'t let you do that')
        return
    for channel in bot.channels:
        bot.msg(channel, '[ANNOUNCMENT] %s' % trigger.group(2))
