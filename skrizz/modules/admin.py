# coding=utf-8
"""
admin.py - Skrizz Admin Module
Copyright 2010-2011, Sean B. Palmer (inamidst.com) and Michael Yanovich
(yanovich.net)
Copyright 2012, Elad Alfassa, <elad@fedoraproject.org>
Copyright 2013, Ari Koivula <ari@koivu.la>
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""

import skrizz.module


def configure(config):
    """
    | [admin] | example | purpose |
    | -------- | ------- | ------- |
    | hold_ground | False | Auto re-join on kick |
    """
    config.add_option('admin', 'hold_ground', "Auto re-join on kick")


@skrizz.module.commands('join')
@skrizz.module.priority('low')
@skrizz.module.example('.join #example or .join #example key')
def join(bot, trigger):
    """Join the specified channel. This is an admin-only command."""
    # Can only be done in privmsg by an admin
    if trigger.sender.startswith('#'):
        return

    if trigger.admin:
        channel, key = trigger.group(3), trigger.group(4)
        if not channel:
            return
        elif not key:
            bot.join(channel)
        else:
            bot.join(channel, key)


@skrizz.module.commands('part')
@skrizz.module.priority('low')
@skrizz.module.example('.part #example')
def part(bot, trigger):
    """Part the specified channel. This is an admin-only command."""
    # Can only be done in privmsg by an admin
    if trigger.sender.startswith('#'):
        return
    if not trigger.admin:
        return

    channel, _sep, part_msg = trigger.group(2).partition(' ')
    if part_msg:
        bot.part(channel, part_msg)
    else:
        bot.part(channel)


@skrizz.module.commands('quit')
@skrizz.module.priority('low')
def quit(bot, trigger):
    """Quit from the server. This is an owner-only command."""
    # Can only be done in privmsg by the owner
    if trigger.sender.startswith('#'):
        return
    if not trigger.owner:
        return

    quit_message = trigger.group(2)
    if not quit_message:
        quit_message = 'Quitting on command from %s' % trigger.nick

    bot.quit(quit_message)


@skrizz.module.commands('msg')
@skrizz.module.priority('low')
@skrizz.module.example('.msg #YourPants Does anyone else smell neurotoxin?')
def msg(bot, trigger):
    """
    Send a message to a given channel or nick. Can only be done in privmsg by an
    admin.
    """
    if trigger.sender.startswith('#'):
        return
    if not trigger.admin:
        return

    channel, _sep, message = trigger.group(2).partition(' ')
    message = message.strip()
    if not channel or not message:
        return

    bot.msg(channel, message)


@skrizz.module.commands('me')
@skrizz.module.priority('low')
def me(bot, trigger):
    """
    Send an ACTION (/me) to a given channel or nick. Can only be done in privmsg
    by an admin.
    """
    if trigger.sender.startswith('#'):
        return
    if not trigger.admin:
        return

    channel, _sep, action = trigger.group(2).partition(' ')
    action = action.strip()
    if not channel or not action:
        return

    msg = '\x01ACTION %s\x01' % action
    bot.msg(channel, msg)


@skrizz.module.event('KICK')
@skrizz.module.rule(r'.*')
@skrizz.module.priority('low')
def hold_ground(bot, trigger):
    """
    This function monitors all kicks across all channels skrizz is in. If it
    detects that it is the one kicked it'll automatically join that channel.

    WARNING: This may not be needed and could cause problems if skrizz becomes
    annoying. Please use this with caution.
    """
    if bot.config.has_section('admin') and bot.config.admin.hold_ground:
        channel = trigger.sender
        if trigger.args[1] == bot.nick:
            bot.join(channel)


@skrizz.module.commands('mode')
@skrizz.module.priority('low')
def mode(bot, trigger):
    """Set a user mode on Skrizz. Can only be done in privmsg by an admin."""
    if trigger.sender.startswith('#'):
        return
    if not trigger.admin:
        return
    mode = trigger.group(3)
    bot.write(('MODE ', bot.nick + ' ' + mode))


@skrizz.module.commands('set')
@skrizz.module.example('.set core.owner Me')
def set_config(bot, trigger):
    """See and modify values of skrizzs config object.

    Trigger args:
        arg1 - section and option, in the form "section.option"
        arg2 - value

    If there is no section, section will default to "core".
    If value is None, the option will be deleted.
    """
    if trigger.sender.startswith('#'):
        bot.reply("This command only works as a private message.")
        return
    if not trigger.admin:
        bot.reply("This command requires admin priviledges.")
        return

    # Get section and option from first argument.
    arg1 = trigger.group(3).split('.')
    if len(arg1) == 1:
        section, option = "core", arg1[0]
    elif len(arg1) == 2:
        section, option = arg1
    else:
        bot.reply("Usage: .set section.option value")
        return

    # Don't modify non-existing values to guard against typos.
    if not bot.config.has_option(section, option):
        bot.reply("Option %s.%s does not exist." % (section, option))
        return

    # Display current value if no value is given.
    value = trigger.group(4)
    if not value:
        # Except if the option looks like a password. Censor those to stop them
        # from being put on log files.
        if option.endswith("password") or option.endswith("pass"):
            value = "(password censored)"
        else:
            value = getattr(getattr(bot.config, section), option)
        bot.reply("%s.%s = %s" % (section, option, value))
        return

    # Otherwise, set the value to one given as argument 2.
    setattr(getattr(bot.config, section), option, value)


@skrizz.module.command('save')
@skrizz.module.example('.save')
def save_config(bot, trigger):
    """Save state of skrizzs config object to the configuration file."""
    if trigger.sender.startswith('#'):
        return
    if not trigger.admin:
        return
    bot.config.save()

@skrizz.module.command('reload_new')
@skrizz.module.example('.reload module_name|all')
@skrizz.module.priority('high')
def reload(bot, trigger):
    """Attempt to reload modules."""
    if not trigger.admin:
        bot.reply("Only an admin can reload modules!")
    else:
        count = bot.setup()
        message = "Reloaded " + str(count[0]) + " Modules, " + str(count[1]) + " modules failed to load!"
        bot.reply(message)
        return 

if __name__ == '__main__':
    print __doc__.strip()
