from package.models import *
from package.migrations import *
from package.config.config import *
from requests_oauthlib import OAuth1Session
import requests
import json
import time
import os

def main():
    # Run Migrations
    if (Migration1.migrate()):
        print("Table created or already exists.");

    auth = twitter_sign_in();
    while (not auth):
        if (twitter_oauth_gen()):
            auth = twitter_sign_in();

    while (True):
        save_latest_posts_from_reddit(subreddit);

        image = Image.fetchRandomImage();

        print(image);

        if (image):
            if (download_photo(image)):
                image.save();
                if (Upload(auth, image).upload_and_tweet_photo()):
                    print("Tweeted photo: ", image);
                    image.save();
                else:
                    print("Failed to upload photo");
            else:
                print("Failed to download photo");
        else:
            print("Failed to fetch random image, no new images available");
        time.sleep(3600);

def twitter_sign_in():
    with open("package/config/oauth_info.json", "r") as f:
        oauth_info = f.read()
        oauth_info = eval(oauth_info)

    auth = OAuth1Session(
        oauth_info["consumer_key"],
        client_secret = oauth_info["consumer_secret"],
        resource_owner_key = oauth_info["access_token"],
        resource_owner_secret = oauth_info["access_token_secret"],
    )

    test_url = "https://api.twitter.com/1.1/account/verify_credentials.json";
    resp = auth.get(test_url);

    if (resp.status_code == 401):
        return False;
    elif (resp.status_code == 200):
        return auth;
    else:
        print("Twitter auth error: " + resp.status_code);
        exit(0);

def twitter_oauth_gen():
    consumer_key = api_info["api_key"];
    consumer_secret = api_info["api_secret_key"];

    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write";
    auth_url = "https://api.twitter.com/oauth/authorize";
    access_token_url = "https://api.twitter.com/oauth/access_token";

    oauth = OAuth1Session(consumer_key,
    client_secret = consumer_secret);

    try:
        res = oauth.fetch_request_token(request_token_url);
    except ValueError:
        print("Invalid response from Twitter");
        return False;

    resource_owner_key = res.get('oauth_token');
    resource_owner_secret = res.get('oauth_token_secret');
    print("Got Resource Owner.");

    confirm_auth_url = oauth.authorization_url(auth_url);
    print("Please go here and authorize: %s" % confirm_auth_url);
    
    verifier = input("Please input the verifier: ");

    oauth = OAuth1Session(consumer_key,
                            client_secret=consumer_secret,
                            resource_owner_key=resource_owner_key,
                            resource_owner_secret=resource_owner_secret,
                            verifier=verifier);
    oauth_tokens = oauth.fetch_access_token(access_token_url);

    with open("package/config/oauth_info.json", "w") as f:
        json.dump({"consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "access_token": oauth_tokens["oauth_token"],
            "access_token_secret": oauth_tokens["oauth_token_secret"]
        });

    return True;

def save_latest_posts_from_reddit(subreddit):
    api_url = "https://www.reddit.com/r/" + subreddit + "/hot/.json"
    headers = {"User-Agent": "2meirl4meirlTweetBot"};
    res = requests.get(api_url, headers=headers);
    res_json = res.json();
    
    if (res.status_code != 200):
        print("Could not get data from Reddit's servers, will try again later.");
        return False;

    for i in res_json["data"]["children"]:
        if "preview" in i["data"] and i["data"]["is_video"] == False:
            image_url = i["data"]["url"];
            file_name = image_url.split("/")[-1];
            post_title = i["data"]["title"];
            op_url = i["data"]["id"];
            upvotes = i["data"]["ups"];
            
            image = Image.fetchImageByFileName(file_name)

            if (image):
                image.upvotes = upvotes;
            else:
                image = Image(file_name, post_title, image_url, op_url, False, False, None, False, upvotes)

            if (image.save()):
                print("Image: " + file_name + " saved successfully");
            else:
                print("Could not save image: " + file_name);

    return True;

def download_photo(image):
    try:
        with open("package/storage/images/" + image.file_name, "wb") as f:
            f.write(requests.get(image.url).content);
        image.downloaded = True;
        return True;
    except:
        return False;

if __name__ == "__main__":
    main()