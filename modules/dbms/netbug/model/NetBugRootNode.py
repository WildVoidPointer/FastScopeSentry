from ..dao import NetBug
from . import NetBugNode


class NetBugRootNode:  # 假设 NetBugRootNode 是 NetBugNode 的子类
    def __init__(self, url="", outDomain=None, fingerPrint="", children: list[NetBugNode] = None, id=0):
        self.url = url
        self.outDomain = outDomain if outDomain is not None else []
        self.fingerPrint = fingerPrint
        self.children = children if children is not None else [NetBugNode]
        self.id = id

    @classmethod
    def generousWithNetBug(cls, netBug: NetBug):
        return NetBugRootNode(netBug.url, netBug.outDomain, netBug.fingerPrint, None, netBug.id)
