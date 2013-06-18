"""
info.py - Skrizz Information Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""
from skrizz.module import command, rule, example, priority

@rule('$nick' '(?i)(help|doc) +([A-Za-z]+)(?:\?+)?$')
@example('$nickname: help tell')
@priority('low')
def doc(bot, trigger):
    """Shows a command's documentation, and possibly an example."""
    name = trigger.group(2)
    name = name.lower()

    if bot.doc.has_key(name):
        bot.reply(bot.doc[name][0])
        if bot.doc[name][1]:
            bot.say('e.g. ' + bot.doc[name][1])
	    
@command('help')
@example('.help c')
def help(bot, trigger):
    """Get help for a command."""
    if not trigger.group(2):
	bot.reply('Say .help <command> (for example .help c) to get help for a command, or .commands for a list of commands.')
    else:
	doc(bot, trigger)

@command('commands')
@priority('low')
def commands(bot, trigger):
    """Return a list of bot's commands"""
    names = ', '.join(sorted(bot.doc.iterkeys()))
    bot.reply("I am sending you a private message of all my commands!")
    bot.msg(trigger.nick, 'Commands I recognise: ' + names + '.')
    bot.msg(trigger.nick, ("For help, do '%s: help example' where example is the " +
                    "name of the command you want help for.") % bot.nick)

@rule('$nick' r'(?i)help(?:[?!]+)?$')
@priority('low')
def help2(bot, trigger):
    response = (
        'Hi, I\'m a bot. Say ".commands" to me in private for a list ' +
        'of my commands, or see http://skrizz.dftba.net for more ' +
        'general details. My owner is %s.'
    ) % bot.config.owner
    bot.reply(response)


if __name__ == '__main__':
    print __doc__.strip()
