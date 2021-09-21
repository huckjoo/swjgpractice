import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client.prmemo
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index2.html")


@app.route("/memo", methods=["GET"])
def listing():  # db에서 값들을 불러와서 ajax에게 넘긴다.
    # 1. db에서 모든것을 불러와서 list화한다. _id빼고
    articles = list(db.articles.find({}, {"_id": 0}))
    # 2. json으로 결과값을 넘긴다.
    return jsonify({"result": "success", "articles": articles})


@app.route("/memo", methods=["POST"])
def saving():
    # 1. post로 url, comment 받아오기
    url = request.form["url_get"]
    comment = request.form["comment_get"]
    # 2. web 스크래핑 해오기
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
    }
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, "html.parser")
    og_title = soup.select_one("meta[property='og:title']")
    og_image = soup.select_one("meta[property='og:image']")
    og_desc = soup.select_one("meta[property='og:description']")

    title = og_title["content"]
    image = og_image["content"]
    desc = og_desc["content"]
    # 3. article이라는 collection에 저장
    db.articles.insert_one(
        {"title": title, "url": url, "image": image, "desc": desc, "comment": comment}
    )
    return jsonify({"result": "success"})


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
