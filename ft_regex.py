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


def simple_regex_check(config, word):
    # Fail if word doesn't match REGEX_POSITIVE
    if re.match(config['REGEX_POSITIVE'], word) is None:
        return False
    # Fail if word matchs REGEX_NEGATIVE
    elif 0<len(config['REGEX_NEGATIVE']) and re.search(config['REGEX_NEGATIVE'], word):
        return False
    # Fail if word matchs REGEX_REPEAT
    elif 0<len(config['REGEX_REPEAT']) and re.search(config['REGEX_REPEAT'], word):
        return False
    else:
        return True


def regex_vecfile(config, vecfile):
    """
    Runs the regex on the vec-file entries and
    adds the word if the word matches the regex == garbage word.
    Reads vec-file line by line and inserts garbage words to garbwords table.
    """
    db = MysqlDB(config)

    print('Adding garbage words to database')
    with open(vecfile) as infile:
        count = 0
        for line in infile:
            count += 1
            m = re.match(r'^([^"\\ ]+) ', line)  # get the first field
            if m is not None:
                word = m.group(1)
                if not simple_regex_check(config, word):
                    result = db.words_insert_garbword(word, 1)
                    if hasattr(result, 'lastrowid'):
                        print(f'{word} ', end='')  # show garbage word
                    else:
                        import pdb; pdb.set_trace()
                        print(f'\nError: Failed to add "{word}" to database\n')
            if not count % 60:
                print('')  # print carriage return every 60 iterations

    # commit to db
    print('\n\nCommitting garbage words to database')
    db.commit()
    print('\nRegex done')


if __name__ == "__main__":
    # execute only if run as a script
    from ft_config import load_config
    config = load_config()

    regex_vecfile(config, config['VEC_FILE'])
