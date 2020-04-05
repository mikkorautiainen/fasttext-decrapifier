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

import subprocess
import sys
import re
import os

from ft_dbconnect import MysqlDB
from ft_spell_checker import SpellChecker


# check python version >= 3.6
assert sys.version_info >= (3, 6)


def remove_special_cases(config, sc, word):
    # remove words with "'", "\" and Latin œ characters
    if "'" in word or '\\' in word or u'\u0153' in word:
        return True
    # remove if length under nn_query RANDOM_MIN_LENGTH and fails spell checker
    if len(word) < int(config['RANDOM_MIN_LENGTH']):
        if not sc.spelling(word):
            return True
    # remove if foreign characters and fails spelling checker
    if config['REGEX_FOREIGN']:
        if re.search(config['REGEX_FOREIGN'], word):
            if not sc.spelling(word):
                return True
    # keep word if none of the above match
    return False


def remove_garbage_from_vecfile(config, vecfile, new_vecfile):
    """
    file = open vecfile
    ok-words-file = open file for writing

    for line in file:
       word = line.chars-up-to-first-space
       select word in garbwords-db-table
       if not found-entry:
          # this is a ok word
          write this line to ok-words-file
       else:
          pass  # ignore
    end
    """
    db = MysqlDB(config)

    sc = SpellChecker(config)

    outfile = open(new_vecfile, 'w')

    with open(vecfile) as infile:
        count = 0
        print('Removing words from vec-file')
        regex = r'^([^ ]+) '
        for line in infile:
            count += 1
            m = re.match(regex, line)  # get the first word
            if m is not None:
                word = m.group(1)
                if remove_special_cases(config, sc, word):
                    print(f' {word} ', end='')
                    continue
                # remove if found in garbwords table
                if db.find_word(word):
                    print('.', end='')  # show normal removed word as dot
                    continue
                # everthing is ok - write line to output file
                outfile.write(line)
            if not count % 100:
                print('')  # print carriage return every 100 iterations
        print('\n')
    outfile.close()

    
def prepend_line_to_file(text, filepath):
    tmpfile = './__ptemp'
    with open(tmpfile, 'w') as tmp:
        tmp.write(text)
        with open(filepath, 'r') as input:
            for line in input:
                tmp.write(line)
    os.rename(tmpfile, filepath)
    return 0


def add_header_to_vecfile(vecfile):
    # get column and row count
    rows = 0
    with open(vecfile) as outfile:
        line = outfile.readline()
        columns = line.count(' ')
        outfile.seek(0)
        buf = outfile.read(1024 * 1024)
        while buf:
            rows += buf.count('\n')
            buf = outfile.read(1024 * 1024)

    # add header row
    header = f'{rows} {columns}'
    print(f'Adding header "{header}"')
    """
    sed_command = f"1 i\{header}"
    print(f"SED command opt and vec {sed_command} {vecfile}")
    result = subprocess.call(["sed", "-i", sed_command, vecfile])
    """
    result = prepend_line_to_file(header, vecfile)
    if result == 0:
        print('Header added successfully')
        return True
    else:
        print('\nError: Failed to add header\n')
        return False


if __name__ == "__main__":
    # execute only if run as a script
    from ft_config import load_config
    config = load_config()

    remove_garbage_from_vecfile(config, config['VEC_FILE'], config['OUT_FILE'])
    add_header_to_vecfile(config['OUT_FILE'])
