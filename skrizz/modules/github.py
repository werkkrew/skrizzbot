"""
github.py - Skrizz Github Module
Copyright 2012, Dimitri Molenaars http://tyrope.nl/
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""

from datetime import datetime
from urllib2 import HTTPError
import json
import re
import skrizz.web as web

def checkConfig(skrizz):
    if not skrizz.config.has_option('github', 'oauth_token') or not skrizz.config.has_option('github', 'repo'):
        return False
    else:
        return [skrizz.config.github.oauth_token, skrizz.config.github.repo]

def configure(config):
    """
    | [github] | example | purpose |
    | -------- | ------- | ------- |
    | oauth_token | 5868e7af57496cc3ae255868e7af57496cc3ae25 | The OAuth token to connect to your github repo |
    | repo | embolalia/skrizz | The GitHub repo you're working from. |
    """
    chunk = ''
    if config.option('Configuring github issue reporting and searching module', False):
        config.interactive_add('github', 'oauth_token', 'Github API Oauth2 token', '')
        config.interactive_add('github', 'repo', 'Github repository', 'embolalia/skrizz')
    return chunk

def issue(skrizz, trigger):
    """Create a GitHub issue, also known as a bug report. Syntax: .makeissue Title of the bug report"""
    #check input
    if not trigger.group(2):
        return skrizz.say('Please title the issue')

    #Is the Oauth token and repo available?
    gitAPI = checkConfig(skrizz)
    if gitAPI == False:
        return skrizz.say('Git module not configured, make sure github.oauth_token and github.repo are defined')

    #parse input
    now = ' '.join(str(datetime.utcnow()).split(' ')).split('.')[0]+' UTC'
    body = 'Submitted by: %s\nFrom channel: %s\nAt %s' % (trigger.nick, trigger.sender, now)
    data = {"title":trigger.group(2).encode('utf-8'), "body":body, "labels": ["IRC"]}
    #submit
    try:
        raw = web.post('https://api.github.com/repos/'+gitAPI[1]+'/issues?access_token='+gitAPI[0], json.dumps(data))
    except HTTPError:
        return skrizz.say('The GitHub API returned an error.')
    
    data = json.loads(raw)
    skrizz.say('Issue #%s posted. %s' % (data['number'], data['html_url']))
    skrizz.debug('GitHub','Issue #%s created in %s' % (data['number'],trigger.sender),'warning')
issue.commands = ['makeissue','makebug']
issue.priority = 'medium'

def findIssue(skrizz, trigger):
    """Search for a GitHub issue by keyword or ID. usage: .findissue search keywords/ID (optional) You can specify the first keyword as "CLOSED" to search closed issues."""
    if not trigger.group(2):
        return skrizz.reply('What are you searching for?')

    #Is the Oauth token and repo available?
    gitAPI = checkConfig(skrizz)
    if gitAPI == False:
        return skrizz.say('Git module not configured, make sure github.oauth_token and github.repo are defined')
    firstParam = trigger.group(2).split(' ')[0]
    if firstParam.isdigit():
        URL = 'https://api.github.com/repos/%s/issues/%s' % (gitAPI[1], trigger.group(2))
    elif firstParam == 'CLOSED':
        if '%20'.join(trigger.group(2).split(' ')[1:]) not in ('','\x02','\x03'):
            URL = 'https://api.github.com/legacy/issues/search/'+gitAPI[1]+'/closed/'+'%20'.join(trigger.group(2).split(' ')[1:])
        else:
            return skrizz.reply('What are you searching for?')
    else:
        URL = 'https://api.github.com/legacy/issues/search/%s/open/%s' % (gitAPI[1], trigger.group(2))

    try:
        raw = web.get(URL)
    except HTTPError:
        return skrizz.say('The GitHub API returned an error.')

    try:
        if firstParam.isdigit():
            data = json.loads(raw)
        else:
            data = json.loads(raw)['issues'][-1]
    except (KeyError, IndexError):
        return skrizz.say('No search results.')
    if len(data['body'].split('\n')) > 1:
        body = data['body'].split('\n')[0]+'...'
    else:
        body = data['body'].split('\n')[0]
    skrizz.reply('[#%s]\x02title:\x02 %s \x02|\x02 %s' % (data['number'],data['title'],body))
    skrizz.say(data['html_url'])
findIssue.commands = ['findissue','findbug']
findIssue.priority = 'medium'

if __name__ == '__main__':
    print __doc__.strip()

