from Parser.y_disk import Disk
from Parser.metropolitan import Metropolitan
from Parser.local import Local
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info('start programm')
    token = ''
    filename_recorded_images = ''
    filename_index_name_images = ''

    logger.info('start y_disk')
    y = Disk(token=token)
    y.set_new_work_directory('/CSC/NIR/Goskatalog/Parser/Metropolitan/')

    logger.info('start local_disk')
    l = Local(images_directory='',
              meta_data_csv='',
              mapping_csv='')
    l.preparation_data()

    logger.info('start Metropolitan')
    conditions = ['hasImages=true', 'medium=Sculpture', 'q=Sculpture']
    search = 'https://collectionapi.metmuseum.org/public/collection/v1/search?'
    metro = Metropolitan(search=search, conditions=conditions, filename_recorded_images=filename_recorded_images,
                         filename_index_name_images=filename_index_name_images, y=y, l=l)

    logger.info('run progress_local')
    # metro.progress_web()
    metro.progress_local()

    # print(len(list(y.y.listdir('/CSC/NIR/Goskatalog/Parser/Metropolitan', n_retries=10, retry_interval=5, timeout=100))))