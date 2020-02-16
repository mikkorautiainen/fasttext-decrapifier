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
import sys
import datetime
import random
import fasttext

from   ft_dbconnect import MysqlDB
import ft_forward_model
import ft_regex


# check python version >= 3.6
assert sys.version_info >= (3, 6)


# constants
MIN_LENGTH = 4
MAX_LENGTH = 20
LOOP_CUTOFF = 100
NUM_GARBAGE_WORDS = 100
FINNISH_CONSONANTS = 'bdfghjklmnprstv'  # finnish consonants


def get_random_words(chars, start, stop, n):
    """
    Returns a list of random words using the arg chars
    in the length from start to stop and count n.
    """
    results = []
    for i in range(n):
        len = random.randrange(start, stop)
        results.append(''.join(random.choice(chars) for _ in range(len)))
    return results

"""
model.get_nn_tpl(word) ret value is e.g.
[Vastainen 0.69319
mukainen 0.662854
vastaisuus 0.656536
säännönvastainen 0.638514
ulkomaalaisvastainen 0.634755
amerikkalaisvastainen 0.634363
lainvastainen 0.632588
vastaista 0.623824
luonnonvastainen 0.616921
venäläisvastainen 0.605122]
"""


def write_garbage_to_database(config, model, db, garbage_words):
    """
    Writes the garbage words iff the word value is over .5
    """
    for word in garbage_words:
        try:
            result = model.get_nn_tpl(word)
            for tp in result:
                if .5 < float(tp[1]):
                    if ft_regex.simple_regex_check(config, tp[0]):
                        db.words_insert_garbword(tp[0], 0)
        except KeyError as err:
            db.words_insert_garbword(word, 2)
            print(f'\tError {err}')
        db.commit()


def run_nn_random(config, BIN_FILE):
    db = MysqlDB(config)

    # load model
    print(datetime.datetime.now().time())
    print('\tLoading model ...')
    model = ft_forward_model.NNLookup(config['FASTTEXT_PATH'], BIN_FILE)
#    print(datetime.datetime.now().time())

    # loop until only LOOP_CUTOFF new words per NUM_GARBAGE_WORDS iterations
    print('Starting nn_query loop')
    garbage_count_old = False
    while True:
        garbage_count_new = db.get_word_count(0)
        if not garbage_count_old:
            regex_count = db.get_word_count(1)
            print(f'\tFound {regex_count} regex words'
                  f' and {garbage_count_new} nn_query words')
        else:
            garbage_count_difference = garbage_count_new - garbage_count_old
            print(f'\tFound {garbage_count_difference} new nn_query words'
                  f' in {NUM_GARBAGE_WORDS} iterations')
            # check LOOP_CUTOFF
            if garbage_count_difference < LOOP_CUTOFF:
                print(f'\tNew nn_query word count {garbage_count_difference} '
                      f' under LOOP_CUTOFF {LOOP_CUTOFF}')
                break
        garbage_count_old = garbage_count_new
        garbage_words = get_random_words(FINNISH_CONSONANTS,
                                         MIN_LENGTH,
                                         MAX_LENGTH,
                                         NUM_GARBAGE_WORDS)
        write_garbage_to_database(config, model, db, garbage_words)

    print('Completed')
    print(datetime.datetime.now().time())


if __name__ == "__main__":
    # execute only if run as a script
    from ft_config import load_config
    config = load_config()

    run_nn_random(config, config['BIN_FILE'])
