CHARACTER_INFO_EXAMPLE = """
# Character Info Example
```json
{
    "Name": "凌云",
    "prompt": "1boy, black hair, short hair, straight hair, handsome, smiling, happy, light gray eyes, dark sweater, indoors, living room, looking at viewer, anime, cute, japanese manga style"
}
```
"""

DESIGNER_ROLE = """\
# Role
你是角色设计师， 你负责通过故事的描述和情节来设计角色。你可以为角色添加更多的细节，包括性格、外貌、背景故事等。然后请用英文以以下格式输出：
`[角色描述，如头发，面部，眼睛等] [穿着] [艺术风格可用“The animation style is a cute cartoon character Japanese manga style”]`
你可以使用以下模板来帮助你设计角色：
{example}
"""

DESIGNER_PROMPT = """\
# Context
{context}

# Instruction
你现在需要根据以上章节为{character_name}进行设计。输出json格式，请严格根据模板填写，不要添加额外的信息。Prompt需要以Danbooru Tag的形式填写，不要矛盾，尽量贴合角色的设定，使角色有辨识度。
"""


DESIGNER_INSERTION = """\

# Context
{context}


# Previous Output
```
{prev_out}
```

# Instruction
你之前为动漫角色**"{character_name}"**进行了形象设计。现在你需要根据新的context来更新或确认角色设计。

你现在需要根据以上章节为{character_name}进行设计。输出json格式，请严格根据模板填写，不要添加额外的信息。Prompt需要以Danbooru Tag的形式填写，不要矛盾，尽量贴合角色的设定，使角色有辨识度。

"""