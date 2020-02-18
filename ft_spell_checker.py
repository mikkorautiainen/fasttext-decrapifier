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

from ft_dbconnect import MysqlDB


# check python version >= 3.6
assert sys.version_info >= (3, 6)


class SpellChecker:
    def __init__(self, config):
        self.language = config['LANGUAGE'].lower()
        if self.language == 'finnish':
            import libvoikko
            self.checker = libvoikko.Voikko(u'fi')
        elif self.language == 'japanese':
            print('Spelling checker for Japanese is not yet implemented')
            sys.exit(4)
        else:
            text_language = self.language.capitalize()
            print(f'Spell checking for {text_language} is not supported')
            sys.exit(4)

    def spelling(self, word):
        if self.language == 'finnish':
            return self.checker.spell(word)

    def morpho(self, word):
        if self.language == 'finnish':
            morpho = self.checker.analyze(word)
            if len(morpho):
                classification = morpho[0].get('CLASS', 'UNKNOWN')
                plurality = morpho[0].get('NUMBER', 'UNKNOWN')
            else:
                classification = 'UNKNOWN'
                plurality = 'UNKNOWN'
            return classification, plurality


def run_spell_checker(config):
    db = MysqlDB(config)
    garbwords = db.get_all_words()
    if not garbwords:
        print('\tError: No garbage words found in database')
        return False

    # remove word from database if it passes spell checker
    sc = SpellChecker(config)
    for json in garbwords:
        word = str(json.get('word'))
        if sc.spelling(word):
            print(f'Removing {word} because it passed the spell ckecker')
            db.words_remove_garbword(word)
            db.commit()


if __name__ == "__main__":
    # execute only if run as a script
    from ft_config import load_config
    config = load_config()

    run_spell_checker(config)
