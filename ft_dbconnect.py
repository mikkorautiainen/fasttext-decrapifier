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

from mysql import connector
import re


class MysqlDB:
    db = None        # connector
    database = None  # config

    def __init__(self, config):
        """ connect to the database """
        try:
            if self.database is None:
                self.database = config['DATABASE']
                self.db = None

            self.db = connector.connect(user=self.database['user'],
                                        password=self.database['password'],
                                        host=self.database['host'],
                                        port=self.database['port'],
                                        database=self.database['dbname'],
                                        use_pure=True)
            MysqlDB.db = self.db
        except connector.Error:
            print(f'Failed to connect to database {self.database["dbname"]}')
            self.db = connector.connect(user=self.database['user'],
                                        password=self.database['password'],
                                        host=self.database['host'],
                                        port=self.database['port'],
                                        use_pure=True)
            MysqlDB.db = self.db

    def execute(self, sql, values):
        """ execute query with params and return cursor """
        try:
            self.cursor = self.db.cursor(dictionary=True, buffered=True)
            self.cursor.execute(sql, values)
            return self.cursor
        except connector.Error as err:
            print(f'Error: Something went wrong: {err} on {sql}')
        return None

    def fetchall(self):
        """ calling fetchall on cursor """
        return self.cursor.fetchall()

    def fetchone(self):
        """ calling fetchone on cursor """
        return self.cursor.fetchone()

    def initialize_database(self):
        """ initialize mysql database from ground 0 """
        query = f'DROP DATABASE IF EXISTS {self.database["dbname"]}'
        self.execute(query, ())

        print(f'Creating database {self.database["dbname"]}')
        query = f'CREATE DATABASE {self.database["dbname"]}'
        self.execute(query, ())

        # reinitialize database connection
        MysqlDB.__init__(self, None)

        query = f'CREATE TABLE `{self.database["table"]}` ( ' \
                 '    `word` text NOT NULL, ' \
                 '    `count` int(11) NOT NULL DEFAULT 0, ' \
                 '    `regexflag` tinyint(4) NOT NULL, ' \
                 '    `value` float DEFAULT 0, ' \
                 '    PRIMARY KEY (`word`(255)) ' \
                 ' ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4'
        self.execute(query, ())

    def words_insert_garbword(self, word, reflag):
        """ inserts a garbage word into the garbword table """
        query = 'INSERT INTO garbwords (`word`, `count`, `regexflag`) ' \
                'VALUES ("{}", 1, {}) ' \
                'ON DUPLICATE KEY UPDATE count=count + 1'.format(word, reflag)
        return self.execute(query, ())

    def words_remove_garbword(self, word):
        query = f'DELETE FROM garbwords WHERE `word` = \'{word}\''
        return self.execute(query, ())

    def find_word(self, word, table='garbwords'):
        """ check if word exists in garbwords table """
        regex1 = r'.*\'.*'
        if re.match(regex1, word) is not None:
            word = word.replace('\'', '\\\'')
        regex2 = r'.*\\.*'
        if re.match(regex2, word) is not None:
            word = word.replace('\\', '\\\\')
        word = word.lower()

        query = f'SELECT word FROM {table} WHERE word = \'{word}\' LIMIT 1'

        cur = self.execute(query, ())
        all = cur.fetchall()

        # collation causes the database to greedy match foreign characters
        # match confirmed when the returned result equals the queried word
        for result in all:
            # mysql-connector converts numbers to ints and floats, causing
            # string comparisons to sometimes fail e.g. "01.50" != "1.5"
            if isinstance(result['word'], int):
                try:
                    if result['word'] == int(word):
                        return True
                except ValueError:
                    print(f'\nWarning: word "{word}" is not an integer')
            elif isinstance(result['word'], float):
                try:
                    if result['word'] == float(word):
                        return True
                except ValueError:
                    print(f'\nWarning: word "{word}" is not a float')
            else:
                if str(result['word']).lower() == word:
                    return True
        return False

    def get_all_words(self, table='garbwords'):
        """ get all words in garbwords without regex flag """
        query = f'SELECT word FROM {table} WHERE regexflag = 0'
        cur = self.execute(query, ())
        all = cur.fetchall()
        return all

    def get_word_count(self, reflag, table='garbwords'):
        """ returns garbword count """
        query = f'SELECT count(word) FROM {table} WHERE regexflag = {reflag}'
        cur = self.execute(query, ())
        count = cur.fetchone().get('count(word)')
        return count

    def commit(self):
        self.db.commit()
