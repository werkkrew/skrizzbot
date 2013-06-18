"""
ping.py - Skrizz Ping Module
Author: Sean B. Palmer, inamidst.com
"""

import random

def hello(skrizz, trigger): 
   if trigger.owner: 
      greeting = random.choice(('Fuck off,', 'Screw you,', 'Go away'))
   else: greeting = random.choice(('Hi', 'Hey', 'Hello'))
   punctuation = random.choice(('', '!'))
   skrizz.say(greeting + ' ' + trigger.nick + punctuation)
hello.rule = r'(?i)(hi|hello|hey) $nickname[ \t]*$'

def rude(skrizz, trigger):
   skrizz.say('Watch your mouth, ' + trigger.nick + ', or I\'ll tell your mother!')
rude.rule = r'(?i)(Fuck|Screw) you, $nickname[ \t]*$'

def interjection(skrizz, trigger): 
   skrizz.say(trigger.nick + '!')
interjection.rule = r'$nickname!'
interjection.priority = 'high'
interjection.thread = False

if __name__ == '__main__': 
   print __doc__.strip()
