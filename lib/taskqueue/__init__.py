from .taskmodel import MultiTaskModelInterFace, MultiTemplateScanModel
from .taskmodel import MultiCrawlerTaskModel, MultiPortScanTaskModel
from sentry.settings import TASK_EXECUTE_CYCLE

from queue import Queue, Full
import threading
import time


class TaskQueueController:
    __GLOBAL_TASK_QUEUE: Queue[MultiTaskModelInterFace] = Queue()

    @staticmethod
    def add_new_crawler_task(task_name: str, target: str) -> tuple[bool, int | None, str | None]:
        current_scan_task: MultiCrawlerTaskModel = MultiCrawlerTaskModel(
            target=target, task_name=task_name
        )
        save_status: tuple[bool, int | None, str | None] = current_scan_task.create_task_record()
        if save_status[0]:
            try:
                TaskQueueController.__GLOBAL_TASK_QUEUE.put(current_scan_task)
            except Full:
                pass
        return save_status

    @staticmethod
    def add_new_tmpl_scan_task(task_name: str, target: str, tmpl: str | None = None) -> (
            tuple[bool, int | None, str | None]
    ):
        current_scan_task: MultiTemplateScanModel = MultiTemplateScanModel(
            target=target, task_name=task_name, tmpl=tmpl
        )
        save_status: tuple[bool, int | None, str | None] = current_scan_task.create_task_record()
        if save_status[0]:
            try:
                TaskQueueController.__GLOBAL_TASK_QUEUE.put(current_scan_task)
            except Full:
                pass
        return save_status

    @staticmethod
    def add_new_port_scan_task(task_name: str, target: str) -> tuple[bool, int | None, str | None]:
        current_scan_task: MultiPortScanTaskModel = MultiPortScanTaskModel(
            target=target, task_name=task_name
        )
        save_status: tuple[bool, int | None, str | None] = current_scan_task.create_task_record()
        if save_status[0]:
            try:
                TaskQueueController.__GLOBAL_TASK_QUEUE.put(current_scan_task)
            except Full:
                pass
        return save_status

    @staticmethod
    def multi_exec_queue_task(interval: float = TASK_EXECUTE_CYCLE) -> None:
        while True:
            while not TaskQueueController.__GLOBAL_TASK_QUEUE.empty():
                t_task = TaskQueueController.__GLOBAL_TASK_QUEUE.get()
                t_task.start()
            time.sleep(interval)


def __task_processor_init():
    crawler_exec_thread = threading.Thread(target=TaskQueueController.multi_exec_queue_task, daemon=True)
    crawler_exec_thread.start()

    crawler_exec_thread.join()


thread_exec = threading.Thread(target=__task_processor_init)
thread_exec.start()
