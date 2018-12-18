# Inkbunny-RSS

My first proper project, inspired by [boothale's FurAffinity API "FAExport"](https://github.com/boothale/faexport)

See IBxml2rss.py for comments in the code explaining parts of the code.

Essentially it takes the output from Inkbunny's search API. Please refer to their [documentation](https://wiki.inkbunny.net/wiki/API#Search) for more information and flags.

## Usage
`python IBxml2rss.py https://inkbunny.net/api_search.php?sid=[SID]&text=[Search query]`

__________________________
I may get around to learning or choosing a web framework to make this script deployable and working with online RSS clients in the future. (If you would like to help, I would gladly accept merge requests!)
In the mean time, feel free to use this code to generate an rss file to use in a local Feed Reader program.
