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


# check python version >= 3.6
assert sys.version_info >= (3, 6)


def remove_garbage_from_vecfile(vecfile, new_vecfile):
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
    db = MysqlDB()

    outfile = open(new_vecfile, 'w')

    with open(vecfile) as infile:
        print('Removing', end='')
        regex = r'^([^ ]+) '
        for line in infile:
            m = re.match(regex, line)  # get the first word
            if m is not None:
                word = m.group(1)
                if "'" in word:
                    print(f' {word}', end='')
                    continue
                cur = db.find_word(word)  # search garbwords table
                # print(f'word={word} {cur.rowcount}')
                if int(cur.rowcount) <= 0:
                    # Not in the garbage words
                    # print(f'Adding {word} as it is not in garbage DB')
                    outfile.write(line)
                else:
                    print(f' {word}', end='')
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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--vec',
                        required=False,
                        default='./cc.fi.300.vec')
    parser.add_argument('--output',
                        required=False,
                        default='./cc.fi.300.filtered.vec')
    args = parser.parse_args()

    VEC_FILE = args.vec  # default './cc.fi.300.vec'
    OUT_FILE = args.output  # default './cc.fi.300.filtered.vec'

    remove_garbage_from_vecfile(VEC_FILE, OUT_FILE)
    add_header_to_vecfile(OUT_FILE)
