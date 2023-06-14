# original script source https://codelabs.developers.google.com/codelabs/cloud-vision-api-python#3
# Image encoding provided by https://www.c-sharpcorner.com/article/converting-image-to-base64-in-python/
#
#
############################
#                          #
#       Modified by:       #
#       Cavan McLellan     #
#       Ramis Qureshi      #
#                          #
############################

import os
from google.cloud import vision
from PIL import Image
import base64


class PeopleCounter:
    def __init__(self):
        self.__feature_types = [vision.Feature.Type.OBJECT_LOCALIZATION]
        self.response = None
        credentials = 'angelic-surfer-388420-7ae25884642f.json'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

    def set_image(self, new_uri):
        self.__image = new_uri

    def get_image(self):
        return self.__image

    def count_people(self, image_path):  # Taken from analyze_image_from_uri() function from Google Codelabs (link in header).
        client = vision.ImageAnnotatorClient()
        image = vision.Image()
        with open(image_path, 'rb') as encoded_image:
            image_content = encoded_image.read()
            image.content = image_content
            features = [vision.Feature(type_=feature_type) for feature_type in self.__feature_types]
            request = vision.AnnotateImageRequest(image=image, features=features)
            response = client.annotate_image(request=request)
            self.response = response
            count = 0
            for detected_object in response.localized_object_annotations:
                if detected_object.name == "Person" and detected_object.score > 0.75:
                    count += 1
            return count



if __name__ == "__main__":
    counter = PeopleCounter()
    waiting = counter.count_people("sample.jpg")
    print("there are", waiting, "people waiting")

