from lib.appresp.respstatus import TaskStatusRespController, TaskStatusResp
from lib.appresp.respstatus import BaseRespController, BaseResponse
from lib.intellicall.contorller import QuestionTemplateController
from modules.dbms.netbug.dao import Crawler, TmplScan, PortScan, session
from sentry.modles import CrawlerTaskCreateModel, TmplScanTaskCreateModel
from sentry.modles import PortScanTaskCreateModel, VulNewsAnalyseModel
from lib.taskqueue import TaskQueueController
from .urls import *

from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI

app = FastAPI()


@app.post(SentryRouters.CRAWLER)
async def create_crawler_task(crawler_task: CrawlerTaskCreateModel) -> TaskStatusResp:
    """
    This view receives POST requests to add web crawler tasks to the Task queue controller
    """
    status = TaskQueueController.add_new_crawler_task(target=crawler_task.target, task_name=crawler_task.task_name)
    if status[0]:
        return TaskStatusRespController.success(task_id=status[1], task_name=status[2])
    return TaskStatusRespController.failed()


@app.get(SentryRouters.CRAWLER_SPECIFIC)
async def get_specific_crawl_info(task_id: int):
    """
    This view function needs to pass in the task ID parameter as the view crawler target task index
    """
    try:
        task_info = session.query(Crawler.crawler_res).filter_by(id=task_id).first()
        return BaseRespController.success(str(task_info[0]))
    except SQLAlchemyError:
        return BaseRespController.failed()


@app.get(SentryRouters.CRAWLER)
async def get_crawler_history() -> BaseResponse:
    """
    This view function acts as a crawler history viewing interface
    """
    try:
        all_task_info = []
        for task in session.query(Crawler).all():
            task_dict = {key: value for key, value in task.__dict__.items() if key != '_sa_instance_state'}
            all_task_info.append(task_dict)
        return BaseRespController.success(data=all_task_info)
    except SQLAlchemyError:
        return BaseRespController.failed()


@app.post(SentryRouters.TMPL_SCAN)
async def create_tmpl_scan_task(tmpl_task: TmplScanTaskCreateModel) -> TaskStatusResp:
    """
    This view receives POST requests to add template scanning tasks to the Task queue controller
    """
    status = TaskQueueController.add_new_tmpl_scan_task(
        task_name=tmpl_task.task_name, target=tmpl_task.target #, tmpl=tmpl_task.template
    )
    if status[0]:
        return TaskStatusRespController.success(task_id=status[1], task_name=status[2])
    return TaskStatusRespController.failed()


@app.get(SentryRouters.TMPL_SCAN_SPECIFIC)
async def get_specific_tmpl_info(task_id: int) -> BaseResponse:
    """
    This view function needs to pass in the task ID parameter as the view template scanning target task index
    """
    try:
        task_info = session.query(TmplScan.tmpls_res).filter_by(id=task_id).first()
        return BaseRespController.success(str(task_info[0]))
    except SQLAlchemyError:
        return BaseRespController.failed()


@app.get(SentryRouters.TMPL_SCAN)
async def get_tmpl_scan_history() -> BaseResponse:
    """
    This view function acts as a template scanning history viewing interface
    """
    try:
        all_task_info = []
        for task in session.query(TmplScan).all():
            task_dict = {key: value for key, value in task.__dict__.items() if key != '_sa_instance_state'}
            all_task_info.append(task_dict)
        return BaseRespController.success(data=all_task_info)
    except SQLAlchemyError:
        return BaseRespController.failed()


@app.post(SentryRouters.PORT_SCAN)
async def create_port_scan_task(port_scan_task: PortScanTaskCreateModel) -> TaskStatusResp:
    """
    This view receives POST requests to add port scanning tasks to the Task queue controller
    """
    status = TaskQueueController.add_new_port_scan_task(
        task_name=port_scan_task.task_name, target=port_scan_task.target
    )
    if status[0]:
        return TaskStatusRespController.success(task_id=status[1], task_name=status[2])
    return TaskStatusRespController.failed()


@app.get(SentryRouters.PORT_SCAN_SPECIFIC)
async def get_port_scan_info(task_id: int) -> BaseResponse:
    """
    This view function needs to pass in the task ID parameter as the view port scanning target task index
    """
    try:
        task_info = session.query(PortScan.port_scan).filter_by(id=task_id).first()
        return BaseRespController.success(str(task_info[0]))
    except SQLAlchemyError:
        return BaseRespController.failed()


@app.get(SentryRouters.PORT_SCAN)
async def get_port_scan_history() -> BaseResponse:
    """
    This view function acts as a port scanning history viewing interface
    """
    try:
        all_task_info = []
        for task in session.query(PortScan).all():
            task_dict = {key: value for key, value in task.__dict__.items() if key != '_sa_instance_state'}
            all_task_info.append(task_dict)
        return BaseRespController.success(data=all_task_info)
    except SQLAlchemyError:
        return BaseRespController.failed()


@app.get(SentryRouters.CRAWLER_IMG)
async def get_website_images_analyse():
    try:
        img_res = session.query(Crawler.img_analyzer).all()
        return BaseRespController.success(data=str(img_res))
    except SQLAlchemyError:
        return BaseRespController.failed()


@app.get(SentryRouters.AI_CRAWLER_ANALYSE)
async def get_ai_for_crawler(task_id: int) -> BaseResponse:
    if analyse_res := QuestionTemplateController.get_crawler_analyse_res(task_id):
        return BaseRespController.success(analyse_res)
    return BaseRespController.failed()


@app.get(SentryRouters.AI_PORT_ANALYSE)
async def get_ai_for_port_scan(task_id: int) -> BaseResponse:
    if analyse_res := QuestionTemplateController.get_port_scan_analyse_res(task_id):
        return BaseRespController.success(analyse_res)
    return BaseRespController.failed()


@app.get(SentryRouters.AI_IMAGE_ANALYSE)
async def get_ai_for_images(task_id: int) -> BaseResponse:
    if analyse_res := QuestionTemplateController.get_images_analyse_res(task_id):
        return BaseRespController.success(analyse_res)
    return BaseRespController.failed()


@app.get(SentryRouters.AI_VUL_SCAN_ANALYSE)
async def get_ai_for_tmpl_scan(task_id: int) -> BaseResponse:
    if analyse_res := QuestionTemplateController.get_tmpl_scan_analyse_res(task_id):
        return BaseRespController.success(analyse_res)
    return BaseRespController.failed()


@app.get(SentryRouters.AI_VUL_NEWS_ANALYSE)
async def get_ai_for_vul_news(vul_news: VulNewsAnalyseModel) -> BaseResponse:
    if analyse_res := QuestionTemplateController.get_vul_news_analyse_res(vul_news.content):
        return BaseRespController.success(analyse_res)
    return BaseRespController.failed()
