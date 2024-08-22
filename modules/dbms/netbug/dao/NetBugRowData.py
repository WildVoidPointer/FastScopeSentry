import json
from typing import Union

from sqlalchemy import BinaryExpression

from . import NetBug, session
from ..model import NetBugRootNode
from ..model.NetBugNode import NetBugNode


#                            _ooOoo_
#                           o8888888o
#                           88" . "88
#                           (| -_- |)
#                            O\ = /O
#                        ____/`---'\____
#                      .   ' \\| |// `.
#                       / \\||| : |||// \
#                     / _||||| -:- |||||- \
#                       | | \\\ - /// | |
#                     | \_| ''\---/'' | |
#                      \ .-\__ `-` ___/-. /
#                   ___`. .' /--.--\ `. . __
#                ."" '< `.___\_<|>_/___.' >'"".
#               | | : `- \`.;`\ _ /`;.`/ - ` : | |
#                 \ \ `-. \_ __\ /__ _/ .-` / /
#         ======`-.____`-.___\_____/___.-`____.-'======
#                            `=---='
#
#         .............................................
#                  佛祖保佑             永无BUG
#          佛曰:
#                  写字楼里写字间，写字间里程序员；
#                  程序人员写程序，又拿程序换酒钱。
#                  酒醒只在网上坐，酒醉还来网下眠；
#                  酒醉酒醒日复日，网上网下年复年。
#                  但愿老死电脑间，不愿鞠躬老板前；
#                  奔驰宝马贵者趣，公交自行程序员。
#                  别人笑我忒疯癫，我笑自己命太贱；
#                  不见满街漂亮妹，哪个归得程序员？

class NetBugRowData:
    WaitInsertQueue = []

    def __init__(self, id, fid=-1, path="", url="", phoneNumbers=None, emailAddresses=None,
                 code=0, title="", outDomain=None, fingerPrint="", toDB=False):
        self.id = id
        self.fid = fid
        self.url = url
        self.outDomain = outDomain if outDomain is not None else []
        self.fingerPrint = fingerPrint
        self.path = path
        self.title = title
        self.phoneNumbers = phoneNumbers
        self.emailAddresses = emailAddresses
        self.code = code
        if toDB == True:
            self.toDB()

    def getRow(self):
        return NetBug(self.id, self.fid, self.url, self.outDomain, self.fingerPrint, self.path, self.title,
                      self.phoneNumbers, self.emailAddresses, self.code)

    def toDB(self):
        operat = self.getRow()
        if self.id is None:
            session.add(operat)
        else:
            session.query(NetBug).filter(NetBug.id == id).update(operat.__dict__)
        session.flush()

        self.id = operat.id
        session.commit()

    @classmethod
    def createOfNetBugNode(cls, netBugRootNode: dict, netBugNode: NetBugNode, clearTempEgion: bool = True):
        path = netBugNode['path']
        title = netBugNode['title']
        phoneNumbers = netBugNode['phoneNumbers']
        emailAddresses = netBugNode['emailAddresses']
        code = netBugNode['code']
        url = netBugRootNode.setdefault('url', None)
        outDomain = netBugRootNode.setdefault('outDomain', None)
        fingerPrint = netBugRootNode.setdefault('fingerprint', None)
        fid = netBugRootNode.setdefault('id', -1)
        currentNode = NetBugRowData(None, fid, path, url, phoneNumbers, emailAddresses, code, title, outDomain,
                                    fingerPrint)
        if netBugNode['children'] is None or len(netBugNode['children']) == 0:
            cls.WaitInsertQueue.append(currentNode)
        else:
            currentNode.toDB()
            netBugNode['id'] = currentNode.id
            netBugNodes = netBugNode['children']
            for item in netBugNodes:
                cls.createOfNetBugNode(netBugNode, item)
        if clearTempEgion == True:
            cls.resolveWaitInsertQueue()

    @classmethod
    def createOfNetBugRootNode(cls, netBugRootNode: NetBugRootNode, clearTempEgion: bool = True):
        url = netBugRootNode['url']
        outDomain = netBugRootNode['outDomain']
        fingerPrint = netBugRootNode['fingerprint']
        fid = -1
        # 如果是叶子节点，那么加入等待队列，最后统一添加
        # self, id, fid=-1, path="", url="", phoneNumbers=None, emailAddress=None,
        # code=0, title="", outDomain=None, fingerPrint="", toDB=False
        currentNode = NetBugRowData(id=None,
                                    fid=fid,
                                    url=url,
                                    phoneNumbers="",
                                    emailAddresses=None,
                                    code=0, title="", outDomain=outDomain, fingerPrint=fingerPrint)
        if netBugRootNode['children'] is None or len(netBugRootNode['children']) == 0:
            cls.WaitInsertQueue.append(currentNode)
        else:
            currentNode.toDB()  # 因为要获取编号，那么现在插入
            netBugRootNode['id'] = currentNode.id
            netBugNodes = netBugRootNode['children']
            for item in netBugNodes:
                cls.createOfNetBugNode(netBugRootNode, item, False)
        if clearTempEgion == True:
            cls.resolveWaitInsertQueue()

    @classmethod
    def resolveWaitInsertQueue(cls):
        if len(cls.WaitInsertQueue) == 0:
            return
        rowList = []
        for e in cls.WaitInsertQueue:
            rowList.append(e.getRow())
        session.add_all(rowList)
        session.commit()
        cls.WaitInsertQueue.clear()

    @classmethod
    def listQuery(cls, queryMapper: Union[NetBug, BinaryExpression[bool]] = None):
        if queryMapper is None:
            return session.query(NetBug).all()
        return session.query(NetBug).where(queryMapper).all()
