"""
reload.py - Skrizz Module Reloader Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.
"""

import sys
import os.path
import time
import imp
import skrizz.module
import subprocess


@skrizz.module.command("reload")
@skrizz.module.priority("low")
@skrizz.module.thread(False)
def f_reload(skrizz, trigger):
    """Reloads a module, for use by admins only."""
    if not trigger.admin:
        return

    name = trigger.group(2)
    if name == skrizz.config.owner:
        return skrizz.reply('What?')

    if (not name) or (name == '*') or (name.upper() == 'ALL THE THINGS'):
        skrizz.callables = None
        skrizz.commands = None
        skrizz.setup()
        return skrizz.reply('done')

    if not name in sys.modules:
        return skrizz.reply('%s: no such module!' % name)

    old_module = sys.modules[name]

    old_callables = {}
    for obj_name, obj in vars(old_module).iteritems():
        if skrizz.is_callable(obj):
            old_callables[obj_name] = obj

    skrizz.unregister(old_callables)
    # Also remove all references to skrizz callables from top level of the
    # module, so that they will not get loaded again if reloading the
    # module does not override them.
    for obj_name in old_callables.keys():
        delattr(old_module, obj_name)

    # Thanks to moot for prodding me on this
    path = old_module.__file__
    if path.endswith('.pyc') or path.endswith('.pyo'):
        path = path[:-1]
    if not os.path.isfile(path):
        return skrizz.reply('Found %s, but not the source file' % name)

    module = imp.load_source(name, path)
    sys.modules[name] = module
    if hasattr(module, 'setup'):
        module.setup(skrizz)

    mtime = os.path.getmtime(module.__file__)
    modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(mtime))

    skrizz.register(vars(module))
    skrizz.bind_commands()

    skrizz.reply('%r (version: %s)' % (module, modified))


if sys.version_info >= (2, 7):
    def update(skrizz, trigger):
        if not trigger.admin:
            return

        """Pulls the latest versions of all modules from Git"""
        proc = subprocess.Popen('/usr/bin/git pull',
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)
        skrizz.reply(proc.communicate()[0])

        f_reload(skrizz, trigger)
else:
    def update(skrizz, trigger):
        skrizz.say('You need to run me on Python 2.7 to do that.')
update.rule = ('$nick', ['update'], r'(.+)')


@skrizz.module.command("load")
@skrizz.module.priority("low")
@skrizz.module.thread(False)
def f_load(skrizz, trigger):
    """Loads a module, for use by admins only."""
    if not trigger.admin:
        return

    module_name = trigger.group(2)
    path = ''
    if module_name == skrizz.config.owner:
        return skrizz.reply('What?')

    if module_name in sys.modules:
        return skrizz.reply('Module already loaded, use reload')

    mods = skrizz.config.enumerate_modules()
    for name in mods:
        if name == trigger.group(2):
            path = mods[name]
    if not os.path.isfile(path):
        return skrizz.reply('Module %s not found' % module_name)

    module = imp.load_source(module_name, path)
    mtime = os.path.getmtime(module.__file__)
    modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(mtime))
    if hasattr(module, 'setup'):
        module.setup(skrizz)
    skrizz.register(vars(module))
    skrizz.bind_commands()

    skrizz.reply('%r (version: %s)' % (module, modified))


if __name__ == '__main__':
    print __doc__.strip()
