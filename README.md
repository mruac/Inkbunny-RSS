# Inkbunny-RSS

My first proper project, inspired by the RSS function in [boothale's FurAffinity API "FAExport"](https://github.com/boothale/faexport)

Essentially it takes the output from Inkbunny's search API and converts it into a usable RSS file that can be used locally. Please refer to InkBunny's API [documentation](https://wiki.inkbunny.net/wiki/API#Search) for more information and possible flags.

If no Session ID (SID) is set, the app will login as a guest user on Inkbunny.

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

## Docker deployment

```docker-compose up --detach```

Usable environment variables (Set them before running the docker compose command):

* `SID` - Inkbunny's Session identifier.
* `PORT` - Port to access InkBunny-RSS on. Defaults to port `80`, set to a different port if your network is already using port `80`.

The instance can be accessed by `http://localhost:${PORT}`

## Heroku

Deploy directory to Heroku

Add [`Heroku Data for Redis®`](https://elements.heroku.com/addons/heroku-redis) add-on for Redis cache

Add SID as environment variable and set to your SID.
