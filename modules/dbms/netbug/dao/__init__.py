from datetime import datetime

from sentry.settings import DEFAULT_DB_CONF
from sqlalchemy import create_engine, Text
from sqlalchemy import Column, DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.mysql import MEDIUMTEXT
import json


metadata = MetaData()
# 定义ORM模型
Base = declarative_base()


class NetBug(Base):
    __tablename__ = 'net_bug'
    id = Column(Integer, primary_key=True)
    fid = Column(Integer)
    url = Column(String(512))
    outDomain = Column(String(512))
    fingerPrint = Column(String(512))
    path = Column(String(512))
    title = Column(String(512))
    phoneNumbers = Column(String(512))
    emailAddresses = Column(Text)
    code = Column(Integer)

    def __init__(self, id, fid, url, outDomain, fingerPrint, path, title, phoneNumbers, emailAddresses, code):
        self.id = id
        self.fid = fid
        self.url = url
        self.outDomain = json.dumps(outDomain)
        self.fingerPrint = json.dumps(fingerPrint)
        self.path = path
        self.title = title
        self.phoneNumbers = json.dumps(phoneNumbers)
        self.emailAddresses = json.dumps(emailAddresses)
        self.code = code


class NetBugTask(Base):
    __tablename__ = 'net_bug_task'
    id = Column(Integer, primary_key=True)
    ids = Column(String(10240))

    def __init__(self, id, ids):
        self.id = id
        self.ids = ids


class Crawler(Base):
    __tablename__ = 'crawler'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(256))
    target = Column(String(1024))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String(52), default='scanning')
    crawler_res = Column(MEDIUMTEXT)
    img_analyzer = Column(Text)

    def __init__(self, task_name=None, target=None, status='scanning', crawler_res=None, img_analyzer=None):
        self.task_name = task_name
        self.target = target
        self.status = status
        self.crawler_res = crawler_res
        self.img_analyzer = img_analyzer


class TmplScan(Base):
    __tablename__ = 'tmpl_scan'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(256))
    target = Column(String(1024))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String(52), default='scanning')
    tmpl = Column(String(1024))
    tmpls_res = Column(Text)

    def __init__(self, task_name=None, target=None, tmpl=None, status='scanning', tmpls_res=None):
        self.task_name = task_name
        self.target = target
        self.status = status
        self.tmpl = tmpl
        self.tmpls_res = tmpls_res


class PortScan(Base):
    __tablename__ = 'port_scan'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(256))
    target = Column(String(1024))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String(52), default='scanning')
    port_scan = Column(Text)

    def __init__(self, task_name=None, target=None, status='scanning', port_scan=None):
        self.task_name = task_name
        self.target = target
        self.status = status
        self.port_scan = port_scan


engine = create_engine(
    f"{DEFAULT_DB_CONF['DB_ENGINE']}://"
    f"{DEFAULT_DB_CONF['USERNAME']}:"
    f"{DEFAULT_DB_CONF['PASSWORD']}@"
    f"{DEFAULT_DB_CONF['HOST']}:"
    f"{DEFAULT_DB_CONF['PORT']}/"
    f"{DEFAULT_DB_CONF['DBNAME']}",
    echo=True
)
# engine = create_engine("mysql+pymysql://root:123456@localhost:3308/sentryapp",echo=True)
metadata.create_all(engine)  # 表的持久化 todo:建库打开运行即可
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine, checkfirst=True)
session = Session()
