"""
pushover.py - register a nick and do some notification shit
Copyright 2014, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""
import random
import time
import datetime
import re
import json
import requests
import skrizz.module

from distutils.version import StrictVersion 
from skrizz.tools import Nick

def setup(bot):
    if bot.db and not bot.db.preferences.has_columns('push_service'):
        bot.db.preferences.add_columns(['push_service'])
    if bot.db and not bot.db.preferences.has_columns('push_key'):
        bot.db.preferences.add_columns(['push_key'])
  
@skrizz.module.rule('.*')
@skrizz.module.priority('low')
def watch_chat(bot, trigger):
    do_nothing = True


def notify_pushbullet(key, channel, nick, message):
    """ extend this later to support specific devices and types of notifications """

    PUSH_URL = "https://api.pushbullet.com/api/pushes"
    JSON_HEADER = {'Content-Type': 'application/json'}

    api_key = key
    device = "all"
    push_type = "note"

    push_title = "IRC: " + channel + ", " + nick
    push_body = message

    headers = JSON_HEADER
    headers.update({"User-Agent": "ifttt2pushbullet.herokuapp.com"})

    data = {"type": push_type, "title": push_title, "body": push_body}
    files = {}

    data = json.dumps(data)

    return requests.post(PUSH_URL, data=data, headers=headers, files=files, auth=(api_key, ""))


@skrizz.module.command('setnotify')
@skrizz.module.example('.setnotify <service name: pushover|pushbullet|nma> <api_key>')
def set_notifications(bot, trigger):
    """Set your notification service."""
    valid_services = ['pushover', 'pushbullet', 'nma']
  
    command = trigger.group(2)
 
    if not command:
        return bot.reply("Please enter both a service and an api key.")

    try: 
        push_service, push_key = command.split(' ', 1)
    except ValueError:
        return bot.reply("Please enter both a service and an api key.")

    push_service = push_service.lower()
      
    if bot.db:

        if push_service in valid_services:
            bot.db.preferences.update(trigger.nick, {'push_service': push_service})
        else:
            return bot.reply("I'm sorry, %s is not a valid service." % (push_service))

        bot.db.preferences.update(trigger.nick, {'push_key': push_key})

        bot.reply("Sending confirmation in private message.  By the way if you didn't set this up in a private message you are dumb.") 
        bot.msg(trigger.nick, 'Notifications successfully set for Service: ' + push_service + ' and API Key: ' + push_key)
    else:
        bot.reply("I can't remember that; I don't have a database.")


@skrizz.module.command('notify')
@skrizz.module.example('.notify <nick> <message>')
def manual_notify(bot, trigger):
    """Send a notification to someone"""

    command = trigger.group(2)

    if not command:
        return bot.reply("Please enter both a service and an api key.")

    try:
        notify_to, message = command.split(' ', 1)
    except ValueError:
        return bot.reply("Please enter both a service and an api key.")


    notify_from_nick = trigger.nick
    notify_from_chan = trigger.sender

    if bot.db and notify_to in bot.db.preferences:
        api_key = bot.db.preferences.get(notify_to, 'push_key')
        push_service = bot.db.preferences.get(notify_to, 'push_service')
        if not api_key:
            return bot.reply("The user " + notify_to + " is not set up to recieve notifications!")
 
        if push_service == "pushbullet":    
            notify = notify_pushbullet(api_key, notify_from_chan, notify_from_nick, message);
        elif push_service == "pushover":
            notify = False
        elif push_service == "nma":
            notify = False
        else:
            return bot.reply("No valid push service was found for the user.")

        if notify and notify.status_code == 200:
            return bot.reply("Message sent successfully!")
        elif notify == False:
            return bot.reply("I am not yet set up to notify using the " + push_service + " service specified by the user.")
        else:
            return bot.reply("Something went wrong, status code = " + str(notify.status_code))
    else:
        return bot.reply("The user " + notify_to + " is not set up to recieve notifications!")


if __name__ == '__main__':
    print __doc__.strip()
