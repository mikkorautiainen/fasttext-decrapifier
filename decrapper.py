#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 GBC Networks Oy.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import sys

from ft_config import load_config


# check python version >= 3.6
assert sys.version_info >= (3, 6)


# read config.json
config = load_config()


# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--action',
                    required=True,
                    help="Action to perform: 'init', 'regex', "
                         "'nn_query', 'spell_checker', 'remove', "
                         "'vocabulary'")
parser.add_argument('--bin',
                    required=False,
                    default=config['BIN_FILE'],
                    help="Fasttext model in binary format")
parser.add_argument('--vec',
                    required=False,
                    default=config['VEC_FILE'],
                    help="Fasttext vectors in plain-text format")
parser.add_argument('--output',
                    required=False,
                    default=config['OUT_FILE'],
                    help="Decrapped vectors in plain-text format")
parser.add_argument('--vocab',
                    required=False,
                    default=config['VOCAB_FILE'],
                    help="Decrapped vocabulary")
args = parser.parse_args()


# actions
ACTION = args.action.lower()
if ACTION == 'init':
    from ft_dbconnect import MysqlDB
    db = MysqlDB(config)

    db.initialize_database()
    sys.exit(0)

elif ACTION == 'regex':
    import ft_regex
    ft_regex.regex_vecfile(config, args.vec)
    sys.exit(0)

elif ACTION == 'nn_query':
    import ft_nn_query
    ft_nn_query.run_nn_random(config, args.bin)
    sys.exit(0)

elif ACTION == 'spell_checker':
    import ft_spell_checker
    ft_spell_checker.run_spell_checker(config)
    sys.exit(0)

elif ACTION == 'remove':
    import ft_remove_garbage
    ft_remove_garbage.remove_garbage_from_vecfile(config, args.vec, args.output)
    ft_remove_garbage.add_header_to_vecfile(args.output)
    sys.exit(0)

elif ACTION == 'vocabulary':
    import ft_vocab
    ft_vocab.create_vocab_file(args.output, args.vocab)
    sys.exit(0)

else:
    print('Error: Action {} not found'.format(ACTION))
    sys.exit(5)
