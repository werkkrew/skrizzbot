"""
tumblr.py - Skrizz Tumblr Module
Copyright 2013, Bryan Chain, http://www.bryanchain.com

This module allows you to post things to tumblr either
on an account in the name of the bot or on a per-user basis (in development)

As of right now it only supports image and video posts.
Video embed links are only vimeo and youtube at the moment.

Licensed under the Eiffel Forum License 2.
"""
import tumblpy
from tumblpy import Tumblpy
import time
import re
from skrizz.tools import Nick

def configure(config):
    """
    These values are all found by signing up your bot at the tumblr developer site
    For posting to a tumblr the bot owns you need the (access_token, access_token_secret) fields
    For allowing the bot to post on other users' behalf you need the (consumer_key, consumer_secret ) fields
    
    | [tumblr] | example | purpose |
    | --------- | ------- | ------- |
    | consumer_key | 09d8c7b0987cAQc7fge09 | OAuth consumer key |
    | consumer_secret | LIaso6873jI8Yasdlfi76awer76yhasdfi75h6TFJgf | OAuth consumer secret |
    | access_token | 564018348-Alldf7s6598d76tgsadfo9asdf56uUf65aVgdsf6 | OAuth access token |
    | access_token_secret | asdfl7698596KIKJVGvJDcfcvcsfdy85hfddlku67 | OAuth access token secret |
    """
    
    if config.option('Configure Tumblr? (You will need to register on http://www.tumblr.com/oauth/apps', False):
        config.interactive_add('tumblr', 'consumer_key', 'Consumer key')
        config.interactive_add('tumblr', 'consumer_secret', 'Consumer secret')
        config.interactive_add('tumblr', 'access_token', 'Access token')
        config.interactive_add('tumblr', 'access_token_secret', 'Access token secret')

def setup(skrizz):
    global consumer_key, consumer_secret, access_token, access_token_secret
    consumer_key = skrizz.config.tumblr.consumer_key
    consumer_secret = skrizz.config.tumblr.consumer_secret
    access_token = skrizz.config.tumblr.access_token
    access_token_secret = skrizz.config.tumblr.access_token_secret



def format_thousands(integer):
    """Returns string of integer, with thousands separated by ','"""
    return re.sub(r'(\d{3})(?=\d)', r'\1,', str(integer)[::-1])[::-1]

def build_post(post_content):
    matcher = re.compile(r'(?u)((?:http|https|ftp)(?:://\S+)) (.*)')
    image_url = re.compile(r'(https?:\/\/(?:[a-z0-9\-]+\.)+[a-z0-9]{2,6}(?:\/[^\/#?]+)+\.(?:jpe?g|gif|png))')
    youtube_url = re.compile(r'.*(youtube.com/watch\S*v=|youtu.be/)([\w-]+)')
    vimeo_url = re.compile(r'.*(vimeo\.com/(\w*/)*(([a-z]{0,2}-)?\d+))')

    post = re.match(matcher, post_content)
    if post is not None:
        post_url = post.group(1)
        post_caption = post.group(2)
    else: 
        return 0

	"""detect the type of post"""
    image = re.match(image_url, post_url)
    youtube = re.match(youtube_url, post_url)
    vimeo = re.match(vimeo_url, post_url)

    if image is not None:
        return {'type': 'photo', 'link': post_url, 'source': post_url, 'caption': post_caption}, {'url': post_url, 'caption': post_caption}
    elif youtube is not None:
        video_id = youtube.group(2)
        post_embed = '<iframe width="640" height="360" src="http://www.youtube.com/embed/' + video_id + '?feature=player_embedded" frameborder="0" allowfullscreen></iframe>'
        return {'type': 'video', 'caption': post_caption, 'embed': post_embed}, {'url': post_url, 'caption': post_caption}
    elif vimeo is not None:
        video_id = vimeo.group(3)
        post_embed = '<iframe src="http://player.vimeo.com/video/' + video_id + '" width="400" height="300" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>'
        return {'type': 'video', 'caption': post_caption, 'embed': post_embed}, {'url': post_url, 'caption': post_caption}
    else:
        return {'type': 'link', 'url': post_url, 'description': post_caption}, {'url': post_url, 'caption': post_caption}

def f_post(skrizz, trigger):
    """Post to the bots tumblr account"""
    post_content = trigger.group(2)

    t = Tumblpy(consumer_key, consumer_secret, access_token, access_token_secret)

    blog_info = t.post('user/info')
    blog_url = blog_info['user']['blogs'][0]['url']
    blog_title = str(blog_info['user']['blogs'][0]['title'])
    blog_desc = str(blog_info['user']['blogs'][0]['description'])
    blog_posts = str(blog_info['user']['blogs'][0]['posts'])

    if post_content.startswith('info'):
        skrizz.say('[TUMBLR] Title: ' + blog_title + ' | Address: ' + str(blog_url) + ' | Description: ' + blog_desc + ' | Posts: ' + blog_posts)
        return

    if post_content.startswith('that'):
        if trigger.sender not in skrizz.memory['last_seen_url']:
            skrizz.say('I haven\'t seen any URL\'s lately...')
            return
        post_url = skrizz.memory['last_seen_url'][trigger.sender]
        post_caption = post_content.replace("that","",1)
        if not post_caption and skrizz.memory['last_seen_url_title'][trigger.sender]:
            post_caption = skrizz.memory['last_seen_url_title'][trigger.sender]
        elif not post_caption:
            post_caption = "I was too lazy to come up with a clever caption."
        post_content = post_url + " " + post_caption

    post, meta = build_post(post_content)

    if not post:
        skrizz.say("Error: No URL Specified to post.")
        return

    try:
        t.post('post', blog_url=blog_url, params=post)
    except TumbplyError, e:
        skrizz.say(e.message)
        skrizz.say('Something super sad happened :(')
    else: 
        skrizz.say('Successfully posted ' + post['type'] + ':' + meta['url'] + ' with the caption "' + meta['caption'] + '" to my tumblr at: ' + str(blog_url))
    
f_post.commands = ['tumblr', 'tumbl']
f_post.priority = 'medium'
f_post.example = '.tumblr <link> <caption>, .tumbl that <caption> to post last seen url, .tumblr info for information on the bots tumblr account.'

if __name__ == '__main__':
    print __doc__.strip()
