from sentry.settings import USER_AGENT_DICT_PATH, LOGGER_CONF_PATH
from logging.config import fileConfig
from urllib.parse import urljoin
from pyzbar.pyzbar import decode
from bs4 import BeautifulSoup
from typing import Final
from io import BytesIO

import PIL.Image
import requests
import logging
import base64
import random
import json
import PIL
import re


def web_images_analyzer_action(url: str) -> str | None:
    """
    Return json string format:
    [
        {
            "image_link": "http://example.com/download.png",
            "image_content": [
                "http://example.com/"
            ],
            "image_base64": "image_base64_content"
        }
    ]
    """

    class AnalyzerRuntimeMETA:
        LOGGER_CONFIG_PATH: Final[str] = LOGGER_CONF_PATH
        DEFAULT_LOGGER_NAME: Final[str] = "analyzerLogger"
        DEFAULT_USER_AGENT_PATH: Final[str] = USER_AGENT_DICT_PATH
        RELATIVE_PATH_REPLACE_PATTERNS: Final[tuple[tuple[str, str]]] = ((r"\\", "/"), )

    class AnalyzerLoggingStatus:
        JSON_DATA_LOAD_ERROR: Final[str] = "JSONDataLoadError - Load user define json error. The json invalid !"
        NOT_EXISTS_TASK_ERROR: Final[str] = "NotExistsTaskError - No task data is provided !"
        NOT_EXISTS_FILE_ERROR: Final[str] = "NotExistsFileError - RuntimeMATA Key file missing error !"
        NOT_FOUND_TASK_INFO_ERROR: Final[str] = "NotFoundTaskInfoError - No task info data is provided !"
        TASK_INFO_INVALID_ERROR: Final[
            str] = "TaskInfoInvalidError - Load user define task_info error. The task_info invalid !"
        TASK_EXECUTE_TIMEOUT_WARNING: Final[str] = "TaskExecuteTimeoutWarning - Timeout !"
        TASK_REQUEST_FAILED_ERROR: Final[str] = "TaskRequestFailedError - Failed to request the target URL !"
        IMG_EXT_NOT_UNIDENTIFIED_WARNING: Final[str] = "UnidentifiedImageWarning - This image is not recognized !"
        IMG_NOT_TRANSITION_WARNING: Final[str] = "NotTransitionImageWarning - Picture conversion exception !"
        ANALYSE_FAILED_INFO: Final[str] = "AnalyseFailedInfo - Website image parsing failed !"
        ANALYSE_SUCCESS_INFO: Final[str] = "AnalyseSucceedInfo - Website image parsing succeed !"

    fileConfig(AnalyzerRuntimeMETA.LOGGER_CONFIG_PATH)
    analyzer_logger: logging.Logger = logging.getLogger(AnalyzerRuntimeMETA.DEFAULT_LOGGER_NAME)

    def task_json_loads(target_url: str) -> dict[str, str] | None:
        if target_url is None:
            analyzer_logger.error(AnalyzerLoggingStatus.NOT_EXISTS_TASK_ERROR)
            return None
        return {"url": target_url}

    def relative_path_character_filter(original: str) -> str | None:
        if isinstance(original, str) and original != "":
            for pattern in AnalyzerRuntimeMETA.RELATIVE_PATH_REPLACE_PATTERNS:
                original = re.sub(pattern[0], pattern[-1], original)
                return original
        return None

    def request_user_data_decider(user_data_dict: dict[str, str] | str) -> bool:
        if user_data_dict is not None and user_data_dict != "":
            return True
        return False

    def request_session_builder(task: dict[str, str]) -> requests.Session | None:
        if not isinstance(task, dict):
            analyzer_logger.error(AnalyzerLoggingStatus.NOT_EXISTS_TASK_ERROR)
            return None

        user_def_cookies: dict[str, str] = task.get("cookies", '')
        user_def_headers: dict[str, str] = task.get("headers", '')
        user_def_url: str = task.get("url", '')
        ses: requests.Session = requests.session()

        if request_user_data_decider(user_def_headers):
            ses.headers.update(user_def_headers)
        else:
            try:
                with open(AnalyzerRuntimeMETA.DEFAULT_USER_AGENT_PATH, 'r') as f:
                    ses.headers['User-Agent'] = random.choice(f.readlines()).strip()
            except FileNotFoundError:
                analyzer_logger.error(AnalyzerLoggingStatus.NOT_EXISTS_FILE_ERROR)

        if request_user_data_decider(user_def_cookies):
            ses.cookies.update(user_def_cookies)
        else:
            if request_user_data_decider(user_def_url):
                initiate_request(user_def_url, ses)
        return ses

    def initiate_request(task_url: str, img_task_session: requests.Session) -> requests.Response | None:
        img_task_response: requests.Response | None = None
        try:
            img_task_response = img_task_session.get(url=task_url, timeout=2)
        except requests.exceptions.InvalidURL:
            analyzer_logger.error(AnalyzerLoggingStatus.TASK_INFO_INVALID_ERROR)
        except requests.exceptions.Timeout:
            analyzer_logger.warning(AnalyzerLoggingStatus.TASK_EXECUTE_TIMEOUT_WARNING)
        except requests.exceptions.ConnectionError:
            analyzer_logger.error(AnalyzerLoggingStatus.TASK_REQUEST_FAILED_ERROR)

        return img_task_response

    def capture_qrcode_images(base_url: str, img_task_response: requests.Response) -> tuple[str] | None:
        if isinstance(img_task_response, requests.Response) and base_url is None and base_url != "":
            analyzer_logger.error(AnalyzerLoggingStatus.NOT_EXISTS_TASK_ERROR)
            return None

        soup = BeautifulSoup(img_task_response.text, "html.parser")
        image_links: list[str] = []

        for img in soup.find_all('img', src=True):
            img_src: str = relative_path_character_filter(img['src'])
            if not img_src.startswith('http'):
                img_src = urljoin(base_url, img_src)
            image_links.append(img_src)
        return tuple(image_links)

    def image_to_base64(img: PIL.Image.Image) -> str | None:
        if isinstance(img, PIL.Image.Image):
            buffered = BytesIO()
            img_format = img.format if img.format else "PNG"
            try:
                img.save(buffered, format=img_format)
                return base64.b64encode(buffered.getvalue()).decode('utf-8')
            except Exception:
                analyzer_logger.warning(AnalyzerLoggingStatus.IMG_NOT_TRANSITION_WARNING)
        return None

    def qrcode_images_decider(img_src: str, img_task_session: requests.Session) -> (
            tuple[bool, list | None, PIL.Image.Image | None]):

        """
        Returns a triple: (Discriminating Mark  => boolean, 
                           QR code content list => list, 
                           PIL.Image Object of QR code => PIL.Image.Image ) 
        """

        if img_src != "" and img_src is not None and isinstance(img_task_session, requests.Session):
            try:
                img = img_task_session.get(img_src, timeout=2).content
                img = PIL.Image.open(BytesIO(img))
                decode_object = decode(img)
                if len(decode_object) > 0 and any(obj.type == 'QRCODE' for obj in decode_object):
                    return True, decode_object, img
            except requests.exceptions.InvalidURL:
                analyzer_logger.error(AnalyzerLoggingStatus.TASK_INFO_INVALID_ERROR)
            except requests.exceptions.Timeout:
                analyzer_logger.warning(AnalyzerLoggingStatus.TASK_EXECUTE_TIMEOUT_WARNING)
            except (PIL.UnidentifiedImageError, IndexError):
                analyzer_logger.warning(AnalyzerLoggingStatus.IMG_EXT_NOT_UNIDENTIFIED_WARNING)
        return False, None, None

    def qrcode_images_analyzer(images: tuple[str], img_site_session: requests.Session) \
            -> list[dict[str, str | list[str]]]:

        """
        Returns a tuple of elements, 
        the first tuple being a list tuple of the contents of the picture, 
        and the second being a base64 encoded tuple of the picture
        """

        if isinstance(images, tuple) and isinstance(img_site_session, requests.Session):
            final_filter_res: list[dict] = []
            for image in images:
                tmp_res_tuple: tuple = qrcode_images_decider(image, img_site_session)
                if tmp_res_tuple[0]:
                    image_content: list[str] = [img_cont.data.decode("utf-8") for img_cont in tmp_res_tuple[1]]
                    image_base64: str = image_to_base64(tmp_res_tuple[-1])
                    final_filter_res.append(
                        {"image_link": image, "image_content": image_content, "image_base64": image_base64})

            return final_filter_res

    if not isinstance(url, str):
        return None

    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    try:
        task_info = task_json_loads(target_url=url)
        session = request_session_builder(task=task_info)
        response = initiate_request(task_info.get("url", ""), img_task_session=session)
        image_src_attrs = capture_qrcode_images(task_info.get("url", ""), img_task_response=response)
        print(image_src_attrs)
        analyse_res = qrcode_images_analyzer(image_src_attrs, img_site_session=session)
        if analyse_res is not None:
            analyzer_logger.info(AnalyzerLoggingStatus.ANALYSE_SUCCESS_INFO)
            return json.dumps(analyse_res)
    except Exception:
        analyzer_logger.info(AnalyzerLoggingStatus.ANALYSE_FAILED_INFO)
        return None
