from utils import JSON_ENCODER_DECODER

Grade_five_question_types = [
    "fill in the blanks",
    "multiple choices",
    "true / false",
    "short answer question",
    "long answer questions" "constructed response questions",
]


class Prompts:
    grade_subject = None
    grade_subject_meta = None

    def __init__(self, grade_subject):
        self.grade_subject_id = grade_subject
        self.grade_subject_meta = JSON_ENCODER_DECODER.data_load(
            f"prompts/prompts_{grade_subject}"
        )

    def get_extract_exercises_prompt(self):
        return f"""
            Examine the provided educational book and identify all fill in the blanks, multiple choices, true / false, short answer question and long answer question.
            For each identified question, note whether it includes or refers to an image. If it does, describe the image in detail as part of the question.
            Skip constructed response, project-based and investigate questions. Must return question page number with each question.
            Format the output as list of JSON objects, following the given structure:
            JSON Response format:
            ```
            [
            {{
                 "question_statement": "Question statement here",
                 "image_based_question": true / false,
                 "question_image": "Detailed description if image_based_question is True",
                 "question_type": "Question type here",
                 "question_page_number": "question_page_number",
                 "answer_options": [Option 1, Option 2, etc.],
            }},
            ...
            ]
            Ensure all questions, are included in single JSON list.
            """

    def get_constructed_response_exercises_prompt(self):
        return f"""
            Examine the provided educational mages and identify all constructed response and constructive response questions ONLY. For each identified question, note whether it includes or refers to an image. If it does, describe the image in detail as part of the question. 
            Must include the question_page_number where the image exist for each question. Note Question either has sub part or not. attached example.  
            Format your response as a JSON list with the following structure of EXAMPLES next: 
            EXAMPLES:
            ```
            [
            {{
            "image_based_question": true,
            "question_statement": "Why do zebras have black and white stripes?",
            "question_image": "An illustration of a zebra with black and white stripes standing in profile.",
            "question_type": "constructed response",
            "question_page_number": 30,
            "sub_questions": []
            }},
            {{ 
            "question_statement": "Why are some bacteria and fungi called decomposers?",
            "image_based_question": false,
            "question_type": "Short Answer",
            "question_page_number": 30,
            "sub_questions": []
            }},
            {{
            "image_based_question": false,
            "question_statement": "Imagine you are writing on your notebook with a pencil. Answer the following questions based on your observation:",
            "question_type": "constructed response",
            "question_page_number": "125",
            "sub_questions": [
            {{
            "question_statement": "What force do you use (push or pull) while writing?",
            "image_based_question": false,
            "question_page_number": "125"
            }},
            {{
            "question_statement": "What is the role of friction in writing on the paper with a pencil?",
            "image_based_question": false,
            "question_page_number": "125"
            }},
            }},
            ]
            Ensure all questions, are included in single JSON list.
            """

    def prompt_link_image_to_questions(self, question, images_links):

        return f"""
        For the given images and question. use question_image to pick the most relevant image from provided link and only return its url in the follwoing format
        '''
        QUESTIONS 
        {question}
        '''
        IMAGES: {" ,".join(images_links)}
        Response Format:
        [
        images_url,
        images_url,
        ....
        ]
        NOTE: Strictly return response in JSON format and do not generate images by your self. return links of the given images as it is
        """