import json
import re


def extract_json_from_string(input_string, raise_exception=False):
    # Regular expression to find JSON objects or arrays
    json_pattern = re.compile(r'(\{.*\}|\[.*\])', re.DOTALL)
    
    # Search for JSON in the input string
    match = json_pattern.search(input_string)
    
    if match:
        # Extract the JSON part from the matched pattern
        json_str = match.group(0)
        
        try:
            # Parse the JSON string
            parsed_json = json.loads(json_str)
            return parsed_json
        except json.JSONDecodeError as e:
            print("Error: Found JSON but could not parse it.", e)
            # print(json_str)
            if raise_exception:
                raise e
    else:
        print("No JSON found in the input string.")
        if raise_exception:
            raise ValueError("No JSON found in the input string.")
        return []

