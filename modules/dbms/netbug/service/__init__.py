# serivce层 实际处理接口
from typing import Union

from sqlalchemy import BinaryExpression

from modules.dbms.netbug.dao import session, NetBug
from modules.dbms.netbug.model.NetBugNode import NetBugNode
from modules.dbms.netbug.model.NetBugRootNode import NetBugRootNode
from modules.dbms.netbug.dao.NetBugRowData import NetBugRowData


class NetBugService():

    @classmethod
    def storageRootNodes(cls, rootNodes: list[NetBugRootNode]):
        if isinstance(rootNodes[0], list):
            for rootNode in rootNodes[0]:
                NetBugRowData.createOfNetBugRootNode(rootNode, False)
        else:
            NetBugRowData.createOfNetBugRootNode(rootNodes[0], False)
        NetBugRowData.resolveWaitInsertQueue()

    @classmethod
    def transformToTree(cls, rows: [NetBugRowData] = None):
        # 传入None默认全量转换
        if rows is None or len(rows) == 0:
            rows = NetBugRowData.listQuery()
        # 先获取所有的根节点
        rootNodeRows = list(filter(lambda row: row.fid == -1, rows))
        # 　从根节点找到所有子节点装入即可
        netBugNodes = []
        roots = []
        for rootNode in rootNodeRows:
            netBugRoot = NetBugRootNode.generousWithNetBug(rootNode)
            netBugNodes.append(netBugRoot)  # 这里存储一份，方便记录，思考完了就会发现这算法和bfs一模一样
            roots.append(netBugRoot)  # 这里返回结果
        for item in netBugNodes:
            child = list(filter(lambda node: node.fid == item.id, rows))
            childNode = list(map(lambda node: NetBugNode.generousWithNetBug(node), child))
            item.children = childNode
            if childNode is not None:
                if isinstance(childNode, list):
                    netBugNodes += childNode
                else:
                    netBugNodes.append(childNode)
        return roots
