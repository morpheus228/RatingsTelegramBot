import numpy as np
from PIL import Image
import os
import glob
import argparse

import tensorflow as tf
from tensorflow.keras.applications.resnet_v2 import preprocess_input


class PhotoSelector:
    def __init__(self, model_path='photo_selector/model.hdf5'):
        self.model = tf.keras.models.load_model(model_path)

    def resize(self, photo):
        return tf.image.resize(photo, self.model.input_shape[1:3], tf.image.ResizeMethod.BILINEAR)

    def select(self, photos_list):
        photos_list = [np.asarray(photo)[None, ...] for photo in photos_list]
        resized_photos_list = [self.resize(photo) for photo in photos_list]
        photos_array = np.concatenate(resized_photos_list, axis=0)
        preprocessed_photos_array = preprocess_input(photos_array)
        predictions = self.model.predict(preprocessed_photos_array)

        return predictions

    def delete_bad_photos(directory):
        photo_url_main_list = glob.glob(directory + '/**/*.jpeg', recursive=True) + glob.glob(directory + '/**/*.jpg', recursive=True)
        photo_url_lists = list(split(photo_url_main_list, 80))
        for i in range(len(photo_url_lists)):
            print((i/len(photo_url_lists))*100, '% ВЫПОЛНЕНО')
            X = []
            photo_url_list = photo_url_lists[i]
            for photo_url in photo_url_list:
                image = Image.open(photo_url)
                image = tf.image.resize(image, model.input_shape[1:3], tf.image.ResizeMethod.BILINEAR)
                preprocessed_img = preprocess_input(image)
                X.append(preprocessed_img)

            X_t = np.array(X)
            predictions = model.predict(X_t)
            predictions_by_url = {photo_url_list[i]: predictions[i][0] for i in range(len(photo_url_list))}

            for photo_url in predictions_by_url.keys():
                if predictions_by_url[photo_url] < 0.3:
                    print(photo_url)
                    os.remove(photo_url)
