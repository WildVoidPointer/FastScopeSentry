from pydantic import BaseModel


class CrawlerTaskCreateModel(BaseModel):
    task_name: str
    target: str


class TmplScanTaskCreateModel(BaseModel):
    task_name: str
    target: str
    # template: str | None = None


class PortScanTaskCreateModel(BaseModel):
    task_name: str
    target: str


class VulNewsAnalyseModel(BaseModel):
    content: str
