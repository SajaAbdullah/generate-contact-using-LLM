"""

"""
import json

from ai_models_services import GPT4_CLIENT
from prompts import Prompts
from utils import JSON_ENCODER_DECODER


class Book:
    def __init__(self, file_path):
        book = JSON_ENCODER_DECODER.data_load(fname=file_path)[0]
        self.book_details = {
            "id": book["id"],
            "title": book["title"],
            "grade_subject_id": book["grade_subject_id"],
        }

    def add_chapter(self):
        book_chapters = JSON_ENCODER_DECODER.data_load(
            fname="input_data/book_library_bookchapter.json"
        )
        all_lp_inputs = JSON_ENCODER_DECODER.data_load(
            fname="input_data/book_ocr_lp_input.json"
        )
        grade_subject_prompts = Prompts(
            grade_subject=self.book_details["grade_subject_id"]
        )

        for index, book_chapter in enumerate(book_chapters):
            # the if else for testing purpose that control number of chapter to process
            if (
                index != 1
            ):
                pass
            else:
                print("book_chapter", book_chapter["id"], book_chapter["title"])
                # get chapter lp inputs
                chapter_lp_inputs = [
                    lp_input
                    for lp_input in all_lp_inputs
                    if lp_input["book_chapter_id"] == book_chapter["id"]
                ]
                print("Number of chapter_lp_inputs", len(chapter_lp_inputs))
                chapter = BookChapter(
                    book_details=self.book_details,
                    book_chapter=book_chapter,
                    lp_inputs=chapter_lp_inputs,
                    prompts=grade_subject_prompts,
                )
                chapter.execute_generation_process()


class BookChapter:

    """
    remind me to fill it
    """

    def __init__(self, book_details, book_chapter, lp_inputs, prompts):
        self.book_details = book_details
        self.chapter_details = book_chapter
        self.PROMPTS = prompts
        self.lp_inputs = lp_inputs
        self.chapter_questions = None

    def execute_generation_process(self):
        # check if book exercise exist or not
        chapter_text = self.chapter_details["chapter_text"]
        if chapter_text:
            self.generate_questions()
        else:
            print(
                f"Chapter id {self.chapter_details['id']} does not contain chapter text"
            )

    def generate_questions(self):
        # save generated question in local file
        output_file_name = f"output_progress/{self.book_details['id']}_{self.chapter_details['id']}"
        JSON_ENCODER_DECODER.data_write(fname=output_file_name, data=[])

        for lp_input in self.lp_inputs:
            lp_input_questions = []
            slo_statement = lp_input["slo_statement"]
            lp_input_content = lp_input["related_chapter_content"]
            lp_input_content["slo_statement"] = slo_statement
            print("slo_statement", slo_statement)
            # identify slo cognitive level
            cognitive_level_prompt = self.PROMPTS.identify_slo_cognitive_level(
                slo=slo_statement
            )

            slo_cognitive_level = GPT4_CLIENT.get_gpt_4_1106_preview(
                prompt=cognitive_level_prompt,
                json_format=False
            )

            if not slo_cognitive_level:
                raise Exception("slo_cognitive_level couldn't be found")

            # get question types and each type level.
            question_types_and_cognitive_levels: list[
                dict
            ] = self.PROMPTS.get_question_type_and_cognitive_level(
                slo_cognitive_level=slo_cognitive_level.lower()
            )
            # according slo we select number of questions to generate
            number_of_questions = self.PROMPTS.get_number_of_questions(slo_cognitive_level=slo_cognitive_level.lower())

            # loop trough each questions type and generate the questions
            for question_type_and_levels in question_types_and_cognitive_levels:

                question_type, cognitive_levels = next(
                    iter(question_type_and_levels.items())
                )
                # print("question_type:", question_type)
                # print("cognitive_levels:", cognitive_levels)

                question_prompt = self.PROMPTS.get_question_type_prompt(
                    question_type=question_type,
                    no_of_questions=number_of_questions[question_type],
                    cognitive_levels=cognitive_levels,
                    content=lp_input_content
                )
                # print(question_prompt)
                # breakpoint()
                json_response = GPT4_CLIENT.get_gpt_4_1106_preview(prompt=question_prompt)
                json_response = json.loads(json_response)
                questions_array = json_response.get("questions", [])
                print(f"{question_type} questions", questions_array)

                """<><><><><><><><><><><><><><><><>Marking scheme<><><><><><><><><><><><><><><><>"""
                # assign marking-scheme to SAQ and LAQ questions.
                if question_type in ('short_answer', "long_answer"):
                    marking_scheme_prompt = self.PROMPTS.marking_scheme(
                        question_type=question_type, question_array=questions_array, question_source='generate'
                    )
                    json_response = GPT4_CLIENT.get_gpt_4_1106_preview(prompt=marking_scheme_prompt)
                    json_response = json.loads(json_response)
                    questions_array = json_response.get("questions", [])
                    for ques in questions_array:
                        ques["type"] = question_type
                        ques["source"] = "book_text_unseen"
                        ques["lp_input_id"] = lp_input["id"]
                else:
                    # add meta data to the questions
                    for ques in questions_array:
                        ques["type"] = question_type
                        ques["source"] = "book_text_unseen"
                        ques["score"] = 1
                        ques["lp_input_id"] = lp_input["id"]

                lp_input_questions.append(questions_array)

            # save after each LP_INPUT completion
            final_question = {
                "lp_input_id": lp_input['id'],
                "generated_questions": lp_input_questions,
            }
            chapter_questions = JSON_ENCODER_DECODER.data_load(fname=output_file_name)
            chapter_questions.append(final_question)
            JSON_ENCODER_DECODER.data_write(fname=output_file_name, data=chapter_questions)


book = Book(file_path="input_data/book.json")
book.add_chapter()
