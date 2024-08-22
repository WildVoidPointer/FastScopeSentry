from modules.dbms.netbug.dao import Crawler, PortScan, TmplScan, session
from modules.intelliapi.sparktmpl import SparkAiModel
from sentry.settings import INTELLI_QA_TEMPLATE

import json


class QuestionTemplateController:

    __TEMPLATE_DATA: dict[str, str] | None = None

    @staticmethod
    def get_user_define_template(path: str = INTELLI_QA_TEMPLATE) -> dict[str, str]:
        with open(path, 'r', encoding='utf-8') as f:
            tmpl = f.read()
            return json.loads(tmpl)

    @staticmethod
    def get_crawler_analyse_res(task_id: int):
        if isinstance(QuestionTemplateController.__TEMPLATE_DATA, dict) and isinstance(task_id, int):
            crawl_res: str = session.query(Crawler.crawler_res).filter_by(id=task_id).first()
            try:
                _tmpl = QuestionTemplateController.__TEMPLATE_DATA.get('CRAWLER', '')
                content = (_tmpl + crawl_res) if _tmpl != '' else None
                res = SparkAiModel.get_ai_analyse_res(content)
                if res is not None:
                    return res
            except Exception:
                return None

    @staticmethod
    def get_images_analyse_res(task_id: int):
        if isinstance(QuestionTemplateController.__TEMPLATE_DATA, dict) and isinstance(task_id, int):
            images_res: str = session.query(Crawler.img_analyzer).filter_by(id=task_id).first()
            try:
                _tmpl = QuestionTemplateController.__TEMPLATE_DATA.get('IMAGE_ANALYSE', '')
                content = (_tmpl + images_res) if _tmpl != '' else None
                _res = SparkAiModel.get_ai_analyse_res(content)
                if _res is not None:
                    return _res
            except Exception:
                return None

    @staticmethod
    def get_port_scan_analyse_res(task_id: int):
        if isinstance(QuestionTemplateController.__TEMPLATE_DATA, dict) and isinstance(task_id, int):
            port_scan_res: str = session.query(PortScan.port_scan).filter_by(id=task_id).first()
            try:
                _tmpl = QuestionTemplateController.__TEMPLATE_DATA.get('PORT_SCAN', '')
                content = (_tmpl + port_scan_res) if _tmpl != '' else None
                res = SparkAiModel.get_ai_analyse_res(content)
                if res is not None:
                    return res
            except Exception:
                return None

    @staticmethod
    def get_tmpl_scan_analyse_res(task_id: int):
        if isinstance(QuestionTemplateController.__TEMPLATE_DATA, dict) and isinstance(task_id, int):
            tmpl_scan_res: str = session.query(TmplScan.tmpls_res).filter_by(id=task_id).first()
            try:
                _tmpl = QuestionTemplateController.__TEMPLATE_DATA.get('TMPL_SCAN', '')
                content = (_tmpl + tmpl_scan_res) if _tmpl != '' else None
                res = SparkAiModel.get_ai_analyse_res(content)
                if res is not None:
                    return res
            except Exception:
                return None

    @staticmethod
    def get_vul_news_analyse_res(content: str):
        if isinstance(QuestionTemplateController.__TEMPLATE_DATA, dict) and isinstance(content, str):
            try:
                _tmpl = QuestionTemplateController.__TEMPLATE_DATA.get('VUL_NEWS', '')
                content = (_tmpl + content) if _tmpl != '' else None
                res = SparkAiModel.get_ai_analyse_res(content)
                if res is not None:
                    return res
            except Exception:
                return None
