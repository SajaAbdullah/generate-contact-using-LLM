import os
from tempfile import TemporaryDirectory

import boto3
import openai
from dotenv import find_dotenv, load_dotenv

from llm_response_validattion import AWS_RESPONSE_VALIDATION

_ = load_dotenv(find_dotenv())


class GPT4Client:
    OPENAI_API_KEY = os.getenv("OPENAI_APIKEY")
    if not OPENAI_API_KEY:
        print("No API Key provided")
    # Initialize the OpenAI client
    CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)

    @classmethod
    def call_gpt(
        cls, messages: list[dict[str, str]], model: str, json_format: bool = False
    ):

        messages = [{"role": "user", "content": messages}]

        try:
            if json_format:
                response = cls.CLIENT.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=4096,
                    response_format={"type": "json_object"}
                )
            else:
                response = cls.CLIENT.chat.completions.create(
                    model=model, messages=messages, max_tokens=4096
                )

        except Exception as e:
            raise Exception(f"OpenAI request failed, Error: {e}")

        return response.choices[0].message.content

    @classmethod
    def get_gpt_4_1106_preview(cls, prompt: str):
        if not prompt:
            raise ValueError("Prompt is empty")

        gpt_model = "gpt-4-1106-preview"
        message = [{"type": "text", "text": prompt}]
        print("message", message)
        return cls.call_gpt(messages=message, model=gpt_model, json_format=True)

    @classmethod
    def get_gpt_4_vision(cls, prompt_text: str, images_links: list):

        if not prompt_text:
            raise ValueError("Prompt is empty")

        if not images_links:
            raise ValueError("No image URL is empty")

        message = [{"type": "text", "text": prompt_text}]
        for image in images_links:
            message.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"{image}",
                    },
                }
            )
        print("message", message)
        return cls.call_gpt(model="gpt-4-vision-preview", messages=message)


GPT4_CLIENT = GPT4Client


class AWSClient:
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    BOOKMAPPING_IMAGES_BUCKET = os.getenv("BOOKMAPPING_IMAGES_BUCKET")
    AWS_REGION = os.getenv("AWS_REGION")
    if not AWS_ACCESS_KEY or not AWS_SECRET_ACCESS_KEY:
        print("No AWS API Key provided")

    TEXTRACT_CLIENT = boto3.client(
        'textract',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    S3_CLIENT = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    @classmethod
    def get_figures_coordinates(cls, s3_object_key):
        print("s3_object_key", s3_object_key)

        response = cls.TEXTRACT_CLIENT.analyze_document(
            Document={
                'S3Object': {
                    'Bucket': cls.BOOKMAPPING_IMAGES_BUCKET,
                    'Name': s3_object_key
                }
            },
            FeatureTypes=[
                'LAYOUT',
            ]
        )

        # print("Textract job response", response)
        return AWS_RESPONSE_VALIDATION.get_valid_figures_layout(response)


    @classmethod
    def upload_image_to_aws(cls, image, image_key):
        """Uploads a local image file to aws bucket."""
        # upload the images to S3
        with TemporaryDirectory() as tempdir:
            image_path = f"{tempdir}.jpeg"
            image.save(image_path, "JPEG")
            cls.S3_CLIENT.upload_file(
                image_path,
                cls.BOOKMAPPING_IMAGES_BUCKET,
                image_key,

            )
        image_url = f"https://{cls.BOOKMAPPING_IMAGES_BUCKET}.s3.{cls.AWS_REGION}.amazonaws.com/{image_key}"

        return image_url

AWS_TEXTRACT_CLIENT = AWSClient