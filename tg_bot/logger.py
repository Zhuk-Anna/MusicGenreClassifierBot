import logging
import os
from config import LOG_DIR, USER_ERROR_REPORT_LEVEL

os.makedirs(LOG_DIR, exist_ok=True)
logging.addLevelName(USER_ERROR_REPORT_LEVEL, "USER_ERROR_REPORT")


def user_error_report(self, message, *args, **kwargs):
    if self.isEnabledFor(USER_ERROR_REPORT_LEVEL):
        self._log(USER_ERROR_REPORT_LEVEL, message, args, **kwargs)

logging.Logger.user_error_report = user_error_report

def only_user_error_report(record):
    return record.levelno == USER_ERROR_REPORT_LEVEL


def get_logger(name="tg_bot"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Проверяем, чтобы повторно не добавлять обработчики
    if not logger.hasHandlers():

        # Консольный вывод
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        # console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        # Файл для всех логов
        file_handler = logging.FileHandler(os.path.join(LOG_DIR, "bot.log"), encoding="utf-8")
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        # file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        # Файл для сообщений об ошибках
        user_error_file_handler = logging.FileHandler(os.path.join(LOG_DIR, "user_error_messages.log"), encoding="utf-8")
        error_file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        user_error_file_handler.setFormatter(error_file_formatter)
        user_error_file_handler.setLevel(USER_ERROR_REPORT_LEVEL)
        user_error_file_handler.addFilter(only_user_error_report)
        logger.addHandler(user_error_file_handler)

    return logger