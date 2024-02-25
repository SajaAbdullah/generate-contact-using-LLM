
import json


class GPT4ResponseValidation:
    @classmethod
    def get_questions_array_from_response(self, response):
        """from vision response try to find json array, if does not exist ask gpt 4
        with json format mode to reformat and return array of json objects"""

        json_found = False
        json_response = []
        # Find the starting index of [
        start_index = response.find("[")
        if start_index != -1:
            # Find the ending index of ]
            end_index = response.rfind("]")
            if end_index != -1:
                # Extract content between [ and ]
                content_between_brackets = response[start_index: end_index + 1]
                try:
                    json_response = list(json.loads(content_between_brackets))
                    json_found = True
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
            else:
                print("No matching ] found.")
        else:
            print("No matching [ found.")

        if not json_found:
            from ai_models_services import GPT4_CLIENT

            print("No json_found.")

            json_response = GPT4_CLIENT.get_gpt_4_1106_preview(
                prompt=f"for given text format in proper JSON response Example: {{'questions': [list of question]}}. TEXT: {response}"
            )
            json_response = json.loads(json_response)
            json_response = json_response.get("questions", [])

        return json_response

    @classmethod
    def get_images_urls(self, response):
        """from vision response try to find json array, """

        json_response = []
        # Find the starting index of [
        start_index = response.find("[")
        if start_index != -1:
            # Find the ending index of ]
            end_index = response.rfind("]")
            if end_index != -1:
                # Extract content between [ and ]
                content_between_brackets = response[start_index: end_index + 1]
                try:
                    json_response = json.loads(content_between_brackets)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
            else:
                print("No matching ] found.")
        else:
            print("No matching [ found.")

        return json_response


GPT4_RESPONSE_VALIDATION = GPT4ResponseValidation

class AWSResponseValidation:

    @classmethod
    def validate_images(cls, height, width):
        """
            Validates a figure based on its height and width.

            Parameters:
                height (float): The height of the figure.
                width (float): The width of the figure.
            Returns:
                bool: True if the figure is valid, False otherwise.
            """

        min_height = 0.1
        min_width = 0.1
        if height < min_height or width < min_width:
            return False
        else:
            return True

    @classmethod
    def get_valid_figures_layout(cls, response):
        blocks = response.get('Blocks', [])

        extracted_items = []
        validated_figures = []
        for block in blocks:
            if block.get('BlockType') == 'LAYOUT_FIGURE':
                geometry = block.get('Geometry')
                width = geometry['BoundingBox']['Width']
                height = geometry['BoundingBox']['Height']
                left = geometry['BoundingBox']['Left']
                top = geometry['BoundingBox']['Top']
                converted_format = (left, top, width, height)

                if cls.validate_images(height, width):
                    validated_figures.append(converted_format)

                extracted_items.append(converted_format)

        print("len extracted_items", len(extracted_items))
        print("len validated_figures", len(validated_figures))
        return validated_figures


AWS_RESPONSE_VALIDATION = AWSResponseValidation
