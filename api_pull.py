import requests
import html
import sqlite3
from requests_oauthlib import OAuth1Session
from config import api_info
import json

def main():
    conn = init_db()
    pull_latest_from_reddit(conn)
    # print(read_image_data(conn, "wj5d7830skq81.jpg"))

    # twitter_oauth_generation()
    auth = twitter_sign_in()
    print(upload_photo(conn, auth))

    # response = auth.post(
    #     "https://api.twitter.com/2/tweets",
    #     json = {"text": "Hello, world x6!"},
    # )

def twitter_oauth_generation():
    consumer_key = api_info["api_key"]
    consumer_secret = api_info["api_secret_key"]

    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

    try:
        r = oauth.fetch_request_token(request_token_url)
    except ValueError:
        print("Invalid response from Twitter")
        return

    resource_owner_key = r.get('oauth_token')
    resource_owner_secret = r.get('oauth_token_secret')
    print("Got OAuth token: %s" % resource_owner_key)

    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)
    print("Please go here and authorize: %s" % authorization_url)
    verifier = input('Please input the verifier: ')

    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(consumer_key,
                            client_secret=consumer_secret,
                            resource_owner_key=resource_owner_key,
                            resource_owner_secret=resource_owner_secret,
                            verifier=verifier)

    oauth_tokens = oauth.fetch_access_token(access_token_url)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]

    with open("oauth_info.json", "w") as f:
        json.dump({"consumer_key": consumer_key,
                 "consumer_secret": consumer_secret,
                 "access_token": access_token,
                 "access_token_secret": access_token_secret}, f, indent=4)

    print("Generated oauth link information")

def twitter_sign_in():
    with open("oauth_info.json", "r") as f:
        oauth_info = f.read()
        oauth_info = eval(oauth_info)

    oauth = OAuth1Session(
        oauth_info["consumer_key"],
        client_secret=oauth_info["consumer_secret"],
        resource_owner_key=oauth_info["access_token"],
        resource_owner_secret=oauth_info["access_token_secret"],
    )

    return oauth

def upload_photo(conn, auth):
    sql = """SELECT * FROM images WHERE posted = 0 AND downloaded = 0 ORDER BY RANDOM() LIMIT 1"""
    cur = conn.cursor()
    cur.execute(sql)
    row = cur.fetchall()[0]

    with open("images/" + row[0], "wb") as f:
        f.write(requests.get(row[1]).content)
    
    media_api = "https://upload.twitter.com/1.1/media/upload.json"
    media = auth.post(media_api, files={"media": open("images/" + row[0], "rb"), "media_category": "tweet_image"})
    print(media.text)

    # update = """UPDATE images SET downloaded = 1 WHERE file_name = ?"""

def pull_latest_from_reddit(conn):
    api_url = "https://www.reddit.com/r/2meirl4meirl/hot/.json"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}
    res = requests.get(api_url, headers=headers)
    res_json = res.json()

    image_urls = []

    for i in res_json["data"]["children"]:
        if "preview" in i["data"]:
            l = []
            image_url = i["data"]["preview"]["images"][0]["source"]["url"]
            op_url = i["data"]["permalink"]
            fixed_url = html.unescape(image_url)
            l.append(fixed_url)
            l.append(op_url)
            image_urls.append(l)

    for i in image_urls:
        file_name = i[0].split("/")[3].split(".")[0]
        file_type = "." + i[0].split("/")[3].split(".")[1].split("?")[0]
        file_full_name = file_name + file_type

        data = (file_full_name, i[0], i[1], False, False, False)
        insert_image_data(conn, data)

    conn.commit()

def init_db():
    conn = create_connection("image_data.db")
    while (not create_table(conn)):
        print("Dropping table")
        conn.execute("DROP TABLE IF EXISTS images")
    print("Created table")
    return conn

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print("Unable to make DB connection" + str(e))
        exit(0)
    finally:
        return conn

def create_table(conn):
    image_data_table  = """CREATE TABLE images (
                            file_name text PRIMARY KEY,
                            url text NOT NULL,
                            op_url text NOT NULL,
                            posted boolean NOT NULL,
                            downloaded boolean NOT NULL,
                            deleted boolean NOT NULL
                        );"""
    try:
        c = conn.cursor()
        c.execute(image_data_table)
        return True
    except sqlite3.Error as e:
        print(e)
        return False

def insert_image_data(conn, data):
    sql = ''' INSERT INTO images(file_name, url, op_url, posted, downloaded, deleted)
              VALUES(?,?,?,?,?,?) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, data)
        return cur.lastrowid
    except:
        print("Error inserting data")

def read_image_data(conn, file_name):
    sql = ''' SELECT * FROM images WHERE file_name = ? '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (file_name,))
        return cur.fetchone()
    except:
        print("Error reading data")

if __name__ == "__main__":
    main()