rss\_reader
===========

## Overview

rss\_reader is a simple script implementing a basic rss feed notification
system. This was a small project to get more familiar with psycopg2.
If you're looking for a good rss reader, you could install the
gnome-extension RSS Feed or use one packaged for your distribution.

The idea is directly taken from this article: [1]
Unlike the original implementation this script uses a postgresql database,
a desktop notification and a command line interface.

## Prerequisites

The following packages are required to use this script:

* psycopg2
* feedparser

You also need a postgresql database and a fitting configuration file, e. g.

``` 
[postgresql]
host = '0.0.0.0'
db = 'test'
user = 'youruser'
pass = 'yourpassword'
```

## Usage

Once you have created a database and a configuration file 
run 
``` python rss_reader.py -c CONFIG```
to use the preconfigured settings. Replace CONFIG with your own configuration
file.
Run
``` python rss_reader.py -h```
to get a complete listing of all possible options.

[1] https://fedoramagazine.org/never-miss-magazines-article-build-rss-notification-system/
and the corresponding code on github:
https://github.com/cverna/rss_feed_notifier


