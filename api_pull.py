import requests
import json
import html
import os
import sqlite3

def main():
    conn = init_db()
    pull_from_reddit(conn)
    print(read_image_data(conn, "wj5d7830skq81.jpg"))

def pull_from_reddit(conn):
    api_url = "https://www.reddit.com/r/2meirl4meirl/hot/.json"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}
    res = requests.get(api_url, headers=headers)
    res_json = res.json()

    image_urls = []

    for i in res_json["data"]["children"]:
        if "preview" in i["data"]:
            image_url = i["data"]["preview"]["images"][0]["source"]["url"]
            fixed_url = html.unescape(image_url)
            image_urls.append(fixed_url)

    for i in image_urls:
        file_name = i.split("/")[3].split(".")[0]
        file_type = "." + i.split("/")[3].split(".")[1].split("?")[0]
        file_full_name = file_name + file_type

        if (os.path.isfile("images/" + file_full_name) == False):
            # with open("images/" + file_full_name, "wb") as f:
            #     f.write(requests.get(i).content)
            data = (file_full_name, i, False, False, False)
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
    sql = ''' INSERT INTO images(file_name, url, posted, downloaded, deleted)
              VALUES(?,?,?,?,?) '''
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