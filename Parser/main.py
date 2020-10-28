from y_disk import Disk
from metropolitan import Metropolitan


if __name__ == "__main__":
    token = 'Здесь токен'
    recorded_images = "Путь до файла с id'шниками спарсеных изображений"
    
    y = Disk(token=token)
    y.set_new_work_directory('/CSC/NIR/Goskatalog/Parser/Metropolitan/')
    conditions = ['hasImages=true', 'medium=Sculpture', 'q=Sculpture']
    search = 'https://collectionapi.metmuseum.org/public/collection/v1/search?'
    metro = Metropolitan(search, conditions, recorded_images, y)

    metro.progress()

    # print(len(list(y.y.listdir('/CSC/NIR/Goskatalog/Parser/Metropolitan', n_retries=10, retry_interval=5, timeout=100))))