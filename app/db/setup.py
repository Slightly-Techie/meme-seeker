"""
Setting up the db and tables
"""
import os
from uuid import uuid4
# from typing import List
from sqlalchemy import (
    create_engine,
    Column,
    # Table,
    String,
    DateTime, LargeBinary,
    UUID,
    ForeignKey,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    relationship,
    Mapped,
    mapped_column
)


db_name = os.environ.get("DB_NAME", "devdb")
db_user = os.environ.get("DB_USER", "devuser")
db_user_pass = os.environ.get("DB_PASS", "changeme")
db_host = os.environ.get("DB_HOST", "localhost:5436")
path = "postgresql://{}:{}@{}/{}".format(
    db_user, db_user_pass, db_host, db_name
)
engine = create_engine(path, echo=True)


class Base(DeclarativeBase):
    pass


# association_table = Table(
#     "association_table",
#     Base.metadata,
#     Column("meme_id", ForeignKey("meme_table.id")),
#     Column("keyword_id", ForeignKey("keyword.id"))
# )


class MemeData(Base):
    """Create db, tables and permissions if necessary"""
    __tablename__ = "meme_table"
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    date_created = Column(DateTime(timezone=True))
    name = Column(String(300))
    image_blob = Column(LargeBinary())
    image_hash_digest = Column(String(99999))
    video_filename = Column(String(300))
    image_filename = Column(String(300))
    keywords: Mapped["Keyword"] = relationship()
    image_url = Column(String(300))
    video_url = Column(String(300))
    tweet_id = Column(String())


class Keyword(Base):
    """Create aa manytomany relation to MemeData table"""
    __tablename__ = "keyword"
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)
    date_created = Column(DateTime(timezone=True))
    name = Column(String(300))
    meme_id: Mapped[UUID] = mapped_column(ForeignKey("meme_table.id"))


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    # create_queue()
