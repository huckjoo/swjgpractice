import requests
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client.dbjungle

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index2.html")


# APIs
@app.route("/api/list")
def show_stars():
    star = list(db.mystar.find({}, {"_id": 0}).sort("like", -1))
    return jsonify({"result": "success", "star_list": star})


@app.route("/api/like", methods=["POST"])
def star_like():
    name = request.form["star_name"]
    target_star = db.mystar.find_one({"name": name})
    new_like = target_star["like"] + 1
    db.mystar.update_one({"name": name}, {"$set": {"like": new_like}})
    return jsonify({"result": "success"})


@app.route("/api/del", methods=["POST"])
def star_del():
    star_name = request.form["star_name"]
    db.mystar.delete_one({"name": star_name})
    return jsonify({"result": "success"})


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
