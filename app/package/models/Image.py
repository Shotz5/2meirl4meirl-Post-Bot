from sqlite3 import IntegrityError
from ..includes.Database import *

class Image:
    def __init__(self, file_name, post_title, url, id, posted, downloaded, twitter_media_id, deleted, upvotes): 
        self.file_name = file_name;
        self.post_title = post_title;
        self.url = url;
        self.id = id;
        self.posted = posted;
        self.downloaded = downloaded;
        self.twitter_media_id = twitter_media_id;
        self.deleted = deleted;
        self.upvotes = upvotes;
        
    def __str__(self):
        return str(self.toArray());

    def toArray(self):
        return [self.file_name, self.post_title, self.url, self.id, self.posted, self.downloaded, self.twitter_media_id, self.deleted, self.upvotes];

    def save(self):
        with Database("package/storage/image_data.db") as db:
            arr = self.toArray();
            res = None;

            try:
                res = db.execute("""
                    INSERT INTO images (
                        file_name,
                        post_title,
                        url,
                        id,
                        posted,
                        downloaded,
                        twitter_media_id,
                        deleted,
                        upvotes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, arr);
            except IntegrityError:
                # Shift file_name to end of array
                arr.insert(len(arr), arr.pop(0));
                res = db.execute("""
                    UPDATE images
                    SET
                        post_title = ?,
                        url = ?,
                        id = ?,
                        posted = ?,
                        downloaded = ?,
                        twitter_media_id = ?,
                        deleted = ?,
                        upvotes = ?
                    WHERE file_name = ?
                """, arr);

            if (res.rowcount == 1):
                return True;
            else:
                return False;

    @staticmethod
    def fetchImageByFileName(file_name):
        with Database("package/storage/image_data.db") as db:
            res = db.query("""
                SELECT *
                FROM images
                WHERE file_name = ?
            """, (file_name,), False);

            if (res):
                obj = Image(*res);
                return obj
            else:
                return None;

    @staticmethod
    def fetchRandomImage():
        with Database("package/storage/image_data.db") as db:
            res = db.query("""
                SELECT * 
                FROM images 
                WHERE posted = 0 AND downloaded = 0 
                ORDER BY upvotes 
                DESC
            """, (), True);

            if (res):
                obj = Image(*res);
                return obj
            else:
                return None;

    @staticmethod
    def fetchAllRecords():
        with Database("package/storage/image_data.db") as db:
            res = db.query("""
                SELECT * 
                FROM images 
                ORDER BY upvotes 
                DESC
            """, (), False);

            return res;

    @staticmethod
    def deleteAllRecords():
        with Database("package/storage/image_data.db") as db:
            res = db.execute("""
                DELETE
                FROM images 
            """);

            return True;