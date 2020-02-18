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

from ft_dbconnect import MysqlDB
from ft_spell_checker import SpellChecker


# check python version >= 3.6
assert sys.version_info >= (3, 6)


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

    if config['REGEX_FOREIGN']:
        sc = SpellChecker(config)

    outfile = open(new_vecfile, 'w')

    with open(vecfile) as infile:
        count = 0
        print('Removing words from vec-file', end='')
        regex = r'^([^ ]+) '
        for line in infile:
            m = re.match(regex, line)  # get the first word
            if m is not None:
                word = m.group(1)
                if "'" in word or '\\' in word:
                    print(f' {word} ', end='')
                    continue
                # remove if foreign characters and fails spelling checker
                if config['REGEX_FOREIGN']:
                    if re.search(config['REGEX_FOREIGN'], word):
                        if not sc.spelling(word):
                            print(f' {word} ', end='')
                            continue
                cur = db.find_word(word)  # search garbwords table
                if int(cur.rowcount) <= 0:
                    # Not in the garbage words
                    # print(f'Adding {word} as it is not in garbage DB')
                    outfile.write(line)
                else:
                    print('.', end='') # show normal removed word as dot
            if not count % 100:
                print('') # print carriage return every 100 iterations
            count += 1
        print('\n')
    outfile.close()


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
    sed_command = f"1 i\{header}"
    result = subprocess.call(["sed", "-i", sed_command, vecfile])
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
