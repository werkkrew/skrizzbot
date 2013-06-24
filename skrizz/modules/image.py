"""
image.py - Skrizz Module to query some reverse image search engines i
and attempt to describe images posted in chat in words.

Author: Bryan Chain - bryanchain.com

This module will transcribe links posted from quickmeme.com into a description of the meme.
"""

from skrizz.module import command, rule, example, NOLIMIT
import re
import urllib2
import json
import sys
import os


image_url = r'(https?:\/\/(?:[a-z0-9\-]+\.)+[a-z0-9]{2,6}(?:\/[^\/#?]+)+\.(?:jpe?g|gif|png))'

google_sbi_url = 'https://www.google.com/searchbyimage?&image_url='
karmadecay_search_url = 'http://karmadecay.com/search?kdtoolver=b1&q='
tineye_search_url = ''

test_img = 'http://i.imgur.com/TTb0GsE.jpg'

headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.16 Safari/534.24"}

def setup(bot):
    image_regex = re.compile(image_url)
    if not bot.memory.contains('url_callbacks'):
        bot.memory['url_callbacks'] = {}
    bot.memory['url_callbacks'][image_regex] = image_info


@rule('.*%s.*' % image_url)
def image_info(bot, trigger, match=None):
    match = match or trigger
    image = match.group(1)

    result = karmadecay_search(bot, image)
    if result:
        message = result
    else:
        message = '[IMAGE] That image must be really unique, it is indescribable!'

    bot.say(message)


def karmadecay_search(bot, image_url):
    karmadecay_query = karmadecay_search_url + image_url
    request = urllib2.Request(karmadecay_query,None,headers)
    try:
        file = urllib2.urlopen(request)
    except urllib2.URLError, e:
        error = '[IMAGE] Error: ' + e + 'URL: ' + match.group(1)
        bot.say(error)
        return
    else:
        data = file.read()
        best_guess = re.search(r'\[(.*?)\]\(', data)
        file.close()
        if best_guess:
            guess = best_guess.group(1)
        else:
            return

        if guess:
            message = '[IMAGE] I can best describe this image as: ' + guess + ' [URL] ' + karmadecay_query
            return message
 
