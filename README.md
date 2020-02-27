fastText Decrapifier
========

 This tool removes non-Finnish words from Facebook's fastText (https://fasttext.cc/) vec-file.\
 The configuration file can be easily customized to work with any languages. If this helps you with your language, please submit a pull request or share your changes with us.

<!-- TOC depthFrom:1 depthTo:2 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Prerequisite](#prerequisite)
- [Installation](#installation)
- [Data and fastText](#data-and-fasttext)
- [Running CLI](#running-cli)
  - [Database initialization](#database-initialization)
  - [Regex](#regex)
  - [Nearest neighbor iteration](#nearest-neighbor-iteration)
  - [Spell checker](#spell-checker)
  - [Create vec-file](#create-vec-file)
  - [Create vocabulary](#create-vocabulary)
- [License](#license)

<!-- /TOC -->


&nbsp;
# Prerequisite

- Python 3.6 or later
- fastText executable
- MySQL or MariaDB
- Voikko spell checker
- libvoikko library 4.3 or later

&nbsp;
# Installation

```
git clone https://github.com/mikkorautiainen/fasttext-decrapifier
cd fasttext-decrapifier
python3.6 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

&nbsp;
# Data and fastText

The code expects the following files to be in the project root:
   1. fastText executable
   2. word vectors in bin-format
   3. word vectors in vec-format

&nbsp;
You can symbolically link the files to the project root:
```
ln -s /usr/src/fastText/fasttext .
ln -s /data/cc.fi.300.bin .
ln -s /data/cc.fi.300.vec .
```

&nbsp;
# Running CLI

  The decrapifier tool uses sub-commands (specified as a command option) to run the non-language word removal steps.

&nbsp;
## Database initialization
The database parameters are specified in [config.json](config.json):
```
  "DATABASE": {
    "dbname":  "decrapper",
    "table": "garbwords",
    "user":  "root",
    "password": "",
    "host": "localhost",
    "port": "3306",
    "charset": "utf8", 
    "collation": "utf8_estonian_ci"
  }
```
Note: It is crucial that you set the correct collation for your language, otherwise the program will fail to differentiate your language’s special characters and accents. The collation must be case-insensitive.\
For example the Finnish language requires Estonian collation. The wrong collation will cause the program to remove “määrä” when it should only remove “maara” or remove “kasino” when it should only remove “kašino”.

&nbsp;
Once you are done changing the user and the password, please run the "init" action to create the database and table.
```
python decrapper.py --action init
```
## Regex
Finds non-language word using regex
```
python decrapper.py --action regex
```
## Nearest neighbor iteration
Generates non-language garbage word and find their nearest neighbors in the vec-file
```
python decrapper.py --action nn_query
```
## Spell checker
The nearest neighbor iteration finds words that are rarely used but correct in the target language vocabulary.\
The spell checker removes these words from the garbage word table (garbwords) in the database.
```
python decrapper.py --action spell_checker
```
## Create vec-file
Checks every word in the vec-file against the database.\
This sub-command creates a new vec-file with the non-language words excluded.
```
python decrapper.py --action remove
```
## Create vocabulary
(Optional step) Replaces the word-vectors with the word’s lexical category and plurality.\
This sub-command creates a new tab-delimited text file with the uncased vocabulary and lexical information.
```
python decrapper.py --action vocabulary
```

&nbsp;
# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
