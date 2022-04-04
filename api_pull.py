import requests
import html
import sqlite3
from requests_oauthlib import OAuth1Session
from config import api_info
import json
import time

def main():
    
    conn = create_connection("image_data.db")

    while(True):
        pull_latest_from_reddit(conn)
        # twitter_oauth_generation()
        auth = twitter_sign_in()
        full_file_name = upload_random_photo(conn, auth)
        if (full_file_name is not None):
            print(read_image_data(conn, full_file_name))
            tweet_uploaded_photo(conn, auth, full_file_name)
            print(read_image_data(conn, full_file_name))
        time.sleep(900)

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

def upload_random_photo(conn, auth):
    sql = """SELECT * FROM images WHERE posted = 0 AND downloaded = 0 ORDER BY RANDOM() LIMIT 1""" 
    cur = conn.cursor()
    cur.execute(sql)
    row = cur.fetchall()[0]

    if (row == None):
        print("No new images to upload")
        return None

    with open("images/" + row[0], "wb") as f:
        f.write(requests.get(row[2]).content)
    
    media_api = "https://upload.twitter.com/1.1/media/upload.json"
    media = auth.post(media_api,
                      files={"media": open("images/" + row[0], "rb"),
                             "media_category": "tweet_image"})
    
    if (media.status_code == 200):
        update = """UPDATE images SET downloaded = 1, twitter_media_id = ? WHERE file_name = ?"""
        media_id = media.json()["media_id_string"]
        cur = conn.cursor()
        cur.execute(update, (media_id, row[0]))
        conn.commit()
        return row[0]
    else:
        print(media.text)
        print("Error uploading image")
        exit(0)

def tweet_uploaded_photo(conn, auth, file_name):
    get_row = """SELECT * FROM images WHERE file_name = ? LIMIT 1"""
    cur = conn.cursor()
    cur.execute(get_row, (file_name,))
    row = cur.fetchall()[0]

    tweet_api = "https://api.twitter.com/2/tweets"
    tweet_object_image = {
        "text": row[1] + " redd.it/" + row[3],
        "media": {
            "media_ids": [row[6]]
        }
    }
    tweet_headers = {"Content-Type": "application/json"}
    response = auth.post(
        tweet_api,
        headers=tweet_headers,
        json=tweet_object_image
    )

    if (response.status_code == 201):
        update = """UPDATE images SET posted = 1 WHERE file_name = ?"""
        cur = conn.cursor()
        cur.execute(update, (file_name,))
        conn.commit()
        print("Tweeted image")

    else:
        print(response.text)
        print("Error tweeting image")
        exit(0)

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
            op_url = i["data"]["id"]
            post_title = i["data"]["title"]
            fixed_url = html.unescape(image_url)
            l.append(fixed_url)
            l.append(op_url)
            l.append(post_title)
            image_urls.append(l)

    for i in image_urls:
        file_name = i[0].split("/")[3].split(".")[0]
        file_type = "." + i[0].split("/")[3].split(".")[1].split("?")[0]
        file_full_name = file_name + file_type

        data = (file_full_name, i[2], i[0], i[1], False, False, False)
        insert_image_data(conn, data)

    conn.commit()

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connection to SQLite DB successful")
        if create_table(conn):
            print("Table created")
        else:
            print("Table already exists")
    except sqlite3.Error as e:
        print("Unable to make DB connection " + str(e))
        exit(0)
    finally:
        return conn

def create_table(conn):
    image_data_table  = """CREATE TABLE IF NOT EXISTS images (
                            file_name text PRIMARY KEY,
                            post_title text NOT NULL,
                            url text NOT NULL,
                            id text NOT NULL,
                            posted boolean NOT NULL,
                            downloaded boolean NOT NULL,
                            twitter_media_id text,
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
    sql = ''' INSERT INTO images(file_name, post_title, url, id, posted, downloaded, deleted)
              VALUES(?,?,?,?,?,?,?) ON CONFLICT DO NOTHING '''
    try:
        cur = conn.cursor()
        cur.execute(sql, data)
        conn.commit()
        return True
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