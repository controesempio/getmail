#!/usr/bin/env python2.3
'''Base classes used elsewhere in the package.

'''

from exceptions import *
from logging import logger

#
# Base classes
#

#######################################
class ConfigurableBase(object):
    '''Base class for user-configurable classes.

    Sub-classes must provide the following data attributes and methods:

      _confitems - a tuple of dictionaries representing the parameters the class
                   takes.  Each dictionary should contain the following key, value
                   pairs:
                     - name - parameter name
                     - type - a type function to compare the parameter value against (i.e. str, int, bool)
                     - default - optional default value.  If not preseent, the parameter is required.
    '''

    def __init__(self, **args):
        self.log = logger()
        self.log.trace('args: %s\n' % args)
        self.conf = {}
        for (name, value) in args.items():
            self.log.trace('setting %s to %s (%s)\n' % (name, value, type(value)))
            self.conf[name] = value
        self.__confchecked = False

    def checkconf(self):
        self.log.trace()
        if self.__confchecked:
            return
        for item in self._confitems:
            self.log.trace('checking %s\n' % item)
            name = item['name']
            dtype = item['type']
            if not self.conf.has_key(name):
                # Not provided
                if item.has_key('default'):
                    self.conf[name] = item['default']
                else:
                    raise getmailConfigurationError('missing required configuration directive %s' % name)
            elif type(self.conf[name]) is not dtype:
                # Value supplied, but not of expected type.  Try to convert.
                try:
                    val = self.conf[name]
                    self.log.debug('converting %s (%s) to type %s\n' % (name, val, dtype))
                    # Handle boolean values intelligently
                    if dtype == bool:
                        if val.lower() in ('0', 'false', 'no', 'off'):
                            self.conf[name] = False
                        elif val.lower() in ('1', 'true', 'yes', 'on'):
                            self.conf[name] = True
                        self.conf[name] = bool(eval(val))
                    else:
                        self.conf[name] = dtype(eval(val))
                except (ValueError, SyntaxError), o:
                    raise getmailConfigurationError('configuration value %s (%s) not of required type %s (%s)' % (name, val, dtype, o))
        self.__confchecked = True
        self.log.trace('done\n')

    def _confstring(self):
        self.log.trace()
        confstring = ''
        names = self.conf.keys()
        names.sort()
        for name in names:
            if confstring:  confstring += ', '
            if name.lower() == 'password':
                confstring += '%s="*"' % name
            else:
                confstring += '%s="%s"' % (name, self.conf[name])
        return confstring
