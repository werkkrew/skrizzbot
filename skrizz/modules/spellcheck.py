# -*- coding: utf8 -*-
"""
spellcheck.py - Skrizz spell check Module
Copyright 2012, Elad Alfassa, <elad@fedoraproject.org>
Copyright 2012, Lior Ramati
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.

This module relies on pyenchant, on Fedora and Red Hat based system, it can be found in the package python-enchant
"""
import enchant
from skrizz.module import commands, example


@commands('spellcheck', 'spell')
@example('.spellcheck stuff')
def spellcheck(skrizz, trigger):
    """
    Says whether the given word is spelled correctly, and gives suggestions if
    it's not.
    """
    if not trigger.group(2):
        return
    word=trigger.group(2).rstrip()
    if " " in word:
        skrizz.say("One word at a time, please")
        return;
    dictionary = enchant.Dict("en_US")
    dictionary_uk = enchant.Dict("en_GB")
    # I don't want to make anyone angry, so I check both American and British English.
    if dictionary_uk.check(word):
        if dictionary.check(word): skrizz.say(word+" is spelled correctly")
        else: skrizz.say(word+" is spelled correctly (British)")
    elif dictionary.check(word):
        skrizz.say(word+" is spelled correctly (American)")
    else:
        msg = word+" is not spelled correctly. Maybe you want one of these spellings:"
        sugWords = []
        for suggested_word in dictionary.suggest(word):
                sugWords.append(suggested_word)
        for suggested_word in dictionary_uk.suggest(word):
                sugWords.append(suggested_word)
        for suggested_word in sorted(set(sugWords)): # removes duplicates
            msg = msg + " '"+suggested_word+"',"
        skrizz.say(msg)
