from modules.dbms.netbug.dao import Crawler, TmplScan, PortScan, session
from modules.imganlz.analyzer import web_images_analyzer_action
from modules.tmplscan.tmplscanner import activate_scanning_main
from modules.webcrawl.crawler import web_crawler_action
from modules.portscan.scanner import port_scan_action

from sqlalchemy.exc import SQLAlchemyError
from threading import Thread
from datetime import datetime


class MultiTaskModelInterFace(Thread):
    def create_task_record(self) -> tuple[bool, int | None, str | None]:
        pass

    def __save_task_results(self) -> bool:
        pass


class MultiCrawlerTaskModel(MultiTaskModelInterFace):
    def __init__(self, task_name: str, target: str) -> None:
        super().__init__()
        if isinstance(target, str) and target != "":
            self.__task_name: str = task_name
            self.__target: str = target
            self.__task_id: int | None = None
            self.__crawler_res: str | None = None
            self.__img_analyzer: str | None = None

    def create_task_record(self) -> tuple[bool, int | None, str | None]:
        try:
            current_task_data = Crawler(task_name=self.__task_name, target=self.__target)
            session.add(current_task_data)
            session.commit()
            session.flush()
            self.__task_id = current_task_data.id
            return True, self.__task_id, self.__task_name
        except SQLAlchemyError:
            session.rollback()
            session.expire_all()
            return False, None, None

    def __save_task_results(self) -> bool:

        try:
            task: Crawler = session.query(Crawler).filter(Crawler.id == self.__task_id).first()
            if task:
                task.status = 'finnish'
                task.crawler_res = self.__crawler_res
                task.img_analyzer = self.__img_analyzer
                task.end_time = datetime.utcnow()
                session.commit()
            return True
        except SQLAlchemyError:
            session.rollback()
            session.expire_all()
            return False

    def run(self) -> None:
        self.__crawler_res = web_crawler_action(self.__target)
        self.__img_analyzer = web_images_analyzer_action(self.__target)
        self.__save_task_results()


class MultiTemplateScanModel(MultiTaskModelInterFace):
    def __init__(self, task_name: str, target: str, tmpl: str | None = None) -> None:
        super().__init__()
        self.__task_id = None
        self.__task_name = task_name
        self.__target = target
        self.__tmpl = tmpl
        self.__scan_res: str | None = None

    def create_task_record(self) -> tuple[bool, int | None, str | None]:
        try:
            current_task_data = TmplScan(task_name=self.__task_name, target=self.__target, tmpl=self.__tmpl)
            session.add(current_task_data)
            session.commit()
            session.flush()
            self.__task_id = current_task_data.id
            return True, self.__task_id, self.__task_name
        except SQLAlchemyError:
            session.rollback()
            session.expire_all()
            return False, None, None

    def __save_task_results(self) -> bool:
        try:
            task: TmplScan = session.query(TmplScan).filter(TmplScan.id == self.__task_id).first()
            if task:
                task.status = 'finnish'
                task.tmpls_res = self.__scan_res
                task.end_time = datetime.utcnow()
                session.commit()
            return True
        except SQLAlchemyError:
            session.rollback()
            session.expire_all()
            return False

    def run(self) -> None:
        self.__scan_res = activate_scanning_main({'url': self.__target, 'template': self.__tmpl})
        self.__save_task_results()


class MultiPortScanTaskModel(MultiTaskModelInterFace):
    def __init__(self, task_name: str, target: str) -> None:
        super().__init__()
        self.__task_id = None
        self.__task_name = task_name
        self.__target = target
        self.__port_scan_res = None

    def create_task_record(self) -> tuple[bool, int | None, str | None]:
        try:
            current_task_data = PortScan(task_name=self.__task_name, target=self.__target)
            session.add(current_task_data)
            session.commit()
            session.flush()
            self.__task_id = current_task_data.id
            return True, self.__task_id, self.__task_name
        except SQLAlchemyError:
            session.rollback()
            session.expire_all()
            return False, None, None

    def __save_task_results(self) -> bool:
        try:
            task: PortScan = session.query(PortScan).filter(PortScan.id == self.__task_id).first()
            if task:
                task.status = 'finnish'
                task.port_scan = self.__port_scan_res
                task.end_time = datetime.utcnow()
                session.commit()
            return True
        except SQLAlchemyError:
            session.rollback()
            session.expire_all()
            return False

    def run(self) -> None:
        self.__port_scan_res = port_scan_action(target=self.__target)
        self.__save_task_results()
