import ku
from ku import model_helper as mh
from ku import applications as apps
from ku import tensor_ops as ops
from ku import generic as gen
from ku import image_utils as img
from keras.layers import Input, GlobalAveragePooling2D
from keras.models import Model
import pandas as pd
import numpy as np
import os


root_path = '/content/ava-mlsp/'

dataset = root_path + 'metadata/AVA_data_official_test.csv';
images_path = root_path + 'images/'
ids = pd.read_csv(dataset)


class MLSP:

    def __init__(self, root_path):
        self.root_path = root_path
        self.dataset = f'{root_path}metadata/AVA_data_official_test.csv'
        self.images_path = f'{root_path}images/'
        self.ids = pd.read_csv(self.dataset)
        self.model_name = 'mlsp_wide_orig'
        self.input_shape = (None, None, 3)
        self.helper = None
        self.pre = None


    def progress(self):
        model_base = apps.model_inceptionresnet_pooled(self.input_shape)
        self.pre = apps.process_input[apps.InceptionResNetV2]


        input_feats = Input(shape=(5, 5, 16928), dtype='float32')
        x = apps.inception_block(input_feats, size=1024)
        x = GlobalAveragePooling2D(name='final_GAP')(x)

        pred = apps.fc_layers(x, name='head', fc_sizes=[2048, 1024, 256,  1], dropout_rates=[0.25, 0.25, 0.5, 0],
                              batch_norm=2)

        model = Model(inputs=input_feats, outputs=pred)

        gen_params = dict(batch_size=1, data_path=self.images_path, process_fn=self.pre, input_shape=self.input_shape,
                          inputs='image_name', outputs='MOS', fixed_batches=False)

        self.helper = mh.ModelHelper(model, self.model_name, self.ids, gen_params=gen_params)

        self.helper.load_model(model_name=f'{self.root_path}models/irnv2_mlsp_wide_orig/model')

        self.helper.model = Model(inputs=model_base.input, outputs=model(model_base.output))

    def predict(self, image_path):
        I = self.pre(img.read_image(image_path))
        I = np.expand_dims(I, 0)
        score = self.helper.model.predict(I)
        return score[0][0]


def main():


if __name__ == "__main__":
    main()
