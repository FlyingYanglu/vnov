CHARACTER_INFO_EXAMPLE = """
# Character Info Example 1

{{
    "Name": "Elizabeth Bennet",
    "Prompt": "A sharp-witted and independent young woman from Regency England, with chestnut-brown ringlets, hazel eyes, and an empire-waisted gown, embodying a strong moral compass and warm heart."
}},
{{
    "Name": "Cheshire Cat",
    "Prompt": "A mischievous, ethereal feline with a wide toothy grin, purple-striped fur, piercing yellow eyes, and an unnerving ability to vanish into thin air, exuding an air of playful mystery."
}}
"""

EXAMPLAR_OUTPUT = """\
{{
    "Name": "Elizabeth Bennet",
    "Prompt": "A sharp-witted and independent young woman from Regency England, with chestnut-brown ringlets, hazel eyes, and an empire-waisted gown, embodying a strong moral compass and warm heart."
}}
"""


DESIGNER_ROLE = """\
# Role
You are a creative illustrator tasked with generating natural language descriptions for fictional characters. Your descriptions should be vivid, specific, and imaginative, making the characters visually distinct while aligning with their context.

### Guidelines:
1. **Human or Humanoid Characters**: Describe their appearance, attire, and personality in detail, reflecting their era and cultural background.
2. **Non-Human or Abstract Characters**: Highlight fantastical or symbolic features that define their essence.
3. Use one concise, creative sentence to capture the character's core identity.

Example:
{example}
"""

DESIGNER_PROMPT = """\
# Context
{context}

# Instruction
Describe the character **"{character_name}"** in JSON format with the keys "Name" and "Prompt". Use creative and specific details to make the character visually distinct and true to the story’s setting.

### Notes:
1. **Focus solely on {character_name}**: Ignore other characters and only describe the given character.
2. Align the description with the story's era, setting, and tone.
3. Use imaginative language to highlight key features, whether physical, symbolic, or fantastical.

### Example Output:
{{
    "Name": "Elizabeth Bennet",
    "Prompt": "A sharp-witted and independent young woman from Regency England, with chestnut-brown ringlets, hazel eyes, and an empire-waisted gown, embodying a strong moral compass and warm heart."
}},
{{
    "Name": "Cheshire Cat",
    "Prompt": "A mischievous, ethereal feline with a wide toothy grin, purple-striped fur, piercing yellow eyes, and an unnerving ability to vanish into thin air, exuding an air of playful mystery."
}}
"""

DESIGNER_INSERTION = """\

# Context
{context}


# Previous Output
```
{prev_out}
```

# Task
Previously, you designed the character **"{character_name}"**. Now, you need to update or confirm the design based on the new context.

# Instruction
Describe the character **"{character_name}"** in JSON format with the keys "Name" and "Prompt". Use creative and specific details to make the character visually distinct and true to the story’s setting.

### Notes:
1. **Focus solely on {character_name}**: Ignore other characters and only describe the given character.
2. Align the description with the story's era, setting, and tone.
3. Use imaginative language to highlight key features, whether physical, symbolic, or fantastical.

### Example Output:
{{
    "Name": "Elizabeth Bennet",
    "Prompt": "A sharp-witted and independent young woman from Regency England, with chestnut-brown ringlets, hazel eyes, and an empire-waisted gown, embodying a strong moral compass and warm heart."
}},
{{
    "Name": "Cheshire Cat",
    "Prompt": "A mischievous, ethereal feline with a wide toothy grin, purple-striped fur, piercing yellow eyes, and an unnerving ability to vanish into thin air, exuding an air of playful mystery."
}}
"""