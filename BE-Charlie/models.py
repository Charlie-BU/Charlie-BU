import re
from datetime import datetime
from sqlalchemy import create_engine, ForeignKey, Boolean, Column, Integer, Text, DateTime, Date, Float, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.ext.mutable import MutableList
from bcrypt import hashpw, gensalt, checkpw
import random

from config import DATABASE_URI

engine = create_engine(
    DATABASE_URI,
    echo=True,
    pool_size=20,  # 默认连接池大小
    max_overflow=30,  # 最大溢出连接数
    pool_timeout=60,  # 连接超时时间
    pool_recycle=3600  # 连接回收时间，防止连接被数据库关闭
)
# 数据库表基类
Base = declarative_base()
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
Base.metadata.naming_convention = naming_convention
# 会话，用于通过ORM操作数据库
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 全局session会造成严重后果
# session = Session()


# 浏览器指纹
class Fingerprint(Base):
    __tablename__ = "fingerprint"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fingerprint = Column(Text, nullable=False)
    create_time = Column(DateTime, default=datetime.now)

    def to_json(self):
        data = {
            "id": self.id,
            "fingerprint": self.fingerprint,
            "create_time": self.create_time,
        }
        return data


class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    password = Column(Text, nullable=False)

    @staticmethod
    def hash_password(password):
        hashed = hashpw(password.encode("utf-8"), gensalt())
        return hashed.decode("utf-8")

    def check_password(self, password):
        return checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    def to_json(self):
        data = {
            "id": self.id,
            "name": self.name,
            "password": self.password,
        }
        return data


class Charlie(Base):
    __tablename__ = "charlie"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    name_ENG = Column(Text)
    description = Column(Text)
    description_ENG = Column(Text)
    height = Column(Float)
    weight = Column(Float)
    birthday = Column(Date)
    github = Column(Text)
    email = Column(Text)
    motto = Column(MutableList.as_mutable(JSON()), default=[])
    motto_ENG = Column(MutableList.as_mutable(JSON()), default=[])
    photos = Column(MutableList.as_mutable(JSON()), default=[])
    resume = Column(Text)

    visitorNumber = Column(Integer)

    @property
    def age(self):
        return (datetime.now().date() - self.birthday).days // 365

    def to_json(self):
        selected_motto = random.choice(self.motto) if self.motto else None
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "birthday": self.birthday,
            "github": self.github,
            "email": self.email,
            "motto": selected_motto,
            "photos": self.photos,
            "resume": self.resume,
            "visitorNumber": self.visitorNumber,
        }
        return data

    def to_json_ENG(self):
        selected_motto = random.choice(self.motto_ENG) if self.motto_ENG else None
        data = {
            "id": self.id,
            "name": self.name_ENG,
            "description": self.description_ENG,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "birthday": self.birthday,
            "github": self.github,
            "email": self.email,
            "motto": selected_motto,
            "photos": self.photos,
            "resume": self.resume,
            "visitorNumber": self.visitorNumber,
        }
        return data


class Talent(Base):
    __tablename__ = "talent"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text)
    title_ENG = Column(Text)
    description = Column(Text)
    description_ENG = Column(Text)
    icon = Column(Text)
    gotoUrl = Column(Text)

    def to_json(self):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "icon": self.icon,
            "gotoUrl": self.gotoUrl,
        }
        return data

    def to_json_ENG(self):
        data = {
            "id": self.id,
            "title": self.title_ENG,
            "description": self.description_ENG,
            "icon": self.icon,
            "gotoUrl": self.gotoUrl,
        }
        return data


class Achievement(Base):
    __tablename__ = "achievement"
    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(Text)
    label_ENG = Column(Text)
    number = Column(Text)

    def to_json(self):
        data = {
            "id": self.id,
            "label": self.label,
            "number": self.number,
        }
        return data

    def to_json_ENG(self):
        data = {
            "id": self.id,
            "label": self.label_ENG,
            "number": self.number,
        }
        return data


