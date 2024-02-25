""" functions handle local file reading and writing"""
import re
import urllib
from json import JSONEncoder, dump, load

import cv2
import numpy
from PIL import Image

from ai_models_services import GPT4_CLIENT


class MyEncoder(JSONEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except TypeError:
            # Handle circular references by returning a representation of the object
            return str(o)


class JSONEncoderDecoder:
    @classmethod
    def json_load(cls, fname: str):
        with open(fname, "r") as f:
            return load(f)

    @classmethod
    def data_load(cls, fname: str):
        if not fname.endswith(".json"):
            fname = fname + ".json"

        return cls.json_load(fname)

    @classmethod
    def data_write(cls, fname: str, data: list | dict):
        if not fname.endswith(".json"):
            fname = fname + ".json"

        with open(fname, "w") as f:
            dump(data, f, indent=4, cls=MyEncoder)


class AiInputDataFormat:
    """class manages input data passed to AI by trying to minimize data in order to tale less input tokens"""

    @classmethod
    def exercise_questions_format_topics(slo):
        formatted_data = {
            "slo": slo["slo"],
            "topics": [
                {
                    "topic_name": topic["topic_name"],
                    "topic_content": topic["topic_content"],
                }
                for topic in slo["topics"]
            ],
            "exercise_questions": slo["exercise_questions"],
        }
        exer_ques = ""
        for exr in slo["exercise_questions"]:
            exer_ques = f"{exer_ques}, {exr['exercise_content']}"

        formatted_data["exercise_questions"] = exer_ques

        return formatted_data


JSON_ENCODER_DECODER = JSONEncoderDecoder


class OPENCV2:

    @classmethod
    def crop_image(cls, image_url, coordinates):
        # Load the image from URL
        print("crop_image")
        print("image_url", image_url)
        image = urllib.request.urlopen(image_url)
        image_array = numpy.asarray(bytearray(image.read()), dtype=numpy.uint8)
        image = cv2.imdecode(image_array, -1)

        # Extract crop coordinates
        left, top, width, height = coordinates
        h, w, _ = image.shape
        left_pixel = int(left * w)
        top_pixel = int(top * h)
        width_pixel = int(width * w)
        height_pixel = int(height * h)

        # Crop the image
        cropped_image = image[top_pixel:top_pixel + height_pixel, left_pixel:left_pixel + width_pixel]
        pil_image = Image.fromarray(cropped_image)

        return pil_image


OPEN_CV2 = OPENCV2()


def get_object_key(url):

    # Define a regular expression pattern to match the S3 object key after "book_images/"
    pattern = r"book_images/.*"

    # Search for the pattern in the URL
    match = re.search(pattern, url)

    if match:
        return match.group(0)
    else:
        print("S3 object key not found in the URL.")
