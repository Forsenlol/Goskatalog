import requests
import datetime as dt
import tempfile
import logging
import sys
from dataclasses import dataclass
logging.basicConfig(stream=sys.stdout)

logger = logging.getLogger(__name__)


@dataclass(frozen=False)
class Image:
    filename: str
    url: str


class Metropolitan:

    def __init__(self, search, conditions, filename, y):
        self.search = search
        self.conditions = conditions
        with open(filename, 'r') as file:
            content = file.readlines()
        self.recorded_images = {x.strip() for x in content}
        self.filename = filename
        self.y = y
        self.template = 'https://collectionapi.metmuseum.org/public/collection/v1/objects/'
        self.sculptures = None
        self.bad_symbols = ['~', '#', '%', '&', '*', '{', '}', '\\', ':', '<', '>', '?', '/', '+', '|', '"']

    def _delete_bad_symbols(self, filename):
        for bad_symbol in self.bad_symbols:
            filename = filename.replace(bad_symbol, '')
        return filename

    def _preparation_data(self):
        self.search += '&'.join(self.conditions)
        response = requests.get(self.search)
        if response.ok:
            self.sculptures = response.json()
        else:
            raise Exception('Bad search requests. Check link and conditions')

    def _write_file(self, images):
        with tempfile.TemporaryDirectory() as directory:
            for image in images:
                filename = image.filename
                p = requests.get(image.url)
                try:
                    with open(f'{directory}{filename}', 'wb') as file:
                        file.write(p.content)
                except OSError:
                    filename = self._delete_bad_symbols(filename)
                    with open(f'{directory}{filename}', 'wb') as file:
                        file.write(p.content)
                with open(f'{directory}{filename}', 'rb') as file:
                    self.y.upload(file, filename)
                logger.info(f'{dt.datetime.now()} - write file - {filename}')

    def _get_filename(self, id, title, additional_images=False):
        images = list()
        if additional_images:
            if not title:
                filename = f'{str(id)}_0.jpg'
                temp = str(id)
            else:
                filename = f'{str(title)}_0.jpg'
                temp = str(title)
            for i, img in enumerate(additional_images):
                images.append(Image(url=str(img), filename=f'{temp}_{str(i + 1)}.jpg'))
        else:
            if not title:
                filename = f'{str(id)}.jpg'
            else:
                filename = f'{str(title)}.jpg'
        images.append(Image(filename=filename, url=''))
        return images

    def _download_images(self):
        for id in self.sculptures.get('objectIDs', list()):
            try:
                if str(id) in self.recorded_images:
                    logger.info(f'{dt.datetime.now()} - image with id - {id} already loaded')
                    continue

                response = requests.get(f'{self.template}{str(id)}')
                if not response.ok:
                    logger.warning(f'{dt.datetime.now()} - bad requests on image - {str(id)}')
                    continue
                response = response.json()

                if not response.get('primaryImage'):
                    logger.info(f'{dt.datetime.now()} - image - {str(id)} does not have "primaryImage"')
                    continue

                images = self._get_filename(id, response.get('title'), response.get('additionalImages', list()))
                url = response.get('primaryImage')
                images[-1].url = url
                self._write_file(images)

                with open(self.filename, 'a') as file:
                    file.write(f'{str(id)}\n')
            except Exception as exc:
                logger.error(f'{dt.datetime.now()} - error = {exc}')

    def progress(self):
        self._preparation_data()
        self._download_images()
