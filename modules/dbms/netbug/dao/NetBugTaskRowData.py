from typing import Union

from sqlalchemy import BinaryExpression

from . import session, NetBugTask


class NetBugTaskRowData:
    @classmethod
    def insert(cls, ids):
        res = NetBugTask(None, ids)
        session.add(res)
        session.flush()
        session.commit()
        return res.id

    @classmethod
    def update(cls, id, ids):
        session.add(NetBugTask(id, ids))
        session.flush()
        session.commit()

    @classmethod
    def getOne(cls, id):
        return session.query(NetBugTask).where(NetBugTask.id == id).one()

    @classmethod
    def listQuery(cls, queryMapper: Union[NetBugTask, BinaryExpression[bool]] = None):
        return session.query(NetBugTask).filter(queryMapper).all()
