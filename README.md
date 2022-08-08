# Inkbunny-RSS

My first proper project, inspired by the RSS function in [boothale's FurAffinity API "FAExport"](https://github.com/boothale/faexport)

Essentially it takes the output from Inkbunny's search API and converts it into a usable RSS file that can be used locally. Please refer to InkBunny's API [documentation](https://wiki.inkbunny.net/wiki/API#Search) for more information and possible flags.

## Local Install

Install requirements
`pip install -r requirements.txt`

Create `config.ini` in the directory with the following lines:
1. `[IB]`
2. `sid = SIDHERE`

Start Redis cache server
`redis-server`

Start Flask web app
`python3.10 app.py`

## Heroku

Deploy directory to Heroku

Add [`Heroku Data for Redis®`](https://elements.heroku.com/addons/heroku-redis) add-on for Redis cache

Add SID as environment variable and set to your SID.
