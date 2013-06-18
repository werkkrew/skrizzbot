"""
version.py - Skrizz Version Module
Copyright 2009, Silas Baronda
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""

from datetime import datetime
from subprocess import *
import skrizz


def git_info():
    p = Popen(["git", "log", "-n 1"], stdout=PIPE, close_fds=True)

    commit = p.stdout.readline()
    author = p.stdout.readline()
    date = p.stdout.readline()
    return commit, author, date


@skrizz.module.command('version')
def version(bot, trigger):
    """Display the latest commit version, if Skrizz is running in a git repo."""
    commit, author, date = git_info()

    if not commit.strip():
        bot.reply("Skrizz v. " + skrizz.__version__)
        return

    bot.say(str(trigger.nick) + ": Skrizz v. %s at commit:" % skrizz.__version__)
    bot.say("  " + commit)
    bot.say("  " + author)
    bot.say("  " + date)


@skrizz.module.rule('\x01VERSION\x01')
@skrizz.module.rate(20)
def ctcp_version(bot, trigger):
    bot.write(('NOTICE', trigger.nick),
              '\x01VERSION Skrizz IRC Bot version %s\x01' % skrizz.__version__)


@skrizz.module.rule('\x01SOURCE\x01')
@skrizz.module.rate(20)
def ctcp_source(bot, trigger):
    bot.write(('NOTICE', trigger.nick),
              '\x01SOURCE https://github.com/Embolalia/skrizz/\x01')


@skrizz.module.rule('\x01PING\s(.*)\x01')
@skrizz.module.rate(10)
def ctcp_ping(bot, trigger):
    text = trigger.group()
    text = text.replace("PING ", "")
    text = text.replace("\x01", "")
    bot.write(('NOTICE', trigger.nick),
              '\x01PING {0}\x01'.format(text))


@skrizz.module.rule('\x01TIME\x01')
@skrizz.module.rate(20)
def ctcp_time(bot, trigger):
    dt = datetime.now()
    current_time = dt.strftime("%A, %d. %B %Y %I:%M%p")
    bot.write(('NOTICE', trigger.nick),
              '\x01TIME {0}\x01'.format(current_time))
