from ..dao.NetBugTaskRowData import NetBugTaskRowData


class NetBugTaskApplication:
    def list(self):
        return NetBugTaskRowData.listQuery()
