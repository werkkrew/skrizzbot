"""
markov.py - markov chain language module thing
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""
import random
import time
import re
import os
import cPickle as pickle
import skrizz.module
import sys
import sqlite3
from skrizz.tools import Nick

chain_length = 2 # supported values are 2 or 3, anything bigger im not dealing with.
db = '/home/wkbec/.skrizz/markov.db'
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
#db = bot.config.markov.database_file
#respond = bot.config.markov.respond
#filter = bot.config.markov.filter

brain = dict()

def build_brain(bot):
    start_time = time.time()
    brain.clear()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT key,next_words FROM markov2')
    rows = c.fetchall()
    if rows is not None:
        for row in rows:
            key = row[0]
            next_words = pickle.loads(str(row[1]))
            brain[key] = next_words
    end_time = time.time()
    total_time = end_time - start_time, "seconds"
    brain_size = sys.getsizeof(brain)
    bot.say("Time to generate brain: " + str(total_time))
    bot.say("Size of brain is: " + str(len(brain)) + " keys and " + str(brain_size) + " bytes")

def setup(bot):
    global SUB
    SUB = (bot.db.substitution,)
    bot.memory['markov'] = dict()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS markov2 ( key STRING PRIMARY KEY ON CONFLICT REPLACE, next_words BLOB )')
    c.execute("PRAGMA journal_mode = wal;")
    conn.commit()
    c.close()
    build_brain(bot)

def configure(config):

    # add all config options here
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
            
        for i in range(len(words) - chain_length):
            yield words[i:i + chain_length + 1]

def get_next_word(key):
    if key not in brain:
        return 0
    else:
        return weighted_choice(brain[key])

def weighted_choice(words):
   total = sum(w for c, w in words.iteritems())
   r = random.uniform(0, total)
   upto = 0
   for c, w in words.iteritems():
      if upto + w > r:
         return c
      upto += w
   assert False, "Shouldn't get here"

def generate_message(seed):
    key = seed

    gen_words = []

    # only follow the chain so far, up to <max words>
    for i in xrange(max_words):

        words = key.split(separator)
        gen_words.append(words[0])

        next_word = get_next_word(key)

        if not next_word:
            break

        key = separator.join(words[1:] + [next_word])

    return ' '.join(gen_words)
   
def add_data(key, next_word):
    if key in brain:
        if next_word in brain[key]:
            weight = brain[key][next_word] + 1
        else:
            weight = 1
        brain[key][next_word] = weight
    else:
        brain[key] = {next_word: 1}

    next_words = brain[key]
    next_words = pickle.dumps(next_words)

    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('INSERT INTO markov2 VALUES (%s, %s)' % (SUB*2), (key, sqlite3.Binary(next_words)))
    conn.commit()
    c.close()

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

        key = separator.join(words[:-1]).encode('utf-8')
        next_word = words[-1].encode('utf-8')

        add_data(key,next_word)

        if say_something:
            best_message = ''
            for i in range(messages_to_generate):
                generated = generate_message(seed=key)
                if len(generated) > len(best_message):
                    best_message = generated

            if best_message:
                messages.append(best_message)


    if len(messages):
        message = random.choice(messages)
        
        # Add a log of things the bot has said, if there isn't already one
        if trigger.sender not in bot.memory['markov']:
            bot.memory['markov'][trigger.sender] = dict()
        if Nick(bot.nick) not in bot.memory['markov'][trigger.sender]:
            bot.memory['markov'][trigger.sender][Nick(bot.nick)] = list()

        templist = bot.memory['markov'][trigger.sender][Nick(bot.nick)] = list()
        templist.append(message)

        # Only hold on to 10 things
        del templist[:-10]

        bot.memory['markov'][trigger.sender][Nick(bot.nick)] = templist
        bot.say(message)


@skrizz.module.command('lastsaid')
@skrizz.module.priority('low')
def lastsaid(bot, trigger):
    if trigger.sender not in bot.memory['markov']:
        bot.say('I haven\'t said anything in this channel recently.')
        return
    recent = bot.memory['markov'][trigger.sender][Nick(bot.nick)]
    bot.say(recent[-1])

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
            start_time = time.time()
            bot.say('Processing file: ' + filename)
            lines = 0

            for line in f:
                lines = lines + 1
                if (lines % 1000) is 0:
                    bot.msg(trigger.nick, 'Processed ' + str(lines) + ' lines in ' + filename)
                line = line.decode("utf-8")
                for words in split_message(sanitize_message(line)):
                    # grab everything but the last word
                    key = separator.join(words[:-1])
                    next_word = words[-1]
                    add_data(key,next_word)

            end_time = time.time()
            total_time = end_time - start_time, "seconds"
            bot.say('Successfully added <' + str(lines) + '> worth of shit to my database in ' + str(total_time) + '!')

    return

@skrizz.module.command('mstats')
@skrizz.module.priority('low')
def mstats(bot, trigger):
    keys = len(brain)
    size_dict = sys.getsizeof(brain)
    size_file = os.path.getsize(db)
    bot.say('[MARKOV STATS] Number of Keys: ' + str(keys) + ' | Dictionary size in memory: ' + str(size_dict/1024) + 'kb | Persistent Database Size: ' + str(size_file/1024/1024) + 'mb')



if __name__ == '__main__':
    print __doc__.strip()
