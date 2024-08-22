from ..dao import NetBug


class NetBugNode:
    def __init__(self, path="", phoneNumbers=None, emailAddresses=None, code=0, title="", children=None,id=None,fid=None):
        self.path = path
        self.phoneNumbers = phoneNumbers if phoneNumbers is not None else []
        self.emailAddresses = emailAddresses if emailAddresses is not None else []
        self.code = code
        self.title = title
        self.children = children if children is not None else []
        self.id = id
        self.fid = fid

    @classmethod
    def generousWithNetBug(cls, netBug:NetBug):
        return NetBugNode(netBug.path,netBug.phoneNumbers,netBug.emailAddresses,netBug.code,netBug.title,None,netBug.id,netBug.fid)