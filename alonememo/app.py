from flask import Flask, render_template, jsonify, request
from bson.objectid import ObjectId

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client.dbjungle  # dbjungle이라는 db생성


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/memo", methods=["GET"])  # /memo url로 들어가면 mongoDB의 모든
# 값들을 찾아서 _id제외한 다음에 json 형식으로 화면에 출력해준다.
def read_articles():
    # 1. 모든 document 찾기 & _id값은 출력에서 제외
    result = list(db.articles.find({}, {"_id": 0}))
    # 2. articles라는 키 값으로 영화정보 내려주기
    return jsonify({"result": "success", "articles": result})


@app.route("/memo", methods=["POST"])
def post_article():
    # 1. 클라이언트로부터 데이터 받기
    url_receive = request.form["url_give"]  # 클라이언트로부터 url 받는 부분
    comment_receive = request.form["comment_give"]  # 클라이언트로부터 comment 받는 부분
    # 2. meta tag 스크래핑하기
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
    }
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, "html.parser")

    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('meta[property="og:title"]')
    og_description = soup.select_one('meta[property="og:description"]')

    url_title = og_title["content"]
    url_description = og_description["content"]
    url_image = og_image["content"]

    article = {
        "url": url_receive,
        "title": url_title,
        "desc": url_description,
        "image": url_image,
        "comment": comment_receive,
    }
    # 3. mongoDB에 데이터 넣기
    db.articles.insert_one(article)

    return jsonify({"result": "success"})


# APIs
@app.route("/api/del", methods=["POSt"])
def del_article():
    title_give = request.form["title"]
    db.articles.delete_one({"title": title_give})
    return jsonify({"result": "success"})


@app.route("/api/update/<idx>", methods=["GET", "POST"])
def update_article(idx):
    # 수정요청이 GET으로 오면 요청온 id로 document 뽑아서 수정할 놈들 보내준다.
    if request.method == "GET":
        article = db.articles.find_one({"_id": ObjectId(idx)})
        return render_template("edit.html", article=article)
    # 수정을 다 하고 POST로 오면 수정하고 db에 저장해준다.
    else:
        return render_template("edit.html")


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
