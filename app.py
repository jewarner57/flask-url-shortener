from flask import Flask, request, render_template, redirect, url_for, flash
from flask_pymongo import PyMongo, ObjectId
import os
import binascii
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.config["MONGO_URI"] = "mongodb://localhost:27017/url_shortener"
mongo = PyMongo(app)


@app.route("/")
def homepage():
    """Homepage redirects to shorten page"""
    return redirect(url_for('shorten'))


@app.route("/shorten", methods=["GET", "POST"])
def shorten():
    """A page with a form to enter the url the user wants shortened"""

    if request.method == "POST":

        dest_url = request.form.get("url")

        if "http://" not in dest_url and "https://" not in dest_url:
            flash("Make sure you enter https:// before the url")
            return render_template("shorten.html")

        urlExists = mongo.db.shortLinks.find({"dest": dest_url})

        if urlExists.count() > 0:
            return redirect(url_for("getUrl", shortId=urlExists[0]["_id"]))
        else:

            short = binascii.b2a_hex(os.urandom(3)).decode("utf-8")

            shortLink = {
                "dest": dest_url,
                "short": short
            }

            newShort = mongo.db.shortLinks.insert_one(shortLink)

            return redirect(url_for("getUrl", shortId=newShort.inserted_id))

    else:
        return render_template("shorten.html")


@ app.route("/getUrl/<shortId>")
def getUrl(shortId):
    """Returns the shortened version of the url"""

    shortData = mongo.db.shortLinks.find_one_or_404({"_id": ObjectId(shortId)})

    context = {
        "dest": shortData['dest'],
        "short": f"/r/{shortData['short']}"
    }

    return render_template("getUrl.html", **context)


@ app.route("/r/<shortLink>")
def useLink(shortLink):
    """Sends the user to the destination of the shortlink entered"""
    shortData = mongo.db.shortLinks.find_one_or_404({"short": shortLink})
    print(shortData["dest"])
    return redirect(shortData["dest"])


if __name__ == '__main__':
    app.run(debug=True)
