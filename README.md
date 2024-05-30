# FIDE Players Viewer

View the list of FIDE players and their ratings. The source of the data is the [FIDE website](https://ratings.fide.com/download.phtml).

## Architecture

- The data is downloaded from the FIDE website and stored in a SQLite database using `players.py`
- API is built with [Datasette](https://datasette.io/) and published on `fly.io`
- `index.html` is a simple HTML page that uses the API to display the list of players
- The Datasette API is available at [https://fide-players.fly.dev/players](https://fide-players.fly.dev/players)
- The HTML page is available at [https://kamicut.cc/fide-players/](https://kamicut.cc/fide-players/)
- TODO: A Github Action to update the data daily
