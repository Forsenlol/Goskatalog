import yadisk
import datetime as dt
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = logging.getLogger(__name__)


class Disk:

    def __init__(self, id=None, secret=None, token=None):
        self.y = yadisk.YaDisk(id=id, secret=secret, token=token)
        self.work_directory = '/'

    def set_new_work_directory(self, path='/'):
        self.work_directory = path

    def create_directory(self, name):
        self.y.mkdir(f'{self.work_directory}{name}')

    def upload(self, file, filename):
        logger.info(f'{dt.datetime.now()} - path in y_disk - "{self.work_directory}{filename}"')
        try:
            self.y.upload(file, f'{self.work_directory}{filename}')
        except yadisk.exceptions.YaDiskError as exc:
            logger.warning(f'{dt.datetime.now()} - warning on file - "{self.work_directory}{filename}". Error: {exc}')
