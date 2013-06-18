"""
meme-transcribe.py - Skrizz Module to Transcribe Memelinks
Author: Bryan Chain - bryanchain.com

This module will transcribe links posted from quickmeme.com into a description of the meme.
"""

from skrizz.module import command, rule, example, NOLIMIT
import re
import urllib2
import json
import sys
import os

domain = r'https?://(?:www\.|np\.)?quickmeme\.com'
meme_url = '(%s/meme/[\w-]+)' % domain


def setup(bot):
    meme_regex = re.compile(meme_url)
    if not bot.memory.contains('url_callbacks'):
        bot.memory['url_callbacks'] = {}
    bot.memory['url_callbacks'][meme_regex] = meme_info


@rule('.*%s.*' % meme_url)
def meme_info(bot, trigger, match=None):
    match = match or trigger
    try:
        file = urllib2.urlopen(match.group(1))
    except urllib2.URLError:
        message = '[MEME] Invalid URL'
    else:
        data = file.read()
        meme_name = re.search(r'<title>(.*?)-', data)
        meme_data = re.search(r'data-id="(.*?)"', data)
        if meme_name and meme_data:
            meme_id = meme_data.group(1)
            meme_ti = meme_name.group(1)
        else:
            meme_id = 0
        file.close()

        if meme_id:
            file = urllib2.urlopen("http://www.quickmeme.com/make/get_data/?id="+meme_id)
            meme_json = file.read()
            qm_json = json.loads(meme_json)
            qm_json = qm_json["caps"]
            jsondataCap = []
            for key in qm_json:
                jsondataCap.append(key["txt"])
            meme_top = jsondataCap[0].upper()
            meme_bottom = jsondataCap[1].upper()
            message = '[MEME] Meme Name: ' + meme_ti + '| Top: ' + meme_top + ' | Bottom: ' + meme_bottom
        else:
            message = '[MEME] Not Found :('
        file.close()

    bot.say(message)
