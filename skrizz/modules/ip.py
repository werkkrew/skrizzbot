# coding=utf-8
"""
ip.py - Skrizz IP Lookup Module
Copyright 2011, Dimitri Molenaars, TyRope.nl,
Copyright 2013, Elad Alfassa <elad@fedoraproject.org>
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""

import re
import pygeoip
import socket
from skrizz.module import commands, example

@commands('iplookup', 'ip')
@example('.ip 8.8.8.8')
def ip(skrizz, trigger):
    """IP Lookup tool"""
    if not trigger.group(2):
        return skrizz.reply("No search term.")
    query = trigger.group(2)
    # FIXME: This shouldn't be hardcoded
    gi_city = pygeoip.GeoIP('/usr/share/GeoIP/GeoLiteCity.dat')
    gi_org = pygeoip.GeoIP('/usr/share/GeoIP/GeoIPASNum.dat')
    host = socket.getfqdn(query)
    response = "[IP/Host Lookup] Hostname: %s" % host
    response += " | Location: %s" % gi_city.country_name_by_name(query)
    region = gi_city.region_by_name(query)['region_name']
    if region is not '':
        response += " | Region: %s" % region
    isp = gi_org.org_by_name(query)
    if isp is not None:
        isp = re.sub('^AS\d+ ', '', isp)
    response += " | ISP: %s" % isp
    skrizz.say(response)

if __name__ == '__main__':
    print __doc__.strip()
