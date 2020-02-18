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

import re
import sys

from ft_spell_checker import SpellChecker


# check python version >= 3.6
assert sys.version_info >= (3, 6)


def create_vocab_file(config, vecfile, vocabfile):
    # read vector file
    vocab = {}
    with open(vecfile) as infile:
        print(f'\tReading {vecfile}')
        line = infile.readline()  # skip first line
        regex = r'^([^ ]+) '
        for line in infile:
            m = re.match(regex, line)  # get the first word
            if m is not None:
                word = m.group(1)
                vocab[word.lower()] = True
    print(f'Found {len(vocab)} words\n')

    # write vocab file
    sc = SpellChecker(config)
    with open(vocabfile, 'w') as outfile:
        print(f'\tWriting {vocabfile}')
        for word in sorted(vocab.keys()):
            # get lexical class and plurality
            classification, plurality = sc.morpho(word)
            # write word TAB class TAB plurality
            line = f'{word}\t{classification}\t{plurality}\n'
            outfile.write(line)
        print('Vocab file creation complete\n')


if __name__ == "__main__":
    # execute only if run as a script
    from ft_config import load_config
    config = load_config()

    create_vocab_file(config, config['VEC_FILE'], config['VOCAB_FILE'])
