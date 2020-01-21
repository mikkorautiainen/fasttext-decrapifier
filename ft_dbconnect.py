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

import mysql.connector
import re


DB = {
    'DB': 'decrapper',
    'TABLE': 'garbwords',
    'USER': 'root',
    'PASSWORD': '',
    'HOST': 'localhost',
    'PORT': '3306'
}
DATABASE = DB


class MysqlDB:
    db = None

    def __init__(self):
        """ connect to the database """
        self.db = {}
        try:
            self.db = mysql.connector.connect(user=DATABASE['USER'],
                                              password=DATABASE['PASSWORD'],
                                              host=DATABASE['HOST'],
                                              port=DATABASE['PORT'],
                                              database=DATABASE['DB'],
                                              use_pure=True)
            # self.connect()  # sets cls.db
            MysqlDB.db = self.db
        except:
            print("Failed to connect to database {}".format(DATABASE['DB']))
            self.db = mysql.connector.connect(user=DATABASE['USER'],
                                              password=DATABASE['PASSWORD'],
                                              host=DATABASE['HOST'],
                                              port=DATABASE['PORT'],
                                              use_pure=True)
            # self.connect()  # sets cls.db
            MysqlDB.db = self.db

    def execute(self, sql, values):
        """ execute query with params and return cursor """
        try:
            self.cursor = self.db.cursor(dictionary=True, buffered=True)
            self.cursor.execute(sql, values)
            return self.cursor
        except mysql.connector.Error as err:
            print(f"Something went wrong: {err} on {sql}")
        return None

    def fetchall(self):
        """ calling fetchall on cursor """
        return self.cursor.fetchall()

    def fetchone(self):
        """ calling fetchone on cursor """
        return self.cursor.fetchone()

    def initialize_database(self):
        """ initialize mysql database from ground 0 """
        query = f"DROP DATABASE IF EXISTS {DATABASE['DB']}"
        self.execute(query, ())

        print(f"Creating database {DATABASE['DB']}")
        query = f"CREATE DATABASE {DATABASE['DB']}"
        self.execute(query, ())

        # reinitialize database connection
        MysqlDB.__init__(self)

        query = f'CREATE TABLE `{DATABASE["TABLE"]}` ( ' \
                 '    `word` text NOT NULL, ' \
                 '    `count` int(11) NOT NULL DEFAULT 0, ' \
                 '    `regexflag` tinyint(4) NOT NULL, ' \
                 '    `input` text DEFAULT \'\', ' \
                 '    `value` float DEFAULT 0, ' \
                 '    PRIMARY KEY (`word`(255)) ' \
                 ' ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 '
        self.execute(query, ())

    def words_insert_garbword(self, word, reflag):
        """ inserts a garbage word into the garbword table """
        query = 'INSERT INTO garbwords (`word`, `count`, `regexflag`) ' \
                'VALUES (\'{}\', 1, {}) ' \
                'ON DUPLICATE KEY UPDATE count=count + 1'.format(word, reflag)
        return self.execute(query, ())

    def words_remove_garbword(self, word):
        query = f'DELETE FROM garbwords WHERE `word` = \'{word}\''
        return self.execute(query, ())

    def find_word(self, word, table='garbwords'):
        """ Checks if word exists in arg table. """
        regex1 = r'.*\'.*'
        regex2 = r'.*\\.*'
        if re.match(regex1, word) is not None:
            word = word.replace('\'', '\\\'')
        elif re.match(regex2, word) is not None:
            word = word.replace('\\', '\\\\')

        query = f'SELECT word FROM {table} WHERE word = \'{word}\' LIMIT 1'
        return self.execute(query, ())

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


if __name__ == '__main__':
    """ test """
    db = MysqlDB()

    db.words_insert_garbword('aaaa0', 0)
    db.words_insert_garbword('aaaa0', 0)
    db.words_insert_garbword('aaaa0', 0)
    db.commit()

    cur = db.execute('SELECT * FROM garbwords', ())
    all = db.fetchall()
    print(all)

    x = db.find_word('duck')
    print(x)
