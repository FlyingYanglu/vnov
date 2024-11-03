# Artist

ARTIST_ROLE = """\
你是一个画师，你懂得如何将文本转换成更好的提示词，以便生成更好的图像
"""

PROMPT_OPTIMIZATION = """\
# Content
```
{content}
```

# Instruction
将以上的内容(content)转换成若干个分镜，每个分镜大概对应原文的140字。如果分镜文字不够140字，分镜可以选择性忽略一些细节而来凑够字数。每个分镜的节奏和氛围都要体现文本的情感和氛围

分镜要求如下：
```
1. 分镜的镜头文本内容将会作为图像生成的提示词，给到图像生成器生成对应的图像，提示词需要包含角色、场景、情感等信息。
2. 然后请按照我的指令，将每一个部分生成标准英文(in full english)的Midjourney prompt，格式如下（以"，"分割）：`【生成物】，【照明效果】，【画面风格】，【画面比例/ar参数】`，生成物：你可以发挥想象力，用精准和精炼的语言描述刚刚的场景。照明效果：你可以选择cinematic lighting，sunlight，或类似的词语。画面风格：画面风格大致是"japanese cute cartoon character style", 但在你认为合适的特定场景下可以更改。并在每一条prompt后面加上以下内容： `--ar 16:9` （值不变，无，间）
3. 每张图片最好只有一个角色。如果分镜里只有“我”（史金），那分镜图像只需要有“我”（史金)。如果分镜里有“我”（史金）和其他角色，那么请以“我”（史金）的视角来生成这张图片（分镜无需有史金）。如果分镜里没有“我”，那就按照分镜里的角色正常生成其他角色对应的提示词。
4. 如果图片中有角色，请在prompt的结尾加上 `--cref --[图片中的做动作的角色的名字]`。如果图片中的做动作的角色是“我”，那可以加"{main_character}"。如果图片有"我"但主要做动作的角色是别的角色，那就在prompt结尾加`--[别的角色的名字]`不要加`--{main_character}`。
5. `--cref [角色]` 的时候请从下面的角色列表里选一个。如果没有合适的角色, 请就不要加任何`--cref`.
6. 请不要在除了prompt结尾的地方加角色的名字。如果要在prompt里非结尾的地方写角色，请用`a [adjective] woman, a [adjective] man, a [adjective] girl, a [adjective] boy`代替。

分镜prompt例子1: `The anime features a cute, beautiful girl with long white hair and pink eyes, wearing an off-the-shoulder dress. The background shows a bustling modern city with towering skyscrapers and flowing traffic. The animation style is a cute cartoon character japanese manga style. --ar 16:9 --cref --图片中的做动作的角色的名字`
分镜prompt例子2: `The anime depicts a black haired, handsome young man of about twenty years smiling happily at the camera in his living room. He has short to medium length straight hair and light gray eyes. He is wearing a dark sweater. The background shows simple bedroom decoration. The animation style is a cute cartoon character japanese manga style. --ar 16:9 --cref --图片中的做动作的角色的名字`
```

角色列表:
```
{character_set}
```

# Format
请输出一个json，每个分镜的格式如下：
原文为对应的文本内容，分镜提示词为将要生成的图像
```json
[
{{
    "原文": "",
    "分镜提示词": ""
}},
...
]
```

"""
