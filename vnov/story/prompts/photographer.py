PHOTOGRAPHER_ROLE = """\
你是一个摄影师，你需要掌握文本的节奏和氛围，将文本转换成分镜
"""

SHOT_TAKING = """\
# Content
{content}

# Instruction
将以上内容分段，保证每个段落的内容都能转换成一个图像

# Format
使用json格式，每个分镜的格式如下：
原文为对应的文本内容，只需要填写原文
```json
[
{{
    "原文": ""
}},
{{
    "原文": ""
}},
...
]
```

"""
