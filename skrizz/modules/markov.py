"""
markov.py - markov chain language module thing
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""
import random
import time
import re
import os
import skrizz.module
from skrizz.tools import Nick

chain_length = 2
chattiness = 0.05
max_words = 30
messages_to_generate = 5
random.seed()
limit = 3
ignore = '/','.','!'
separator = '\x01'
stop_word = '\x02'
respond = True

#chain_length = bot.config.markov.chain_length
#chattiness = bot.config.markov.chattiness
#max_words = bot.config.markov.max_words
#messages_to_generate = bot.config.markov.messages_to_generate

def checkdb(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS markov ( channel STRING, key STRING, words STRING )')
    cursor.execute('CREATE INDEX IF NOT EXISTS markov_idx ON markov (key)')

def setup(bot):
    global SUB
    SUB = (bot.db.substitution,)
    bot.memory['markov'] = dict()

def configure(config):

    if config.option('Configure Markov?', False):
        config.interactive_add('markov', 'chain_length', 'Chain Length')
        config.interactive_add('markov', 'chattiness', 'Chattiness')
        config.interactive_add('markov', 'max_words', 'Max Words')
        config.interactive_add('markov', 'messages_to_generate', 'Messages to Generate')
  
def sanitize_message(message):
    return re.sub('[\"\']', '', message.lower())

def split_message(message):
    # split the incoming message into words, i.e. ['what', 'up', 'bro']
    words = message.split()
     
    # if the message is any shorter, it won't lead anywhere
    if len(words) > chain_length:
           
        # add some stop words onto the message
        # ['what', 'up', 'bro', '\x02']
        words.append(stop_word)
            
        # len(words) == 4, so range(4-2) == range(2) == 0, 1, meaning
        # we return the following slices: [0:3], [1:4]
        # or ['what', 'up', 'bro'], ['up', 'bro', '\x02']
        for i in range(len(words) - chain_length):
            yield words[i:i + chain_length + 1]
    
def generate_message(bot, seed):
    key = seed
     
    # keep a list of words we've seen
    gen_words = []
        
    # only follow the chain so far, up to <max words>
    for i in xrange(max_words):
     
        # split the key on the separator to extract the words -- the key
        # might look like "this\x01is" and split out into ['this', 'is']
        words = key.split(separator)
            
        # add the word to the list of words in our generated message
        gen_words.append(words[0])

        # get a new word that lives at this key -- if none are present we've
        # reached the end of the chain and can bail
        conn = bot.db.connect()
        c = conn.cursor()
        c.execute('SELECT words FROM markov WHERE key = %s ORDER BY RANDOM() LIMIT 1' % (SUB), (key,))
        row = c.fetchone()
        if row is not None:
            next_word = row[0]
        else:
            next_word = 0
        #next_word = redis_conn.srandmember(key)
        if not next_word:
            break
           
        # create a new key combining the end of the old one and the next_word
        key = separator.join(words[1:] + [next_word])

    return ' '.join(gen_words)

@skrizz.module.rule('.*')
@skrizz.module.priority('low')
def log(bot, trigger):

    message = trigger.group()

    if message.startswith(ignore):
        return

    if respond:
        ping = re.compile('(?i).*' + bot.nick + '.*')
        ping_me = ping.match(message) 
    else:
        ping_me = False
    
    # speak only when spoken to, or when the spirit moves me
    say_something = ping_me or (random.random() < chattiness)
        
    messages = []

    # split up the incoming message into chunks that are 1 word longer than
    # the size of the chain, e.g. ['what', 'up', 'bro'], ['up', 'bro', '\x02']
    for words in split_message(sanitize_message(message)):
        # grab everything but the last word
        key = separator.join(words[:-1])
           
        # add the last word to the set
        conn = bot.db.connect()
        c = conn.cursor()
        checkdb(c)
        conn.commit()
        c.execute('INSERT INTO markov VALUES (%s, %s, %s)' % (SUB*3), (trigger.sender, key, words[-1])) 
        conn.commit()
        c.close()
        #bot.db.markov.insert(key, {'words': words[-1], 'channel': trigger.sender})
        #redis_conn.sadd(key, words[-1])
            
        # if we should say something, generate some messages based on what
        # was just said and select the longest, then add it to the list
        if say_something:
            best_message = ''
            for i in range(messages_to_generate):
                generated = generate_message(bot, seed=key)
                if len(generated) > len(best_message):
                    best_message = generated
                
            if best_message:
                messages.append(best_message)

        conn.close()    
        
    if len(messages):
        message = random.choice(messages)
        
        # Add a log of things the bot has said, if there isn't already one
        if trigger.sender not in bot.memory['markov']:
            bot.memory['markov'][trigger.sender] = dict()
        if Nick(trigger.nick) not in bot.memory['markov'][trigger.sender]:
            bot.memory['markov'][trigger.sender][Nick(trigger.nick)] = list()

        templist = bot.memory['markov'][trigger.sender][Nick(trigger.nick)] = list()
        templist.append(message)

        # Only hold on to 10 things
        del templist[:-10]

        bot.memory['markov'][trigger.sender][Nick(trigger.nick)] = templist
        bot.say(message)


@skrizz.module.command('lastsaid')
@skrizz.module.priority('low')
def lastsaid(bot, trigger):
    if trigger.sender not in bot.memory['markov']:
        bot.say('I haven\'t said anything in this channel recently.')
        return
    recent = bot.memory['markov'][trigger.sender][Nick(trigger.nick)]
    bot.say(recent[0])

@skrizz.module.command('teach')
@skrizz.module.priority('low')
@skrizz.module.example('.teach <filename>')
def teach(bot, trigger):
    if not trigger.admin:
        bot.say("Only admins can teach me!")
        return

    filename = trigger.group(2)

    if filename is None:
        bot.say('Usage: .teach <filename>')
    else:
        try:
            f = open(filename, 'r')
        except IOError:
            bot.say('Invalid file.')
        else:
            bot.say('Processing file: ' + filename)
            lines = 0
            conn = bot.db.connect()
            c = conn.cursor()
            checkdb(c)
            conn.commit()

            for line in f:
                lines = lines + 1
                if (lines % 1000) is 0:
                    bot.msg(trigger.nick, 'Processed ' + str(lines) + ' lines in ' + filename)
                line = line.decode("utf-8")
                for words in split_message(sanitize_message(line)):
                    # grab everything but the last word
                    key = separator.join(words[:-1])

                    # add the last word to the set
                    c.execute('INSERT INTO markov VALUES (%s, %s, %s)' % (SUB*3), (trigger.sender, key, words[-1]))
                    conn.commit()

            c.close()
            f.close()
            bot.msg(trigger.nick, 'Successfully added <' + str(lines) + '> worth of shit to my database!')

    return



if __name__ == '__main__':
    print __doc__.strip()
