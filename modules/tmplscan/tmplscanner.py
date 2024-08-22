from sentry.settings import LOGGER_CONF_PATH, TEMPLATE_SCAN_SERVICE_PATH
from logging.config import fileConfig
from typing import Final
import subprocess
import logging
import json
import re


def activate_scanning_main(target: dict[str, str | None]) -> str | None:
    """
    # Intermediate data is not verified
    # Standard task dict format : {'url': 'https://example.com', 'template': 'path/to/template'}
    # Return result json format : { "results": [results, ...] }
    """

    class CallScannerOperators:
        SCANNER_PATH: Final[str] = TEMPLATE_SCAN_SERVICE_PATH
        URL_OPTION_FLAG: Final[str] = '-u'
        TEMPLATE_OPTION_FLAG: Final[str] = '-t'
        SCANNER_SILENT_FLAG: Final[str] = '-silent'
        SCANNER_NOT_COLOR_FLAG: Final[str] = '-nc'
        RES_REPLACE_REGEX: Final[str] = r"nuclei"
        RES_REPLACE_TARGET: Final[str] = "scanner"
        BASE_TASK_COMMAND: Final[tuple] = (SCANNER_PATH, URL_OPTION_FLAG)
        RES_FILTER_REGEX: Final[str] = r"\[(.*?)\]"
        SCANNING_LOGGER_CONFIG: Final[str] = LOGGER_CONF_PATH
        SCANNING_LOGGER_NAME: Final[str] = "scanningLogger"

    class ScanningLoggingStatus:
        SCANNING_RUNTIME_ERROR: Final[str] = "ScanningRuntimeError - Scanning task execution error !"
        SCANNING_FAILED_ERROR: Final[str] = "ScanningFailedError - The scan failed. The result invalid !"
        SCANNING_SUCCEED_FLAG: Final[str] = "ScanningComplete - The scan is successful. The results are valid !"
        JSON_DATA_LOAD_ERROR: Final[str] = "JSONDataLoadError - Load user define json error. The json invalid !"
        NOT_EXISTS_URL_ERROR: Final[str] = "NotExistsURLError - No URL data is provided !"
        NOT_EXISTS_TEMPLATE_WARNING: Final[str] = ("NotExistsTemplateWarning - No template is provided."
                                                   "Automatic scanning is performed by default !")
        DATA_CORRUPTED_ERROR: Final[str] = " DataCorruptedError - A serious error occurred and the data was corrupted !"

    class UserDefineTargetInfoEnum:
        USER_DEFINE_U: Final[str] = "url"
        USER_DEFINE_T: Final[str] = "template"

    fileConfig(CallScannerOperators.SCANNING_LOGGER_CONFIG)
    scanning_logger: logging.Logger = logging.getLogger(CallScannerOperators.SCANNING_LOGGER_NAME)

    def get_target_info(target_info: str) -> dict[str, str] | None:
        if target_info is not None and target_info != "":
            try:
                load_res: dict[str, str] = json.loads(target_info)
                return load_res
            except json.JSONDecodeError:
                scanning_logger.error(ScanningLoggingStatus.JSON_DATA_LOAD_ERROR)
        return None

    def generate_task_command(target_dict: dict[str, str]) -> tuple[str] | None:
        task_command: list[str] | tuple[str] | None = None
        if target_dict is not None and isinstance(target_dict, dict):
            try:
                task_command = list(CallScannerOperators.BASE_TASK_COMMAND)
                task_command.append(target_dict.get(UserDefineTargetInfoEnum.USER_DEFINE_U))

            except KeyError:
                scanning_logger.error(ScanningLoggingStatus.NOT_EXISTS_URL_ERROR)
                return None
            else:
                t_exists_flag: bool = (
                    True if UserDefineTargetInfoEnum.USER_DEFINE_T in target_dict else False
                )

                t_path: str = target_dict.get(UserDefineTargetInfoEnum.USER_DEFINE_T, '')

                if t_exists_flag and t_path != '' and isinstance(t_path, str):
                    task_command.append(CallScannerOperators.TEMPLATE_OPTION_FLAG)
                    task_command.append(t_path)
                else:
                    scanning_logger.warning(ScanningLoggingStatus.NOT_EXISTS_TEMPLATE_WARNING)
                task_command.append(CallScannerOperators.SCANNER_SILENT_FLAG)
                task_command.append(CallScannerOperators.SCANNER_NOT_COLOR_FLAG)

        return tuple(task_command)

    def execute_scanning_task(task: tuple[str]) -> tuple[bool, str] | None:
        if task is not None and isinstance(task, tuple):
            complete_result: subprocess.CompletedProcess[str] = (
                subprocess.run(task, capture_output=True, text=True))
        else:
            return None

        if complete_result.returncode == 0:
            return True, complete_result.stdout.strip('\n')
        else:
            scanning_logger.error(ScanningLoggingStatus.SCANNING_RUNTIME_ERROR)
            return False, complete_result.stderr.strip('\n')

    def scanning_stderr_line_filter(scanning_res: str | None = None) -> str | None:
        if scanning_res is not None and scanning_res != "":
            scanning_res = re.sub(CallScannerOperators.RES_REPLACE_REGEX,
                                  CallScannerOperators.RES_REPLACE_TARGET, scanning_res)
            return re.sub(CallScannerOperators.RES_FILTER_REGEX, '', scanning_res).strip()
        return None

    def scanning_stdout_line_filter(scanning_res: str | None = None) -> str | None:
        if scanning_res is not None and scanning_res != "":
            tmp_matches: list[str] = re.findall(CallScannerOperators.RES_FILTER_REGEX, scanning_res)
            if len(tmp_matches) > 3:
                return f"{tmp_matches[0]}: {tmp_matches[3]}"
            elif len(tmp_matches) > 0:
                return tmp_matches[0]
        return None

    def collect_task_results(res: tuple[bool, str]) -> str | None:
        final_task_res: dict[str, list[tuple[str, str] | None]] | None = None
        if res is not None and isinstance(res, tuple):
            if res[0]:
                final_task_res = {
                    "results": [scanning_stdout_line_filter(res_line) for res_line in res[1].split('\n')
                                if scanning_stdout_line_filter(res_line) is not None]
                }
                scanning_logger.info(ScanningLoggingStatus.SCANNING_SUCCEED_FLAG)

            else:
                final_task_res = {
                    "results": [scanning_stderr_line_filter(res_line) for res_line in res[1].split('\n')
                                if scanning_stderr_line_filter(res_line) is not None]
                }
                scanning_logger.warning(ScanningLoggingStatus.SCANNING_FAILED_ERROR)

        try:
            return json.dumps(final_task_res)
        except json.JSONDecodeError:
            scanning_logger.critical(ScanningLoggingStatus.DATA_CORRUPTED_ERROR)
            return None

    final_scan_res: str | None = None
    try:
        # target_details: dict[str, str] = get_target_info(target_info=target)
        task_details = generate_task_command(target_dict=target)
        exec_res = execute_scanning_task(task=task_details)
        print(exec_res)
        final_scan_res = collect_task_results(exec_res)
    except Exception:
        scanning_logger.critical(ScanningLoggingStatus.DATA_CORRUPTED_ERROR)
    finally:
        return final_scan_res
