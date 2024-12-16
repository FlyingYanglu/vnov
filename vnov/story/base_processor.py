import os
import json
import time
from vnov.utils import extract_json_from_string

class BaseProcessor:
    def __init__(self, model, **kwargs):
        self.model = model
        self.role = kwargs.get("role", "processor")

    def handle_rate_limit(self, e):
        """Handle rate limit exceptions with retries."""
        if "Rate limit exceeded" in str(e):
            print("Rate limit exceeded, waiting for 10 minutes...")
            time.sleep(600)

    def save_file(self, content, filename):
        """Save text content to a file."""
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        print(f"Saving to {filename}")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    def save_json(self, data, filename):
        """Save JSON data to a file."""
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def parse_response(self, response):
        """Parse response and extract JSON and text content."""
        split_response = response.split("}")
        json_data = extract_json_from_string(response)
        response = split_response[-1].strip().replace("```", "")
        print(json_data)
        return response, json_data

    def create_prompt(self, template, **kwargs):
        """
        Create a prompt based on a template and provided context.
        
        Args:
            template (str): The template string with placeholders for formatting.
            **kwargs: Named arguments to fill in the template placeholders.
            
        Returns:
            str: The formatted prompt.
        """
        return template.format(**kwargs)
    def calculate_cur_max_length(self, model, *args):
        """
        Calculate the current maximum length for the content based on model constraints and input factors.
        
        Args:
            model: An object with a max_length attribute.
            *args: Positional arguments representing various lengths or factors 
                (e.g., instruction_length, last_context_length).
        
        Returns:
            int: The calculated maximum length.
        """
        total_length = 0
        for arg in args:
            total_length += model.token_length(arg)
        return model.max_length - total_length