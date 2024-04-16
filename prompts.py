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
            Examine the provided educational book and identify multiple choices, write short answers question and long answer question. For each identified question, note whether it includes or refers to an image. If it does, describe the image in detail as part of the question.
            DON NOT skip any question of requested types. ONLY Skip constructed response, project-based and investigate questions. Must return question page number with each question.
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
            Examine the provided educational images and ONLY identify all constructed  and constructive response questions. skip multiple choices, short answer question, project and invitigate questions. For each identified question, note whether it includes or refers to an image. If it does, describe the image in detail as part of the question. 
            Carefully select constructed and constructive response questions images. Must include the question_page_number where the image exist for each question. Note Question either has sub part or not. attached example.  
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

    def solve_questions_prompt(self, questions, chapter_content):

        return f"""
        As an Educational teacher, you will receive book content text and questions within triple quotes. Your task involves these steps: 1. Read and understand the Student Learning Outcome (SLO) and the related topic_content. 
        2. Using the topic content provided, formulate answers for each question. 3. Determine the cognitive level of each question. The cognitive levels are from Bloom's Taxonomy: remember, understand, apply, analyze, evaluate, and create.
        4. map question type to the following types multiple-choice, fill-the-blanks, short-answer, long-answer and constructed-response. 5. return the questions in JSON format as a list of objects. As follow
        Response Format:
        ```
        {{'questions': [list of question as {{
        "question_statement": "question here",
        "question_tag": one of remember, understand, apply, analyze, evaluate, and create,
        "image_based_question": "false/true",
        "question_image_url": "",
        "question_type": one of multiple-choice, fill-the-blanks, short-answer, long-answer and constructed-response.,
        "question_page_number": "00",
        "sub_questions": [],
        "answer_options": [
            "option 1",
            "option 2",
            "option 3",
            "option 4",
        ]
        "correct_answer": "correct answer"
        }}]}}
        ```
        Questions:
        ```
        {questions}
        ```
        SLO_TOPICS:
        ```
        {chapter_content}
        ```
        """

    def saq_marking_scheme(self, saq_examples, question_array):
        return f"""
Consider yourself a science teacher for Grade five students in Pakistan. Your task is to create marking scheme of either 2 or 3 marks.for each question given below in triple quotes. 
Also create keywords bank of answer that can help teacher in marking. Do NOT bound your self to the answer given. create list of keywords from question. I am sharing a sample of marking scheme.
Examples: 
'''{saq_examples}'''. 
Format the output as a list of JSON objects as question given, following the given structure:
Response Format:
```
{{'questions': [list of question as {{
"question_statement": "question here",
"question_tag": one of remember, understand, apply, analyze, evaluate, and create,
"image_based_question": "false/true",
"question_image_url": "",
"question_type": one of multiple-choice, fill-the-blanks, short-answer, long-answer and constructed-response.,
"question_page_number": "00",
"sub_questions": [],
"answer_options": [
    "option 1",
    "option 2",
    "option 3",
    "option 4",
]
"correct_answer": "correct answer"
"marking_scheme": "your marking scheme analysis"
"score": "your marking scheme score"
"keywords_bank": "your keywords bank"
}}]}}
```
Questions:
''' {question_array}'''. 
"""

    def laq_marking_scheme(self, laq_examples, question_array):
        return f"""
Consider yourself a science teacher for Grade five students in Pakistan. Your task is to create marking scheme of 5 marks. for each question given below in triple quotes. 
Also create keywords bank of answer that can help teacher in marking. Do NOT bound your self to the answer given. create list of keywords from question. I am sharing a sample of marking scheme.
Examples: 
'''{laq_examples}'''. 
Format the output as a list of JSON objects, following the given structure:
Response Format:
```
{{'questions': [list of question as {{
"question_statement": "question here",
"question_tag": "question_tag here",
"image_based_question": "false/true",
"question_image_url": "",
"question_type": "long-answer",
"question_page_number": "00",
"sub_questions": [],
"answer_options": [
    "option 1",
    "option 2",
    "option 3",
    "option 4",
]
"correct_answer": "correct answer"
"marking_scheme": "your marking scheme analysis"
"score": "your marking scheme score"
"keywords_bank": "your keywords bank"
}}]}}
```
Questions:
''' {question_array}'''. 
"""

    def constructed_marking_scheme(self, examples, question_array):
        return f"""
Consider yourself a science teacher for Grade five students in Pakistan. Your task is to create marking scheme of either 2 or 3 or 5 marks. or each question given below in triple quotes. 
Also create keywords bank of answer that can help teacher in marking. Do NOT bound your self to the answer given. create list of keywords from question. I am sharing a sample of marking scheme.
Examples: 
'''{examples}'''. 
Format the output as a list of JSON objects, following the given structure:
Response Format:
```
{{'questions': [list of question as {{
"question_statement": "question here",
"question_tag": "question_tag here",
"image_based_question": "false/true",
"question_image_url": "",
"question_type": "long-answer",
"question_page_number": "00",
"sub_questions": [],
"answer_options": [
    "option 1",
    "option 2",
    "option 3",
    "option 4",
]
"correct_answer": "correct answer"
"marking_scheme": "your marking scheme analysis"
"score": "your marking scheme score"
"keywords_bank": "your keywords bank"
}}]}}
```
Questions:
''' {question_array}'''. 
"""
