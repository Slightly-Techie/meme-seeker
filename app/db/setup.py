"""
Setting up the db and tables
"""
import os
from typing import List
from sqlalchemy import (
    create_engine,
    Column,
    Table,
    String,
    DateTime, LargeBinary,
    UUID,
    ForeignKey,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    relationship,
    Mapped
)


class Base(DeclarativeBase):
    pass


association_table = Table(
    "association_table",
    Base.metadata,
    Column("meme_id", ForeignKey("meme_table.id")),
    Column("keyword_id", ForeignKey("keyword.id"))
)


class MemeData(Base):
    """Create db, tables and permissions if necessary"""
    __tablename__ = "meme_table"
    id = Column(UUID(), primary_key=True)
    date_created = Column(DateTime(timezone=True))
    name = Column(String(300))
    image_blob = Column(LargeBinary())
    video_filename = Column(String(300))
    # video_blob = Column(LargeBinary())
    keywords: Mapped[List] = relationship(secondary=association_table)
    image_url = Column(String(300))
    video_url = Column(String(300))
    tweet_id = Column(String())


class Keyword(Base):
    """Create aa manytomany relation to MemeData table"""
    __tablename__ = "keyword"
    id = Column(UUID(), primary_key=True)
    date_created = Column(DateTime(timezone=True))
    name = Column(String(300))


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
    # create_queue()
