from flask import Flask, render_template

from archive.query import list_discs
from archive.album_query import show_disc

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", discs=list_discs())


@app.route("/disc/<accession>")
def disc(accession):
    return render_template(
        "disc.html",
        accession=accession,
        result=show_disc(accession),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)