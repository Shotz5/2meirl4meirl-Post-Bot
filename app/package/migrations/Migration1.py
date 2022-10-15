from ..includes.Database import *

class Migration1:

    def __init__(self, nice):
        self._nice = nice;
    
    @staticmethod
    def migrate():
        with Database("package/storage/image_data.db") as db:
            query = """
                CREATE TABLE IF NOT EXISTS images (
                                    file_name text PRIMARY KEY,
                                    post_title text NOT NULL,
                                    url text NOT NULL,
                                    id text NOT NULL,
                                    posted boolean NOT NULL,
                                    downloaded boolean NOT NULL,
                                    twitter_media_id text,
                                    deleted boolean NOT NULL,
                                    upvotes integer NOT NULL DEFAULT 0
                                );
            """;

            try:
                db.execute(query);
                return True;
            except:
                print("Migration failed to run: 2022_10_15");
                return False;