fastText Decrapifier
========

 This tool removes non-Finnish words from the Facebook's fastText (https://fasttext.cc/) vec-file. This reduces the vec-file size for an efficient use of the resource.
 The Python code can be customized easily to work with other languages. Please submit a pull request or share your changes with us if this helps you with your language. 

<!-- TOC depthFrom:1 depthTo:2 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Prerequisite](#prerequisite)
- [Installation](#installation)
- [Data and fastText](#data-and-fasttext)
- [Run CLI](#run-cli)
  - [Initialize database](#initialize-database)
  - [Regex](#regex)
  - [Nearest neighbor iteration](#nearest-neighbor-iteration)
  - [Spell checker](#spell-checker)
  - [Create vec-file](#create-vec-file)
- [License](#license)

<!-- /TOC -->


# Prerequisite

- Python 3.6 or later
- virtualenv
- fastText executable
- MySQL or MariaDB
- Voikko spell checker

&nbsp;
# Installation

```
git clone https://github.com/mikkorautiainen/fasttext-decrapifier
cd fasttext-decrapifier
virtualenv --python=python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
```

&nbsp;
# Data and fastText

The vanilla code expects the following files in the project root:
   1. fastText executable
   2. word vectors in bin-format
   3. word vectors in vec-format
&nbsp;
You can symbolic link your files located elsewhere to the project root like so:
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
Currently the database connection setting is hardcoded in ft_dbconnect.py file as below:
```
DB = {
    'DB': 'decrapper',              # database name
    'TABLE': 'garbwords',
    'USER': 'root',
    'PASSWORD': '',
    'HOST': 'localhost',
    'PORT': '3306'                  # Set to empty string for default.
}
```
It is best to change the USER and the PASSWORD to your MySQL setting for the decrapifier to connect to your MySQL instance.
Once you are done with the change of the user and the password, please run the "init" action to build the database and the table for the decrapifier. 
```
python decrapper.py --action init
```
## Regex
Finds non-language word using regex
```
python decrapper.py --action regex
```
## Nearest neighbor iteration
Generates non-language garbage word and find thier nearest neighbors in the vec-file
```
python decrapper.py --action nn_query
```
## Spell checker
The nearest neighbor iteration finds words that are rarely used but correct in the target language vocabulary. The spell checker removes these words form the garbage word table (garbwords) in the database.

```
python decrapper.py --action spell_checker
```
## Create vec-file
Checks every word in the vec-file against the database.
This sub-command creates a new vec-file with the non-language words excluded.
```
python decrapper.py --action remove
```

&nbsp;
# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
