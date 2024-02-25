"""

"""
import os
from ai_models_services import GPT4_CLIENT, AWS_TEXTRACT_CLIENT
from llm_response_validattion import GPT4_RESPONSE_VALIDATION
from prompts import Prompts
from utils import JSON_ENCODER_DECODER, OPEN_CV2, get_object_key


class Book:
    def __init__(self, file_name):
        book = JSON_ENCODER_DECODER.data_load(fname=file_name)[0]
        self.book_details = {
            "id": book["id"],
            "title": book["title"],
            "grade_subject_id": book["grade_subject_id"],
            "book_text": book["book_text"],
        }

    def add_chapter(self):
        book_chapters = JSON_ENCODER_DECODER.data_load(
            fname="input_data/book_chapters.json"
        )
        PROMPTS = Prompts(grade_subject=self.book_details["grade_subject_id"])

        for index, book_chapter in enumerate(book_chapters):
            if index != 3:
                pass
            else:
                print("book_chapter", book_chapter["title"])
                chapter = BookChapter(
                    book_details=self.book_details,
                    book_chapter=book_chapter,
                    prompts=PROMPTS,
                )
                chapter.execute_extraction_process()



class BookChapter:

    """
    Class BookExercises is intended to extract book exercises by the following process:
    1. Retrieve book and book chapter details from the core backend.
    2. Utilize OCR labeled with book chapters to obtain exercise question pages.
    3. Perform OCR on pages using GPT Vision to extract the questions in the intended format with detailed image descriptions if they exist.
    4. For image-based questions, extract the images from the page using AWS Layout OCR.
    5. Validate the images by their height and width.
    6. Upload validated images to AWS.
    7. Link the images to questions by matching the image to its description.
    8. Associate exercise questions with Student Learning Outcomes (SLOs).
    9. Solve these questions using GPT-4 and SLO content.
    10. Assign a marking scheme to the exercise using GPT-4.
    11. Validate question structure format and push the questions to the core database.
    """

    def __init__(self, book_details, book_chapter, prompts):
        self.book_details = book_details
        self.chapter_details = book_chapter
        self.PROMPTS = prompts
        self.chapter_exercises = None
        self.exercises_pages_urls = None
        self.extracted_exercises = []
        self.page_wise_figures = {}

    def execute_extraction_process(self):
        # check if book exercise exist or not
        chapter_text = self.chapter_details["chapter_text"]
        self.chapter_exercises = chapter_text.get("exercises", None)

        if self.chapter_exercises is not None:
            # self.obtain_exercise_question_pages()
            # self.extract_questions_with_image_descriptions()
            # self.extract_figures_from_pages()
            self.link_images_to_questions()
            print("Done")

            # self.associate_questions_with_slos()
            # self.solve_questions()
            # self.assign_marking_scheme()
            # self.validate_question_structure_and_push_to_database()
        else:
            print("Book Chapter has no exercise questions Found")

    def obtain_exercise_question_pages(self):
        unique_pages = set()
        exercise_pages = []
        for exercise in self.chapter_exercises:
            unique_pages.add(exercise.get("page_number"))

        page_wise_pdf_url: dict[str, str] = {}

        for item in self.book_details["book_text"]:
            if "book_page_no" in item and "pdf_page_image_url" in item:
                page_wise_pdf_url[item["book_page_no"]] = item["pdf_page_image_url"]
        for page in list(unique_pages):
            exercise_pages.append(
                {"book_page_no": page, "page_url": page_wise_pdf_url[page]}
            )

        self.exercises_pages_urls = exercise_pages
        JSON_ENCODER_DECODER.data_write(
            fname=f"output_progress/exercise_pages",
            data=exercise_pages,
        )

    def extract_questions_with_image_descriptions(self):
        # Perform OCR on pages using GPT Vision to extract questions
        # Extract detailed image descriptions if they exist
        prompt_text = self.PROMPTS.get_extract_exercises_prompt()
        constructed_response_prompt = (
            self.PROMPTS.get_constructed_response_exercises_prompt()
        )
        chapter_questions = []

        urls = [
            question_page["page_url"].replace(" ", "+")
            for question_page in self.exercises_pages_urls
        ]

        response = GPT4_CLIENT.get_gpt_4_vision(
            prompt_text=prompt_text, images_links=urls
        )
        print("response", response)
        print("self.extracted_exercises", self.extracted_exercises)

        constructed_questions = GPT4_CLIENT.get_gpt_4_vision(
            prompt_text=constructed_response_prompt, images_links=urls
        )
        print("constructed_questions", constructed_questions)

        # validate responses
        self.extracted_exercises = self.extracted_exercises + GPT4_RESPONSE_VALIDATION.get_questions_array_from_response(
            response=response
        )
        self.extracted_exercises = self.extracted_exercises + GPT4_RESPONSE_VALIDATION.get_questions_array_from_response(
            response=constructed_questions
        )

        print("self.extracted_exercises", self.extracted_exercises)

        JSON_ENCODER_DECODER.data_write(
            fname=f"output_progress/{self.book_details['title']}_{self.chapter_details['title']}",
            data=self.extracted_exercises,
        )

    def extract_figures_from_pages(self):
        """ For image-based questions,
        1. extract images layout from the page using AWS Layout OCR
        2. crop images using openCV2,
        3. upload sub-images to AWS
        """
        # get questions pages
        questions = self.extracted_exercises
        # questions = JSON_ENCODER_DECODER.data_load(fname="output_progress/General Science 5 Hyper-specific_Flowers and Seeds.json")
        page_figures = {}
        pages_no = set()
        for question in questions:
            if question["image_based_question"]:
                pages_no.add(int(question["question_page_number"]))

        # process image by image
        for page_number in pages_no:
            page_url = None
            page_file_name = None
            coordinates_list = []
            figures_links = []
            for exercise in self.exercises_pages_urls:
                if page_number == exercise["book_page_no"]:
                    page_url = exercise["page_url"]
                    page_file_name = get_object_key(url=page_url)
                    coordinates_list = AWS_TEXTRACT_CLIENT.get_figures_coordinates(s3_object_key=page_file_name)
                    break

            if coordinates_list:
                print("number of figures found", len(coordinates_list), f"at page {page_number}")
                # Loop through the coordinates and crop the image
                for index, coordinates in enumerate(coordinates_list, start=1):
                    cropped_image = OPEN_CV2.crop_image(image_url=page_url.replace(' ', '+'), coordinates=coordinates)

                    # upload image to aws
                    format_name = os.path.splitext(page_file_name)[0]
                    image_name = f"{format_name.replace(' ', '_')}.{index}"
                    print("cropped image name", image_name)
                    link = AWS_TEXTRACT_CLIENT.upload_image_to_aws(image=cropped_image, image_key=image_name)
                    print("link", link)
                    figures_links.append(link)

                page_figures[page_number] = figures_links
            else:
                print(f"no figures found at page {page_number}")

            self.page_wise_figures = page_figures
            JSON_ENCODER_DECODER.data_write(
                fname=f"output_progress/figures_links_{page_number}",
                data=page_figures,
            )

    def link_images_to_questions(self):
        # Link the images to questions by matching the image to its description
        questions = JSON_ENCODER_DECODER.data_load(fname="output_progress/General Science 5 Hyper-specific_Classification of Living Organisms.json")
        page_wise_figures = JSON_ENCODER_DECODER.data_load(fname="output_progress/figures_links_18.json")
        # questions = self.extracted_exercises
        # print("len", len(questions))
        # page_wise_figures = self.page_wise_figures
        # print("LEN page_wise_figures", len(page_wise_figures))
        # print(" page_wise_figures", page_wise_figures)

        for question in questions:

            if question['image_based_question']:
                print("question['image_based_question']", question['image_based_question'])
                question_page_number = question['question_page_number']
                page_figures = page_wise_figures.get(str(question_page_number), None)
                if page_figures:
                    print("page_figures", page_figures)
                    images_urls = page_figures
                    prompt = self.PROMPTS.prompt_link_image_to_questions(question=question, images_links=images_urls)
                    question_images_urls = GPT4_CLIENT.get_gpt_4_vision(prompt_text=prompt, images_links=images_urls)

                    print(question_images_urls)
                    urls_list = GPT4_RESPONSE_VALIDATION.get_images_urls(response=question_images_urls)
                    print("urls_list", urls_list)
                    if urls_list:
                        question["question_image_url"] = urls_list
                    else:
                        question["question_image_url"] = question_images_urls

        self.extracted_exercises = questions
        JSON_ENCODER_DECODER.data_write(
            fname=f"output_progress/Linked_{self.book_details['title']}_{self.chapter_details['title']}",
            data=self.extracted_exercises,
        )

    def associate_questions_with_slos(self):
        # Associate exercise questions with Student Learning Outcomes (SLOs)
        pass

    def solve_questions(self):
        # Solve questions using GPT-4 and SLO content
        pass

    def assign_marking_scheme(self):
        # Assign a marking scheme to the exercise using GPT-4
        pass

    def validate_question_structure_and_push_to_database(self):
        # Validate question structure format and push questions to the core database
        pass


book = Book(file_name="input_data/book.json")
book.add_chapter()
