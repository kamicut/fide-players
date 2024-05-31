# ![Chess Icon](./docs/assets/board.png) FIDE Players API & Viewer

View the list of FIDE players and their ratings. Originally created for use for [Keshmat Chess School](https://keshmat.org/).

## Architecture

- The data is downloaded from the FIDE website and stored in a SQLite database using `players.py`
- API is built with [Datasette](https://datasette.io/) and published on `fly.io`
- `index.html` is a simple HTML page that uses the API to display the list of players
- The Datasette API is available at [https://fide-players.fly.dev/players](https://fide-players.fly.dev/players)
- The HTML page is available at [https://kamicut.cc/fide-players/](https://kamicut.cc/fide-players/)
- A Github Action is used to update the data weekly and deploy the API and HTML page

## Run locally

Clone the repository and install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the script to download the data and create the database:

```bash
curl -O http://ratings.fide.com/download/players_list_xml.zip
unzip players_list_xml.zip
mv players_list_xml_foa.xml players.xml
python players.py players.xml players.db
```

Run the API locally:

```bash
datasette players.db -m metadata.json
```

Open the HTML page in a browser:

```bash
open index.html
```

## Attributions

- Data from [FIDE](https://ratings.fide.com/download.phtml)
- Icons <a href="https://www.flaticon.com/free-icons/chess" title="chess icons">Chess icons created by Andrejs Kirma - Flaticon</a>

# License
