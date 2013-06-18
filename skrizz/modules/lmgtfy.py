"""
lmgtfy.py - Skrizz Let me Google that for you module
Copyright 2013, Dimitri Molenaars http://tyrope.nl/
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""
from skrizz.module import commands

@commands('lmgtfy', 'lmgify', 'gify', 'gtfy')
def googleit(bot, trigger):
    """Let me just... google that for you."""
    #No input
    if not trigger.group(2):
        return bot.say('http://google.com/')
    bot.say('http://lmgtfy.com/?q=' + trigger.group(2).replace(' ', '+'))
