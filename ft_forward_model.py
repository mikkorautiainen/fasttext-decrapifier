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

import fasttext
import pexpect



NUM_NEIGHBORS = 10


"""
Adapted from https://github.com/facebookresearch/fastText/issues/384
"""
class NNLookup:
    """Class for using the command-line interface to
    fasttext nn to lookup neighbours. It's rather fiddly
    and depends on exact text strings. But it is at least
    short and simple."""
    def __init__(self, fasttext_path, model_path):
        self.nn_process = pexpect.spawn(
            f'{fasttext_path} nn {model_path} {NUM_NEIGHBORS}'
            )
        self.nn_process.expect('Query word?',
                               timeout=180)  # Flush the first prompt out.

    def get_nn(self, word):
        """ Returns a list of text strings in
        the form ["mukainen 0.662854",...] """
        self.nn_process.sendline(word)
        self.nn_process.expect('Query word?')
        output = self.nn_process.before
        output = output.decode('UTF-8')
        words = []
        results = output.split('\r\n')[1:]
        for line in results:
            words.append(line)
        return words

    def get_nn_tpl(self, word):
        """
        returns a list of word and value tuples
        e.g. [(Vastainen,0.69319),(mukainen,0.662854),(vastaisuus,0.656536),
              (säännönvastainen,0.638514)....]
        """
        self.nn_process.sendline(word)
        self.nn_process.expect('Query word?')
        output = self.nn_process.before
        output = output.decode('UTF-8')
        results = output.split('\r\n')[1:]
        ret = []
        for line in results:
            if 0 < len(line):
                wv = line.split(' ')
                tp = (wv[0], wv[1],)
                ret.append(tp)
        return ret
