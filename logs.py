import logging
import time

def log():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    main_log_handler = logging.FileHandler("log/MyStrategy_{0}.log".format(time.strftime("%Y%m%d")), mode="a",
                                           encoding="utf-8")
    main_log_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    main_log_handler.setFormatter(formatter)
    logger.addHandler(main_log_handler)
    return logger
