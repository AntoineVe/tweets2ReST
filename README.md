# tweets2ReST
Transforms tweets in ReST (for pelican static site generator).
Handles URL, mentions and pictures.
Records only "real tweet" (no direct mentions, no retweets).

# Thanks to...
* [Python](https://www.python.org/)
* [jpcw](https://github.com/jpcw) for telling me Python
* [Twitter API](https://dev.twitter.com/overview/api)
* Python's modules :
  * [twitter](https://pypi.python.org/pypi/twitter)
  * [urlextract](https://pypi.python.org/pypi/urlextract)
  * [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
  * core modules : `json`, `datetime`, `dateutil`, `locale`, `PIL`, `io`, `urllib.request`, `os`, `argparse`, `logging` and `urllib.request`
* [Pelican static site generator](http://docs.getpelican.com)

# Usage
1. Install `python3`
2. Install third-party required modules (see `requirements.txt`) [This explains how to do](https://docs.python.org/3/installing/index.html)
3. Create a twitter app <https://apps.twitter.com/> and create an access token (copy all credentials somewhere safe)
4. copy the script `tweets2rst.py` in your "pelican" directory
5. `python3 tweets2rst.py token token_key con_secret con_secret_key twitter_name`
  * Optionnaly, you can use `-D` to see some (not really useful) debug message
  * Optionnaly, create some cron or systemd-timers task to populate your blog content every 15 minutes (see [API rate limits](https://dev.twitter.com/rest/public/rate-limiting)). **I encourage to do this because there is a limit how deep in twitter where API can dive and retrieve tweets** (i.e. : you can loose some tweets).

# Licence
This work is free. You can redistribute it and/or modify it under the terms of the Do What The Fuck You Want To Public License, Version 2, as published by Sam Hocevar. See the COPYING file for more details.
