"""
Managing all db operations - postgres
"""
import os
# import io
from uuid import uuid4
from datetime import datetime
# from PIL import Image
import sqlalchemy as db

# from util.utils import load_config
from util.logger_tool import Logger


class DbOperations:
    def __init__(self):
        self.db_name = os.environ.get("DB_NAME", "devdb")
        self.db_user = os.environ.get("DB_USER", "devuser")
        self.db_user_pass = os.environ.get("DB_PASS", "changeme")
        self.db_host = os.environ.get("DB_HOST", "localhost:5436")
        path = "postgresql://{}:{}@{}/{}".format(
            self.db_user, self.db_user_pass,
            self.db_host, self.db_name
        )
        self.engine = db.create_engine(path)
        # self.conn = self.engine.connect()
        self.metadata = db.MetaData()

    def save_image(self, full_data, image_format, username="Test"):
        """Saving media in DB"""
        self.meme_table = db.Table(
            'meme_table', self.metadata, autoload_with=self.engine
            )
        self.keywords_table = db.Table(
            'keyword', self.metadata, autoload_with=self.engine
            )
        query = db.insert(self.meme_table).values(
            id=uuid4(),
            date_created=datetime.now(),
            name=username,
            **full_data,
        )
        keyword_insert = db.insert(self.keywords_table).values(
            id=uuid4(),
            date_created=datetime.now(),
            name=username
        )
        with self.engine.connect() as conn:
            result = conn.execute(query)
            k_result = conn.execute(keyword_insert)
            # query.keywords.add(k_result)
            conn.commit()
            print("Successfully committed")
            Logger.info(result.inserted_primary_key)
            Logger.info(k_result.inserted_primary_key)
            self.show_image(
                result.inserted_primary_key, image_format
                )
        return True

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
