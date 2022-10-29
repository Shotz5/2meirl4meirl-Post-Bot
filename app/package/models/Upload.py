from tabnanny import check
from package.models.Image import *
import os
import time

CHUNK_SIZE = 4*1024*1024;
MEDIA_ENDPOINT_URL = "https://upload.twitter.com/1.1/media/upload.json";
TWEETS_ENDPOINT_URL = "https://api.twitter.com/2/tweets";

class Upload:
    def __init__(self, auth, image):
        self.auth = auth;
        self.image = image;
        self.image_size = os.path.getsize("package/storage/images/" + image.file_name);

    def upload_and_tweet_photo(self):
        if (self.upload_photo()):
            if (self.tweet_photo()):
                return True;
            else:
                return False;
        else:
            return False;

    def tweet_photo(self):
        tweet_object_image = {
            "text": self.image.post_title + " redd.it/" + self.image.id,
            "media": {
                "media_ids": [str(self.image.twitter_media_id)]
            }
        }
        tweet_headers = {"Content-Type": "application/json"}
        response = self.auth.post(
            TWEETS_ENDPOINT_URL,
            headers=tweet_headers,
            json=tweet_object_image
        )

        if (response.status_code == 201):
            self.image.posted = True;
            return True;
        else:
            print(response.text);
            return False;

    def upload_photo(self):
        if (".gif" not in self.image.file_name):
            media = self.auth.post(MEDIA_ENDPOINT_URL, files={"media": open("package/storage/images/" + self.image.file_name, "rb")})
            
            if (media.status_code == 200):
                self.image.twitter_media_id = media.json()["media_id"];
                return True;
            else:
                return False;

        elif (".gif" in self.image.file_name):
            if (self.__init()):
                if(self.__append()):
                    if(self.__finalize()):
                        return True;
                    else:
                        return False;
                else:
                    return False;
            else:
                return False;

    def __init(self):
        media_upload = {
            "command": "INIT",
            "total_bytes": self.image_size,
            "media_type": "image/gif",
            "media_category": "tweet_gif"
        };

        res = self.auth.post(url=MEDIA_ENDPOINT_URL, data=media_upload);

        if (res.status_code < 200 or res.status_code > 299):
            return False;
        else:
            self.image.twitter_media_id = res.json()['media_id'];
            return True;

    def __append(self):
        segment = 0;
        bytes_sent = 0;
        file = open("package/storage/images/" + self.image.file_name, "rb");

        while (bytes_sent < self.image_size):
            chunk = file.read(CHUNK_SIZE);

            upload_meta = {
                "command": "APPEND",
                "media_id": self.image.twitter_media_id,
                "segment_index": segment,
            };

            upload_chunk = {
                "media": chunk
            };

            res = self.auth.post(MEDIA_ENDPOINT_URL, data=upload_meta, files=upload_chunk);

            if (res.status_code < 200 or res.status_code > 299):
                return False;
            else:
                segment += 1;
                bytes_sent = file.tell();
        return True;

    def __finalize(self):
        request_data = {
            "command": "FINALIZE",
            "media_id": self.image.twitter_media_id
        };

        res = self.auth.post(MEDIA_ENDPOINT_URL, data=request_data);

        if (res.status_code < 200 or res.status_code > 299):
            return False;
        else:
            self.processing_info = res.json().get("processing_info", None);
            status = self.__check_status();
            while (status == "pending"):
                status = self.__check_status();

            if (status == "success"):
                return True;
            else:
                return False;

    def __check_status(self):
        if self.processing_info is None:
            return True;

        if (self.processing_info["state"] == "succeeded"):
            return "success";
        elif (self.processing_info["state"] == "failed"):
            return "failed";

        check_after_secs = self.processing_info["check_after_secs"];
        time.sleep(check_after_secs);

        request_data = {
            "command": "STATUS",
            "media_id": self.image.twitter_media_id
        };

        res = self.auth.get(url=MEDIA_ENDPOINT_URL, params=request_data);

        self.processing_info = res.json().get('processing_info', None)
        return "pending";
