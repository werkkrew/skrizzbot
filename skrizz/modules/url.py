"""
url.py - Skrizz URL title module
Copyright 2010-2011, Michael Yanovich, yanovich.net, Kenneth Sham
Copyright 2012-2013 Edward Powell
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""

import re
from htmlentitydefs import name2codepoint
import skrizz.web as web
from skrizz.module import command, rule
import urllib2
import urlparse

url_finder = None
r_entity = re.compile(r'&[A-Za-z0-9#]+;')
exclusion_char = '!'
# These are used to clean up the title tag before actually parsing it. Not the
# world's best way to do this, but it'll do for now.
title_tag_data = re.compile('<(/?)title( [^>]+)?>', re.IGNORECASE)
quoted_title = re.compile('[\'"]<title>[\'"]', re.IGNORECASE)
# This is another regex that presumably does something important.
re_dcc = re.compile(r'(?i)dcc\ssend')


def configure(config):
    """

    | [url] | example | purpose |
    | ---- | ------- | ------- |
    | exclude | https?://git\.io/.* | A list of regular expressions for URLs for which the title should not be shown. |
    | exclusion_char | ! | A character (or string) which, when immediately preceding a URL, will stop the URL's title from being shown. |
    """
    if config.option('Exclude certain URLs from automatic title display', False):
        if not config.has_section('url'):
            config.add_section('url')
        config.add_list('url', 'exclude', 'Enter regular expressions for each URL you would like to exclude.',
            'Regex:')
        config.interactive_add('url', 'exclusion_char',
            'Prefix to suppress URL titling', '!')


def setup(skrizz):
    global url_finder, exclusion_char
    if skrizz.config.has_option('url', 'exclude'):
        regexes = [re.compile(s) for s in
                   skrizz.config.url.get_list(exclude)]
    else:
        regexes = []

    # We're keeping these in their own list, rather than putting then in the
    # callbacks list because 1, it's easier to deal with modules that are still
    # using this list, and not the newer callbacks list and 2, having a lambda
    # just to pass is kinda ugly.
    if not skrizz.memory.contains('url_exclude'):
        skrizz.memory['url_exclude'] = regexes
    else:
        exclude = skrizz.memory['url_exclude']
        if regexes:
            exclude.append(regexes)
        skrizz.memory['url_exclude'] = regexes

    # Ensure that url_callbacks and last_seen_url are in memory
    if not skrizz.memory.contains('url_callbacks'):
        skrizz.memory['url_callbacks'] = {}
    if not skrizz.memory.contains('last_seen_url'):
        skrizz.memory['last_seen_url'] = {}

    if skrizz.config.has_option('url', 'exclusion_char'):
        exclusion_char = skrizz.config.url.exclusion_char

    url_finder = re.compile(r'(?u)(%s?(?:http|https|ftp)(?:://\S+))' %
        (exclusion_char))


@command('title')
def title_command(skrizz, trigger):
    """
    Show the title or URL information for the given URL, or the last URL seen
    in this channel.
    """
    if not trigger.group(2):
        if trigger.sender not in skrizz.memory['last_seen_url']:
            return
        matched = check_callbacks(skrizz, trigger,
                                  skrizz.memory['last_seen_url'][trigger.sender],
                                  True)
        if matched:
            return
        else:
            urls = [skrizz.memory['last_seen_url'][trigger.sender]]
    else:
        urls = re.findall(url_finder, trigger)

    results = process_urls(skrizz, trigger, urls)
    for result in results[:4]:
        message = '[ %s ] - %s' % tuple(result)


@rule('(?u).*(https?://\S+).*')
def title_auto(skrizz, trigger):
    """
    Automatically show titles for URLs. For shortened URLs/redirects, find
    where the URL redirects to and show the title for that (or call a function
    from another module to give more information).
    """
    if re.match(skrizz.config.core.prefix + 'title', trigger):
        return

    urls = re.findall(url_finder, trigger)
    results = process_urls(skrizz, trigger, urls)
    skrizz.memory['last_seen_url'][trigger.sender] = urls[-1]

    for result in results[:4]:
        message = '[ %s ] - %s' % tuple(result)
        if message != trigger:
            skrizz.say(message)


def process_urls(skrizz, trigger, urls):
    """
    For each URL in the list, ensure that it isn't handled by another module.
    If not, find where it redirects to, if anywhere. If that redirected URL
    should be handled by another module, dispatch the callback for it.
    Return a list of (title, TLD) tuples for each URL which is not handled by
    another module.
    """

    results = []
    for url in urls:
        if not url.startswith(exclusion_char):
            # Magic stuff to account for international domain names
            url = iri_to_uri(url)
            # First, check that the URL we got doesn't match
            matched = check_callbacks(skrizz, trigger, url, False)
            if matched:
                continue
            # Then see if it redirects anywhere
            new_url = follow_redirects(url)
            if not new_url:
                continue
            # Then see if the final URL matches anything
            matched = check_callbacks(skrizz, trigger, new_url, new_url != url)
            if matched:
                continue
            # Finally, actually show the URL
            title = find_title(url)
            if title:
                results.append((title, getTLD(url)))
    return results


def follow_redirects(url):
    """
    Follow HTTP 3xx redirects, and return the actual URL. Return None if
    there's a problem.
    """
    try:
        connection = web.get_urllib_object(url, 60)
        url = connection.geturl() or url
        connection.close()
    except:
        return None
    return url


def check_callbacks(skrizz, trigger, url, run=True):
    """
    Check the given URL against the callbacks list. If it matches, and ``run``
    is given as ``True``, run the callback function, otherwise pass. Returns
    ``True`` if the url matched anything in the callbacks list.
    """
    # Check if it matches the exclusion list first
    matched = any(regex.search(url) for regex in skrizz.memory['url_exclude'])
    # Then, check if there's anything in the callback list
    for regex, function in skrizz.memory['url_callbacks'].iteritems():
        match = regex.search(url)
        if match:
            if run:
                function(skrizz, trigger, match)
            matched = True
    return matched


def find_title(url):
    """Return the title for the given URL."""
    content, headers = web.get(url, return_headers=True)
    content_type = headers.get('Content-Type') or ''
    encoding_match = re.match('.*?charset *= *(\S+)', content_type)
    # If they gave us something else instead, try that
    if encoding_match:
        try:
            content = content.decode(encoding_match.group(1))
        except:
            encoding_match = None
    # They didn't tell us what they gave us, so go with UTF-8 or fail silently.
    if not encoding_match:
        try:
            content = content.decode('utf-8')
        except:
            return

    # Some cleanup that I don't really grok, but was in the original, so
    # we'll keep it (with the compiled regexes made global) for now.
    content = title_tag_data.sub(r'<\1title>', content)
    content = quoted_title.sub('', content)

    start = content.find('<title>')
    end = content.find('</title>')
    if start == -1 or end == -1:
        return
    title = content[start + 7:end]
    title = title.strip()[:200]

    def get_unicode_entity(match):
        entity = match.group()
        if entity.startswith('&#x'):
            cp = int(entity[3:-1], 16)
        elif entity.startswith('&#'):
            cp = int(entity[2:-1])
        else:
            cp = name2codepoint[entity[1:-1]]
        return unichr(cp)

    title = r_entity.sub(get_unicode_entity, title)

    title = ' '.join(title.split())  # cleanly remove multiple spaces

    # More cryptic regex substitutions. This one looks to be myano's invention.
    title = re_dcc.sub('', title)

    return title or None


def getTLD(url):
    idx = 7
    if url.startswith('https://'):
        idx = 8
    elif url.startswith('ftp://'):
        idx = 6
    tld = url[idx:]
    slash = tld.find('/')
    if slash != -1:
        tld = tld[:slash]
    return tld


# Functions for international domain name magic


def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)


def iri_to_uri(iri):
    parts = urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti == 1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )
