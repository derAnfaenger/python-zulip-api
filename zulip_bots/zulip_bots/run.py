#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import

import logging
import argparse
import sys
import os
from types import ModuleType
from importlib import import_module
from os.path import basename, splitext

import six

from zulip_bots.lib import run_message_handler_for_bot
from zulip_bots.provision import provision_bot

current_dir = os.path.dirname(os.path.abspath(__file__))

def import_module_from_source(path, name=None):
    if not name:
        name = splitext(basename(path))[0]

    if six.PY2:
        import imp
        module = imp.load_source(name, path)
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    return module

def name_and_patch_match(given_name, path_to_bot):
    if given_name and path_to_bot:
        name_by_path = os.path.splitext(os.path.basename(path_to_bot))[0]
        if (given_name != name_by_path):
            return False
    return True

def parse_args():
    usage = '''
        zulip-run-bot <bot_name>
        Example: zulip-run-bot followup
        (This program loads bot-related code from the
        library code and then runs a message loop,
        feeding messages to the library code to handle.)
        Please make sure you have a current ~/.zuliprc
        file with the credentials you want to use for
        this bot.
        See lib/readme.md for more context.
        '''

    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('bot',
                        action='store',
                        help='the name or path of an existing bot to run')

    parser.add_argument('--quiet', '-q',
                        action='store_true',
                        help='turn off logging output')

    parser.add_argument('--config-file',
                        action='store',
                        help='(alternate config file to ~/.zuliprc)')

    parser.add_argument('--force',
                        action='store_true',
                        help='try running the bot even if dependencies install fails')

    parser.add_argument('--provision',
                        action='store_true',
                        help='install dependencies for the bot')

    args = parser.parse_args()
    return args


def main():
    # type: () -> None
    args = parse_args()
    if os.path.isfile(args.bot):
        bot_path = os.path.abspath(args.bot)
        bot_name = os.path.splitext(basename(bot_path))[0]
    else:
        bot_path = os.path.abspath(os.path.join(current_dir, 'bots', args.bot, args.bot+'.py'))
        bot_name = args.bot
    if args.provision:
        provision_bot(os.path.dirname(bot_path), args.force)
    lib_module = import_module_from_source(bot_path, bot_name)

    if not args.quiet:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    run_message_handler_for_bot(
        lib_module=lib_module,
        config_file=args.config_file,
        quiet=args.quiet,
        bot_name=bot_name
    )

if __name__ == '__main__':
    main()
