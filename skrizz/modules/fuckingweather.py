"""
fuckingweather.py - Skrizz module for The Fucking Weather
Copyright 2013 Michael Yanovich
Copyright 2013 Edward Powell
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""
from skrizz import web
import re

def fucking_weather(skrizz, trigger):
    text = trigger.group(2)
    if not text:
        skrizz.reply("INVALID FUCKING PLACE. PLEASE ENTER A FUCKING ZIP CODE, OR A FUCKING CITY-STATE PAIR.")
        return
    text = web.quote(text)
    page = web.get("http://thefuckingweather.com/?where=%s" % (text))
    re_mark = re.compile('<p class="remark">(.*?)</p>')
    results = re_mark.findall(page)
    if results:
        skrizz.reply(results[0])
    else:
        skrizz.reply("I CAN'T GET THE FUCKING WEATHER.")
        return skrizz.NOLIMIT
fucking_weather.commands = ['fucking_weather', 'fw']
fucking_weather.rate = 30
fucking_weather.priority = 'low'
