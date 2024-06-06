from utils import JSON_ENCODER_DECODER


class Prompts:
    grade_subject = None
    grade_subject_meta = None

    def __init__(self, grade_subject):
        self.grade_subject_id = grade_subject
        self.grade_subject_meta = JSON_ENCODER_DECODER.data_load(
            f"prompts/prompts_{grade_subject}"
        )

    # __________________Extract exercises prompts________________________________
    def get_extract_exercises_prompt(self):
        return self.grade_subject_meta["extract_exercises"]

    def get_constructed_response_exercises_prompt(self):
        return self.grade_subject_meta["constructed_response_exercises"]

    def prompt_link_image_to_questions(self, question, images_links):

        prompt = self.grade_subject_meta.get("link_image_to_questions")

        # Add a value to the middle
        modified_prompt = prompt.replace("{question}", str(question))
        modified_prompt = modified_prompt.replace(
            "{images_links}", str({" ,".join(images_links)})
        )

        return modified_prompt

    def solve_questions_prompt(self, questions, chapter_content):

        prompt = self.grade_subject_meta["solve_exercises_questions"]

        # Add a value to the middle
        modified_prompt = prompt.replace("{questions}", str(questions))
        modified_prompt = modified_prompt.replace(
            "{chapter_content}", str(" ,".join(chapter_content))
        )

        return modified_prompt

    def marking_scheme(self, question_type, question_array, question_source):
        """ marking_scheme method used for both: generate and extract_exercise question process
        but question response format is different in both cases"""
        output_format = None
        if question_source == "generate":
            output_format = f"""Response Format:
                ```
                {{'questions': [list of question as {{
                "question_statement": "question here",
                "question_tag": one of remember, understand, apply, analyze, evaluate, and create,
                "question_type": one of multiple-choice, fill-the-blanks, short-answer, long-answer and constructed-response.,
                "correct_answer": "correct answer"
                "marking_scheme": "your marking scheme analysis"
                "score": "your marking scheme score"
                "keywords_bank": "your keywords bank"
                }}]}}"""
        elif question_source == "exercise":
            output_format = f"""Response Format:
            ```
            {{'questions': [list of question as {{
            "question_statement": "question here",
            "question_tag": one of remember, understand, apply, analyze, evaluate, and create,
            "image_based_question": "false/true",
            "question_image_url": "",
            "question_type": one of multiple-choice, fill-the-blanks, short-answer, long-answer and constructed-response.,
            "question_page_number": "00",
            "correct_answer": "correct answer"
            "marking_scheme": "your marking scheme analysis"
            "score": "your marking scheme score"
            "keywords_bank": "your keywords bank"
            }}]}}"""

        prompt = None
        if question_type == 'long_answer':
            prompt = self.grade_subject_meta["laq_marking_scheme"]

        elif question_type == 'short_answer':
            prompt = self.grade_subject_meta["saq_marking_scheme"]

        # Add a value to the middle
        modified_prompt = prompt.replace("{response_format}", output_format)
        modified_prompt = modified_prompt.replace("{question_array}", str(question_array))

        return modified_prompt

    def constructed_marking_scheme(self, question_array: list):
        prompt = self.grade_subject_meta["constructed_marking_scheme"]
        modified_prompt = prompt.replace("{question_array}", str(question_array))

        return modified_prompt

    # __________________Generate Questions prompts________________________________

    def get_question_type_and_cognitive_level(self, slo_cognitive_level: str):
        question_types_and_level: list = self.grade_subject_meta[
            "question_type_and_cognitive_level"
        ][slo_cognitive_level]

        return question_types_and_level

    def get_number_of_questions(self, slo_cognitive_level: str):

        return self.grade_subject_meta["number_of_questions"][slo_cognitive_level]

    def get_question_type_prompt(self, question_type, no_of_questions, cognitive_levels, content):
        prompt = self.grade_subject_meta[question_type]
        modified_prompt = prompt.replace("{no_of_questions}", no_of_questions)
        modified_prompt = modified_prompt.replace("{cognitive_levels}", str(cognitive_levels))
        modified_prompt = modified_prompt.replace("{content}", str(content))

        return modified_prompt

    def identify_slo_cognitive_level(self, slo: str):
        """function uses AI to identify slo cognitive level"""
        prompt = f"""
        use Bloom's Taxonomy to identify this slo: {slo} cognitive level from the following list of cognitive levels 
        remember, understand, apply, analyze, evaluate, and create. only return the slo cognitive level without extra lines"}}.
        """
        return prompt
