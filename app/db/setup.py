"""
Setting up the db and tables
"""
import os
from sqlalchemy import (
    create_engine,
    Column,
    # Integer,
    String,
    DateTime, LargeBinary, Text, UUID
)
from sqlalchemy.ext.declarative import declarative_base
import pika


Base = declarative_base()


class MemeData(Base):
    """Create db, tables and permissions if necessary"""
    __tablename__ = "meme_table"
    id = Column(UUID(), primary_key=True)
    date_created = Column(DateTime(timezone=True))
    name = Column(String(300))
    image_blob = Column(LargeBinary())
    video_filename = Column(String(300))
    # video_blob = Column(LargeBinary())
    keywords = Column(Text())
    image_url = Column(String(300))
    video_url = Column(String(300))
    tweet_id = Column(String())


def create_queue():
    """Establish RabbitMQ connection"""
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(
            "rabbitmq"
        )
    )
    channel = conn.channel()
    channel.queue_declare("produce_meme")


if __name__ == "__main__":
    db_name = os.environ.get("DB_NAME", "devdb")
    db_user = os.environ.get("DB_USER")
    db_user_pass = os.environ.get("DB_PASS")
    db_host = os.environ.get("DB_HOST", "db")
    path = "postgresql://{}:{}@{}/{}".format(
        db_user, db_user_pass, db_host, db_name
    )
    engine = create_engine(path, echo=True)
    Base.metadata.create_all(engine)
    create_queue()
