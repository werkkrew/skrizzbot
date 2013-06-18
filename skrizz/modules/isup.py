"""
isup.py - Simple website status check with isup.me
Author: Edward Powell http://embolalia.net
Copyright 2013, Bryan Chain, http://www.bryanchain.com

This allows users to check if a website is up through isup.me.
"""

import skrizz.web as web
import re

def isup(skrizz, trigger):
    """isup.me website status checker"""
    site = trigger.group(2)
    if not site:
        return skrizz.reply("What site do you want to check?")

    if site[:6] != 'http://' and site[:7] != 'https://':
        if '://' in site:
            protocol = site.split('://')[0] + '://'
            return skrizz.reply("Try it again without the %s" % protocol)
        else:
            site = 'http://' + site
    try:
        response = web.get(site)
    except Exception as e:
        skrizz.say(site + ' looks down from here.')
        return

    if response:
        skrizz.say(site + ' looks fine to me.')
    else:
        skrizz.say(site + ' is down from here.')
isup.commands = ['isup']
