import requests
import datetime as dt
import tempfile
import logging
import sys
from dataclasses import dataclass
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = logging.getLogger(__name__)


@dataclass(frozen=False)
class Image:
    filename: str
    url: str


class Metropolitan:

    def __init__(self, search, conditions, filename_recorded_images, filename_index_name_images, y, l):
        self.search = search
        self.conditions = conditions

        with open(filename_recorded_images, 'r') as file:
            content = file.readlines()
        self.recorded_images = {x.strip() for x in content}
        self.filename_recorded_images = filename_recorded_images

        with open(filename_index_name_images, 'r') as file:
            content = file.readlines()
            if content:
                self.index_name_image = max([int(x) for x in content]) + 1
            else:
                self.index_name_image = 0
        self.filename_index_name_images = filename_index_name_images

        self.y = y
        self.l = l
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

    def _write_file_local(self, images):
        for image in images:
            filename = image.filename
            p = requests.get(image.url)
            self.l.write_file(filename, p.content)

    def _write_file_web(self, images):
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

    def _get_filename_local(self, additional_images):
        images = list()
        images.append(Image(url='', filename=f'{str(self.index_name_image)}.jpg'))
        self.index_name_image += 1
        for img in additional_images:
            images.append(Image(url=str(img), filename=f'{str(self.index_name_image)}.jpg'))
            self.index_name_image += 1
        return images

    def _get_filename_web(self, id, title, additional_images=False):
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

    def _download_images_local(self):
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

                logger.info(f'write meta_data image - {id} ')
                meta_data_id = self.l.write_meta_data(response)

                images = self._get_filename_local(response.get('additionalImages', list()))
                url = response.get('primaryImage')
                images[0].url = url
                logger.info(f'save files, image - {id} ')
                self._write_file_local(images)

                with open(self.filename_index_name_images, 'a') as file:
                    for image in images:
                        self.l.write_mapping(image.filename[:-4], meta_data_id, id)
                        file.write(f'{image.filename[:-4]}\n')

                with open(self.filename_recorded_images, 'a') as file:
                    file.write(f'{str(id)}\n')
            except Exception as exc:
                logger.error(f'{dt.datetime.now()} - error = {exc}')

    def _download_images_web(self):
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

                images = self._get_filename_web(id, response.get('title'), response.get('additionalImages', list()))
                url = response.get('primaryImage')
                images[-1].url = url
                self._write_file_web(images)

                with open(self.filename_recorded_images, 'a') as file:
                    file.write(f'{str(id)}\n')
            except Exception as exc:
                logger.error(f'{dt.datetime.now()} - error = {exc}')

    def progress_web(self):
        self._preparation_data()
        self._download_images_web()

    def progress_local(self):
        self._preparation_data()
        self._download_images_local()
