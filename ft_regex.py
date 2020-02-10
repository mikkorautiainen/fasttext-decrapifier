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

from ft_dbconnect import MysqlDB


# check python version >= 3.6
assert sys.version_info >= (3, 6)


def simple_regex_check(word):
    """ C, Q, W, X or Z excluded """
    regex = r'^([abd-pr-vyABD-PR-VYÅåÄäÖöŠšŽž\-\']+$)'
    if re.match(regex, word) is None:
        return False
    """ exclude words beginning with dash and containing consecutive dashes """
    if re.search(r'^-|--', word):
        return False
    return True


def regex_vecfile(vecfile):
    """
    Runs the regex on the vec file entries and add the word if the word
    did not match the regex=garbage word.
    Reads line by line from the vec file.
    Check if the word in line has a matching entry in garbwords table.
    Insert the word if not in the table.
    """
    db = MysqlDB()
    with open(vecfile) as infile:
        for line in infile:
            text_regex = r'^([^ ]+) '
            m = re.match(text_regex, line)  # get the first word
            if m is not None:
                word = m.group(1)
                if not simple_regex_check(word):
                    result = db.words_insert_garbword(word, 1)
                    if hasattr(result, 'lastrowid'):
                        print(f'Added {word} because it failed the regex')
                    else:
                        print(f'Failed to add {word} to the database')
    # commit to db
    db.commit()


if __name__ == "__main__":
    # execute only if run as a script
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--vec', required=False, default='./cc.fi.300.vec')
    args = parser.parse_args()

    regex_vecfile(args.vec)
