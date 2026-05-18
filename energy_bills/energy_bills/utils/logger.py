# ----------------------- Logging of Events ---------------------------------- 
import os, sys, logging
from logging.handlers import RotatingFileHandler
from typing import Union

class BaseLogger:
    def __init__(self, *args, **kwargs):
        self.loglevel: Union[str, int] = logging.INFO
        self.BASE_DIR = "/tmp" if os.getenv("RSTUDIO_PRODUCT") == "CONNECT" else os.path.expanduser("/home/eyzacharis/Energy Bills/")
        self.LOG_DIR  = os.path.join(self.BASE_DIR, "logs")
        self.LOG_FILE = os.path.join(self.LOG_DIR, "energy_bills_automation.log")
        self.log_filepath = os.path.join(self.LOG_DIR, "energy_bills_automation.log")
        os.makedirs(self.LOG_DIR, exist_ok=True)
        self.logger = self._build_logger()

    def _build_logger(self):
        """A single utility to build an interpretable logger prototype"""
        
        logger = logging.getLogger("energy_bills_automation_logger")
        logger.setLevel(self.loglevel)

        def handle_exception(exc_type, exc_value, exc_traceback):
            logger.critical(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback))
        sys.excepthook = handle_exception
        
        # Prevent accumulation of concurrent loggers
        if not logger.handlers:
            
            # Define uniform formatter of log output stream
            formatter = logging.Formatter(
#                     fmt="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d]: %(message)s",
                    fmt="%(asctime)s %(levelname)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s",
                    datefmt="%d-%m-%Y %H:%M:%S")
            
            # Create RotatingFile Handler - archived
            rfile_handler = RotatingFileHandler(
                filename=self.log_filepath,
                maxBytes=1_000_000,
                backupCount=3)
            rfile_handler.setLevel(self.loglevel)
            rfile_handler.setFormatter(formatter)
            
            # File Handler
            file_handler = logging.FileHandler(
                filename=self.log_filepath,
                mode='w',
                encoding='utf-8')
            file_handler.setLevel(self.loglevel)
            file_handler.setFormatter(formatter)
            
            # Create console handler
            ch = logging.StreamHandler(stream=sys.stderr)
            ch.setLevel(self.loglevel)
            ch.setFormatter(formatter)
            
            # Set handlers to logger
            logger.addHandler(file_handler)
            logger.addHandler(ch)

        return logger