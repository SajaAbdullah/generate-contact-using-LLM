""" functions handle local file reading and writing"""
import base64
from io import BytesIO
import re
import urllib
from json import JSONEncoder, dump, load
import tempfile

import cv2
import numpy
import requests
from PIL import Image


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


class ImageServices:


    @classmethod
    def encode_image_to_base64(cls, image_path):
        with open(image_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        return base64_image

    @classmethod
    def fix_image_colors_pil(cls, image):
        # Convert OpenCV image to PIL image
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        return pil_image

    @classmethod
    def crop_image_opencv(cls, image_path, coordinates):
        # Load the image from local file using OpenCV
        image = cv2.imread(image_path)
        # Extract crop coordinates
        left, top, width, height = coordinates
        h, w, _ = image.shape
        left_pixel = int(left * w)
        top_pixel = int(top * h)
        width_pixel = int(width * w)
        height_pixel = int(height * h)

        # Crop the image
        cropped_image = image[top_pixel:top_pixel + height_pixel, left_pixel:left_pixel + width_pixel]
        fixed_image_pil = cls.fix_image_colors_pil(cropped_image)
        fixed_image_pil.show()
        return fixed_image_pil

    @classmethod
    def download_image(cls, url, temp_dir):
        response = requests.get(url)
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".jpeg")
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name


IMAGE_SERVICE = ImageServices()


def get_object_key(url):

    # Define a regular expression pattern to match the S3 object key after "book_images/"
    pattern = r"book_images/.*"

    # Search for the pattern in the URL
    match = re.search(pattern, url)

    if match:
        return match.group(0)
    else:
        print("S3 object key not found in the URL.")
