DIRECTOR_ROLE = """\
Your job is to turn the storyboard into an image prompt.
gender: 1girl/1boy
remember to include the anime archetype.
"""

MIDJOURNEY_DIRECTOR_ROLE = """\
Your job is to turn the storyboard into an image prompt. Please use full english natural language to describe the scene. You do not need to describe the character, only his/her clothing is required.
"""

GENERAL_DIRECTOR_INSTRUCTION = """\
Turn each item of the storyboard above into a image prompt. Please use Danbooru tag format for the image prompt.
You have to include the anime archetype tags in the prompt.
Also, append the following tags to the end of the generated image prompt: masterpiece, best quality, very aesthetic, absurdres
**Attention**: Do not include conflicting tags.
"""

MIDJOURNEY_DIRECTOR_INSTRUCTION = """\
Turn each item of the storyboard above into a Midjourney image prompt.
Try to keep the prompt concise without losing details.
**Attention: Ensure the output prompt should be in full english!**
**[language requirement] English**
"""


DIRECTOR_EXAMPLE = """\
```json
{
    "prompt": "1girl, tsundere, solo, outdoors, short hair, sky, shirt, choker, looking at viewer, white shirt, blue eyes, black hair, day, blue sky, cloud, jacket, smile, open clothes, railing, hood, closed mouth, long sleeves, black choker, open jacket, building, hooded jacket, bob cut, hood down, city, blue jacket, lens flare, masterpiece, best quality, very aesthetic, absurdres"
}
```
"""

MIDJOURNEY_DIRECTOR_EXAMPLE = """\
```json
{
    "prompt": "A girl stands outdoors on a sunny day, with a blue sky and clouds overhead. She is wearing a white shirt with an open blue hooded jacket, the hood down. A black choker is around her neck, and she stands near a railing, looking at the viewer with a soft smile. Buildings are visible in the background, and there's a lens flare in the scene, adding warmth to the city setting."
}
```
"""

DIRECTOR_MULCHARACTER_EXAMPLE = """\
```json
{
    "prompt": "1girl, white hair, grey eyes, silver coat, 1boy, black hair, military uniform, couple, hug, close-up, happy, smiling, affectionate gaze, island, sea, romantic, anime, masterpiece, best quality, very aesthetic, absurdres"
}
```
"""

MIDJOURNEY_DIRECTOR_MULCHARACTER_EXAMPLE = """\
```json
{
    "prompt": "The image depicts a close-up of a couple(2 people) sharing an affectionate hug. The girl is an anime-style girl with long white hair and grey eyes wearing a silver coat. The boy is black hair boy in a military uniform. Both are smiling happily, exchanging warm, loving gazes. The scene is set on an island by the sea, creating a romantic atmosphere with anime-style visuals"
}
```
"""


DIRECTOR_PROMPT = """\
# Storyboard
{storyboard}

# Instruction
{instruction}

# Example Prompt for single character in the storyboard:
{example}

# **Example Prompt for multiple characters in the storyboard \
(should follow the format of "1girl/boy, (a few tags for the first character), 1girl/boy, (a few tags for the second character), scene descriptions): **
{multiple_character_example}

# Format
```json
{{
    "prompt": "xxx"
}}
```
"""

MIDJOURNEY_DIRECTOR_PROMPT = """\
# Storyboard
{storyboard}

# Instruction
{instruction}


# Example Prompt for single character:
{example}

# Example Prompt for multiple characters:
{multiple_character_example}


# Character Prompting Logic
- The number of characters in the scene is the length of "角色" in storyboard
- If only one character is present in the storyboard, follow the "Example Prompt for single character".
- If multiple characters are present, apply the "Example Prompt for multiple characters." Start by telling how many characters are in the scene. Then describe each character, along with their positions, interactions, and visual appearance.

**ATTENTION: output prompt MUST be in FULL ENGLISH!**

**[language requirement] English**

# Format
```json
{{
    "prompt": "xxx"
}}
```
"""



BATCH_DIRECTOR_PROMPT = """\
# Storyboards
{storyboard}

# Instruction
{instruction}


# Example Prompt for single character in the storyboard:
{example}

# Example Prompt for multiple characters in the storyboard:
{multiple_character_example}

# Character Prompting Logic
- The number of characters in the scene is the length of "角色" in storyboard
- If only one character is present in the storyboard, follow the "Example Prompt for single character".
- If multiple characters are present, apply the "Example Prompt for multiple characters." Start by telling how many characters are in the scene. Then describe each character, along with their positions, interactions, and visual appearance.

**你的输出应该是全英文的！**
**[language requirement] English**

# Format
```json
{{
    "prompts": [prompt1, prompt2, prompt3, ...]
}}
```

"""