class GrowthTimeline(Base):
    __tablename__ = "growth_timeline"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text)
    content_ENG = Column(Text)
    timestamp = Column(Text)

    def to_json(self):
        data = {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp,
        }
        return data

    def to_json_ENG(self):
        data = {
            "id": self.id,
            "content": self.content_ENG,
            "timestamp": self.timestamp,
        }
        return data


class Bubble(Base):
    __tablename__ = "bubble"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text)
    content_ENG = Column(Text)
    date = Column(Date)
    tags = Column(MutableList.as_mutable(JSON()), default=[])
    tag_ENG = Column(MutableList.as_mutable(JSON()), default=[])

    def to_json(self):
        data = {
            "id": self.id,
            "content": self.content,
            "date": self.date,
            "tags": self.tags,
        }
        return data

    def to_json_ENG(self):
        data = {
            "id": self.id,
            "content": self.content_ENG,
            "date": self.date,
            "tags": self.tag_ENG,
        }
        return data


class Article(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text)
    content_ENG = Column(Text)
    timeCreated = Column(DateTime, default=datetime.now)
    timeLastUpdated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    tags = Column(MutableList.as_mutable(JSON()), default=[])
    tag_ENG = Column(MutableList.as_mutable(JSON()), default=[])
    # 文本：1；markdown：2
    type = Column(Integer, default=1)
    isReleased = Column(Boolean, default=False)
    aiSummary = Column(Text)

    @property
    def title(self):
        if not self.content:
            return ""
        if self.type == 1:
            return self.content.split("\n")[0]
        elif self.type == 2:
            title = self.content.split("\n")[0]
            title = re.sub(r"^#+\s*", "", title)
            return title
        return ""

    @property
    def title_ENG(self):
        if not self.content_ENG:
            return ""
        if self.type == 1:
            return self.content_ENG.split("\n")[0]
        elif self.type == 2:
            title = self.content_ENG.split("\n")[0]
            title = re.sub(r"^#+\s*", "", title)
            return title
        return ""

    def to_json(self):
        data = {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "timeCreated": self.timeCreated,
            "timeLastUpdated": self.timeLastUpdated,
            "tags": self.tags,
            "type": self.type,
            "isReleased": self.isReleased,
            "aiSummary": self.aiSummary,
        }
        return data

    def to_json_ENG(self):
        data = {
            "id": self.id,
            "title": self.title_ENG,
            "content": self.content_ENG,
            "timeCreated": self.timeCreated,
            "timeLastUpdated": self.timeLastUpdated,
            "tags": self.tag_ENG,
            "type": self.type,
            "isReleased": self.isReleased,
            "aiSummary": self.aiSummary,
        }
        return data



class PlaceBeenTo(Base):
    __tablename__ = "place_been_to"
    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(Text)
    country_ENG = Column(Text)
    city = Column(Text)
    city_ENG = Column(Text)
    description = Column(Text)
    description_ENG = Column(Text)
    dateStart = Column(Date)
    dateEnd = Column(Date)

    def to_json(self):
        data = {
            "id": self.id,
            "country": self.country,
            "country_ENG": self.country_ENG,
            "city": self.city,
            "city_CH": self.city,
            "description": self.description,
            "dateStart": self.dateStart,
            "dateEnd": self.dateEnd,
        }
        return data

    def to_json_ENG(self):
        data = {
            "id": self.id,
            "country": self.country_ENG,
            "country_ENG": self.country_ENG,
            "city": self.city_ENG,
            "city_CH": self.city,
            "description": self.description_ENG,
            "dateStart": self.dateStart,
            "dateEnd": self.dateEnd,
        }
        return data
        

class TravelPhoto(Base):
    __tablename__ = "travel_photo"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text)
    travelId = Column(Integer, ForeignKey("place_been_to.id"))
    travel = relationship("PlaceBeenTo", backref="photos")
    isShown = Column(Boolean, default=True)

    def to_json(self):
        data = {
            "id": self.id,
            "url": self.url,
            "travelId": self.travelId,
            "isShown": self.isShown,
        }
        return data


# 创建所有表（被alembic替代）
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
