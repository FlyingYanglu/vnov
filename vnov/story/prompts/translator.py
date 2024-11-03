# Translator

TRANSLATOR_ROLE = """\
You are a professional **"Scene Information in Chinese" to "English Danbooru Tag"** translator. You are professional at converting scene information \
in chinese to Danbooru Tag without losing information. 
You can use the following sample output to assist you(your output should be in the same format):
{example}
"""

EXAMPLE_RESULT = """\
```json
{
    "场景": [
        "desolate_mountain",
        "overcast",
        "strong_wind",
        "overgrown_grass"
    ],
    "动作": [
        "wandering"
    ],
    "表情": [
        "confused_expression",
        "painful_expression"
    ],
    "服装": [
        "tattered_jacket",
        "wrinkled_shirt",
        "worn_pants"
    ]
}
```
"""

TRANSLATOR_PROMPT = """\
# Input:
{input}

# Instruction:
Please convert these four fields of input: "场景，动作，表情，服装" to English dambooru tag. \
If one chinese item description contains too much information for 1 tag, feel free to split them into multiple dambooru tags instead of one.
Output format should be in json. Please follow the same format as the example and ensure each key has its own values. 

"""
