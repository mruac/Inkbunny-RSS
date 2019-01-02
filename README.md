# Inkbunny-RSS

My first proper project, inspired by the RSS function in [boothale's FurAffinity API "FAExport"](https://github.com/boothale/faexport)

See IB2rss.py for comments in the code explaining parts of the code.

Essentially it takes the output from Inkbunny's search API and converts it into a usable RSS file that can be used locally. Please refer to InkBunny's API [documentation](https://wiki.inkbunny.net/wiki/API#Search) for more information and possible flags.

## Usage

There are two ways to use Inkbunny-RSS, via the Flask `app.py` or the console based `IB2rss.py`

**Requirements:** xml.etree.ElementTree, urllib, re, datetime. `IB2rss.py` needs sys, and the Flask `app.py` needs flask.

The Flask app can be executed by running ~/web$ `python app.py` and can then be accessible from http://127.0.0.1:5000/

IB2rss.py can be used by running `python IB2rss.py "https://inkbunny.net/api_search.php?[flags]"`

Ensure the URL is placed within the quotes as the shell will treat the "&" as a new command and create an rss file based on all latest posts.

_________________
Notes: I plan to release this in Heroku, but I don't think it is ready just yet. Since this is my first personal project, I still need to learn how online feed readers will interact with the Flask app.
