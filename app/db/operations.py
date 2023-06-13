"""
Managing all db operations - postgres
"""
# import os
import io
from uuid import uuid4
from datetime import datetime
from PIL import Image
import sqlalchemy as db
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.setup import MemeData, Keyword, engine
# from util.utils import load_config
from util.logger_tool import Logger


class DbOperations:
    def __init__(self):
        self.session = Session(engine)
        self.metadata = db.MetaData()

    def save_image(self, full_data, image_format, keyword_tag="Test"):
        """Saving media in DB"""
        # local_db = self.session
        Logger.info("Save data in database initiated")
        # Logger.info(full_data)
        duplicate_id = self.duplicate_validation(
            full_data["image_hash_digest"]
            )
        if duplicate_id:
            Logger.info("Media already exists in the Database")
            keywords_record = Keyword(
                id=uuid4(),
                date_created=datetime.now(),
                name=keyword_tag,
                meme_id=duplicate_id
                )
            self.session.add(keywords_record)
            self.session.commit()
            Logger.info("Data Commited succesfully")

            return True
        else:
            keywords_record = Keyword(
                id=uuid4(),
                date_created=datetime.now(),
                name=keyword_tag
                )
            meme_record = MemeData(
                id=uuid4(),
                date_created=datetime.now(),
                name=keyword_tag,
                keywords=keywords_record,
                image_filename=uuid4().hex + image_format,
                **full_data,
                )
            self.session.add(keywords_record)
            self.session.add(meme_record)
            self.session.commit()
            Logger.info("Data Commited succesfully")

            return True

    def duplicate_validation(self, image_hash_digest):
        """Takes image hash and compares with db records for a match"""
        stmt = select(MemeData.image_hash_digest, MemeData.id)
        # result = False
        for row in self.session.execute(stmt).all():
            print(row.image_hash_digest, image_hash_digest)
            if row.image_hash_digest == image_hash_digest:
                return row.id

        return None
        # hash_list.append(row.image_hash_digest)

    def get_image(self, tweet_tag):
        """Get image from database"""
        Logger.info("Getting the image from DB")
        Logger.info(tweet_tag)
        stmt = select(Keyword.name, Keyword.meme_id)
        for row in self.session.execute(stmt).all():
            Logger.info(row.name, tweet_tag)
            if row.name == tweet_tag:
                Logger.info("Found a match")
                img_data = self.session.execute(
                    select(MemeData.image_blob,
                           MemeData.id, MemeData.image_filename
                           )).first()
                Logger.info(img_data)
                if img_data:
                    Logger.info("Got some image data")
                    return img_data.image_blob, img_data.image_filename
                else:
                    Logger.debug("Nothing")
                    return None, None
        else:
            Logger.debug("Found no match")
            return None, None

    def get_video_filename(self, tweet_tag):
        """Get video filename from database"""
        Logger.info("Getting the video filename from DB")
        Logger.info(tweet_tag)
        stmt = select(Keyword.name, Keyword.meme_id)
        for row in self.session.execute(stmt).all():
            Logger.info(row.name, tweet_tag)
            if row.name == tweet_tag:
                Logger.info("Found a match")
                img_data = self.session.execute(
                    select(MemeData.video_filename,
                           MemeData.id, MemeData.image_filename,
                           MemeData.image_blob
                           )).first()
                Logger.info(img_data)
                if img_data:
                    Logger.info("Got some data")
                    if img_data.video_filename:
                        Logger.info("It's a video")
                        return img_data.video_filename
                    else:
                        Logger.info("No video found. Image found.")
                        Logger.info("Creating image from blob")
                        image = Image.open(io.BytesIO(img_data.image_blob))
                        image.save(img_data.image_filename)
                        return img_data.image_filename
                else:
                    Logger.debug("Nothing")
                    return None
        else:
            Logger.debug("Found no match")
            return None

    def show_image(self, image_id, image_format):
        """Read data from db and show image"""
        (row_id, ) = image_id
        query = db.select(self.meme_table).where(
            self.meme_table.c.id == row_id
        )
        with self.engine.connect() as conn:
            row = conn.execute(query).first()
            Logger.info(row)

            # image_data = row[3]
            # filename = uuid4().hex
            # image = Image.open(io.BytesIO(image_data))
            # image.save(filename+image_format)
        return True
