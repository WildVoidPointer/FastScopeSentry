import json
import re
import string

from ..dao.NetBugTaskRowData import NetBugTaskRowData
from ..model.NetBugRootNode import NetBugRootNode
from ..service import NetBugService


class NetBugApplication:

    @classmethod
    def to_camelcase(self, name: str) -> str:
        """下划线转驼峰(小驼峰)"""
        return re.sub(r'(_[a-z])', lambda x: x.group(1)[1].upper(), name)

    # json转换
    @classmethod
    def transform(self, js: string):
        js = self.to_camelcase(js)
        res = json.loads(js)
        return res

    @classmethod
    def saveJson(self, js: string):
        return self.save([self.transform(js)])

    # 保存list
    @classmethod
    def save(self, netBugNodeList: [NetBugRootNode]):
        NetBugService.storageRootNodes(netBugNodeList)
        ids = json.dumps(list(map(lambda row: row['id'], netBugNodeList)))
        NetBugTaskRowData.insert(ids)

    # 不传入任务id，默认获取全部，传入任务id，获取和任务关联的即可
    @classmethod
    def getTree(self, id=None):
        if id is None:
            return NetBugService.transformToTree()
        ids = NetBugTaskRowData.getOne(id).ids
        res = ids.strip('[')
        res = res.strip(']')
        res = res.split(',')
        res = list(map(lambda item: int(item), res))
        allRes = NetBugService.transformToTree()
        return list(filter(lambda row: row.id in res, allRes))
