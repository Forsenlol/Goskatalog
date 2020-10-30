import pandas as pd
import csv


class Local:

    def __init__(self, images_directory, mapping_csv, meta_data_csv):
        self.images_directory = images_directory
        self.mapping_csv = mapping_csv
        self.meta_data_csv = meta_data_csv

        self.meta_data_csv_header = None
        self.meta_data_csv_last_index = None

        self.mapping_csv_header = None
        self.mapping_csv_last_index = None

        csv.register_dialect('my_dialect', delimiter='\t', lineterminator='\n')

    def preparation_data(self):
        try:
            meta_data_csv = pd.read_csv(self.meta_data_csv, delimiter='\t')
            self.meta_data_csv_header = meta_data_csv.columns
            self.meta_data_csv_last_index = int(meta_data_csv['id'].max() + 1)
        except pd.errors.EmptyDataError:
            self.meta_data_csv_header = None
            self.meta_data_csv_last_index = 0

        try:
            mapping_csv = pd.read_csv(self.mapping_csv, delimiter='\t')
            self.mapping_csv_header = mapping_csv.columns
        except pd.errors.EmptyDataError:
            self.mapping_csv_header = None

    def write_file(self, filename, content):
        with open(f'{self.images_directory}{filename}', 'wb') as file:
            file.write(content)

    def write_header(self, file, header):
        with open(file, 'w', newline='\n') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header, dialect='my_dialect')
            writer.writeheader()

    def write_meta_data(self, data):
        if self.meta_data_csv_header is None:
            self.meta_data_csv_header = ['id', *data.keys()]
            self.write_header(file=self.meta_data_csv, header=self.meta_data_csv_header)
        with open(self.meta_data_csv, 'a', newline='\n') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.meta_data_csv_header, dialect='my_dialect')
            data['id'] = self.meta_data_csv_last_index
            self.meta_data_csv_last_index += 1
            writer.writerow(data)
        return int(self.meta_data_csv_last_index - 1)

    def write_mapping(self, image_id, meta_data_id, object_id):
        if self.mapping_csv_header is None:
            self.mapping_csv_header = ['image_id', 'meta_data_id', 'object_id']
            self.write_header(file=self.mapping_csv, header=self.mapping_csv_header)
        with open(self.mapping_csv, 'a', newline='\n') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.mapping_csv_header, dialect='my_dialect')
            writer.writerow({'image_id': image_id, 'meta_data_id': meta_data_id, 'object_id': object_id})