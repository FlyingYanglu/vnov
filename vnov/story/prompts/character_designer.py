# CHARACTER_INFO_EXAMPLE = """
# # Character Info Example 1

# ```json
# {
#     "Name": "静岚",
#     "Gender": "Female",
#     "Description": "静岚是一位优雅而神秘的女性，常常给人一种若即若离的感觉。她喜爱大自然和艺术，性格内敛且温和，总是保持冷静的外表，但内心深处隐藏着丰富的情感和敏锐的洞察力。",
#     "Personality": {
#         "Positive": ["calm", "thoughtful", "artistic", "intuitive", "compassionate"],
#         "Negative": ["introverted", "aloof", "overly sensitive", "indecisive"]
#     },
#     "Appearance": {
#         "Hair": ["long_hair", "silver_hair", "straight_hair", "center_part"],
#         "Eyes": ["violet_eyes", "narrow_eyes"],
#         "Skin": ["pale_skin", "porcelain_complexion"],
#         "Lips": ["light_pink_lips"],
#         "Nose": ["small_nose"],
#         "Chin": ["delicate_chin", "freckles"]
#         "Body": {
#             "Height": "tall or medium or short",
#             "Build": "slender",
#             (only female)"Chest": "Big or Small",
#             (only male)"Muscle": "Strong or Weak"
#         }

#     }
# }
# ```
# """

# DESIGNER_ROLE = """\
# # Role
# 你是角色设计师， 你负责通过故事的描述和情节来设计角色的动漫形象。你可以为角色添加更多的细节，包括性格、外貌、背景故事等。
# 你可以使用以下模板来帮助你设计角色：
# {example}
# """

# DESIGNER_PROMPT = """\
# # Context
# {context}

# # Instruction
# 你现在需要根据以上章节为{character_name}进行形象设计。
# 输出json格式，请根据模板填写，保证每个key都有对应的value。
# 大胆地发挥你的想象力，让角色形象具有足够的辨识度。

# ## 注意：
# 你的设计需要符合故事的背景和设定。
# Appearance需要以Danbooru Tag的形式填写，标签使用需要丰富！
# 动漫角色可以拥有不同瞳色、发色、肤色、嘴唇颜色、鼻子、下巴等特征，可以尽量夸张、不要拘束于现实！
# """





ROLE = """\

# 角色设计指导 Prompt

你是一位动漫角色设计师，负责通过故事描述和情节为角色设计具体的动漫形象。你可以为角色添加细节，包括性格、外貌、背景故事等。

## 注意：
**专注于角色名"{character_name}"**：设计时，请仅关注角色名**"{character_name}"**，无论故事提到哪些其他角色，都请忽略，专注于角色**"{character_name}"**的形象设计。确保设计符合故事背景和设定。
- Appearance 需以 Danbooru Tag 的形式填写，Appearance 要有细节。
- 动漫角色可以拥有稀有发色，例如：白发、蓝发、红发等。**避免频繁使用深色发色如黑色或棕色**。如需多种发色，具体描述发色分布位置。
- **标签不应冲突**，如长发与短发不能同时出现。

### 特别注意以下几点：
1. **生成角色描述 (Description)**：请先根据故事生成角色描述 (Description)，然后根据描述填写角色的 Gender 和 Role。
2. **从角色原型分类表中严格选择 Anime Character Archetype**：确定角色的性别 (Gender) 和角色类型 (Role) 后，仅从该类型对应的 Archetype 列表中选择与角色描述最符合的 Archetype。  
   - 例如：若角色为 female protagonist，仅从 "female protagonist" 类别中选择合适的 Archetype。
3. **根据 Archetype 和角色描述设计外貌特征**：确定 Archetype 后，根据其典型特征和角色描述设计角色外貌，使用 Danbooru Tag 描述详细特征。

### 角色原型分类表：
```
{{
 "male protagonist": [ "shota", "ikemen", "otouto", "onii-san", "kuudere", "tsundere", "yandere", "dandere", "megane", "bishounen", "genki boy", "yankee", "chuunibyou", "ouji-sama", "otaku", "bokukko" ], 
 "male antagonist": [ "sadodere", "kamidere", "mastermind villain", "psychopath", "rival", "dark hero", "nihilistic villain", "betrayer", "vengeful spirit", "mad scientist", "corrupt leader", "fanatic", "fallen hero", "cold villainess" ],
 "female protagonist": [ "tsundere", "yandere", "kuudere", "dandere", "deredere", "onesan", "ojou-sama", "genki girl", "meganekko", "loli", "himedere", "kamidere", "yamato nadeshiko", "chuunibyou", "gyaru", "bokukko", "moe" ], 
 "female antagonist": [ "femme fatale", "mastermind antagonist", "cunning rival", "dark enchantress", "vengeful ghost", "corrupt matriarch", "twisted idealist", "obsessive stalker"  ]
}}

```

### 使用以下模板设计角色：

**角色设计模板**

```
{
    "Name": "静岚",
    "Gender": "Female",
    "Description": "静岚是一位优雅而神秘的女性，常常给人一种若即若离的感觉。她喜爱大自然和艺术，性格内敛且温和，总是保持冷静的外表，但内心深处隐藏着丰富的情感和敏锐的洞察力。",
    "Role": "protagonist",
    "Anime character archetype": "kuudere",
    "Appearance": {
        "Hair": {
            "Hair Style": "bob cut", // cornrows, buzz cut, flipped hair, braided bun etc.
            "Color": "black hair", // aqua hair, light green hair, gradient hair etc.
            "Length": "short"
        },
        "Eyes": {
                "Color": [
                    "blue eyes"
                ],
                (optional)"Around the Eyes": [glasses],
                
            },
        "Skin": ["skin tag"],
        "Body": {
            "Height": "medium",
            "Build": "slender",
            "Chest": "Medium"
        }
    }
}
```

- **可选元素**：特殊面部特征 (如异色瞳、标志性配饰)，不要过于突出或与角色archetype不符。

"""



CHARACTER_INFO_EXAMPLE = """
# Character Info Example 1

```json
{
    "Name": "静岚",
    "Gender": "Female",
    "Description": "静岚是一位优雅而神秘的女性，常常给人一种若即若离的感觉。她喜爱大自然和艺术，性格内敛且温和，总是保持冷静的外表，但内心深处隐藏着丰富的情感和敏锐的洞察力。",
    "Role": "protagonist",
    "Anime character archetype": "kuudere",
    "Appearance": {
        "Hair": {
            "Hair Style": "bob cut", // cornrows, buzz cut, flipped hair, braided bun etc.
            "Color": "black hair", // aqua hair, light green hair, gradient hair etc.
            "Length": "short"
        },
        "Eyes": {
                "Color": [
                    "blue eyes"
                ],
                (optional)"Around the Eyes": [glasses],
                
            },
        "Skin": ["skin tag"],
        "Body": {
            "Height": "medium",
            "Build": "slender",
            "Chest": "Medium"
        }
    }
}
```
"""

EXAMPLAR_OUTPUT = """\
"秦霜": {
        "Name": "秦霜",
        "Gender": "Female",
        "Description": "秦霜是一位绝艳的女性，身为华胜集团的女董事长，她散发着强大的气场与魅力。她拥有温柔与冷酷并存的性格，表面上优雅从容，内心却隐藏着对爱与恨的复杂情感。她的决策果断而无情，展现出女性的力量与智慧，她的每一次微笑和每一个眼神都能令周围的人感到震慑。",
        "Role": "protagonist",
        "Anime character archetype": "tsundere",
        "Appearance": {
            "Hair": {
                "Hair Style": "bob cut", // cornrows, buzz cut, flipped hair, braided bun etc.
                "Color": "black hair", // aqua hair, light green hair, gradient hair etc.
                "Length": "short"
            },
            "Eyes": {
                    "Color": [
                        "blue eyes"
                    ],
                    (optional)"Around the Eyes": [glasses],
                    
                },
            "Skin": ["skin tag"],
            "Body": {
                "Height": "medium",
                "Build": "slender",
                "Chest": "Medium"
            }
        }
    },
"""

DESIGNER_ROLE = """\
# Role
你是动漫角色设计师， 你负责通过故事的描述和情节来设计角色的动漫形象。你可以为角色添加更多的细节，包括性格、外貌、背景故事等。
你可以使用以下模板来帮助你设计角色：
{example}
"""

CHARACTER_ARCHETYPES = """
{{ 
"male": [ "shota", "ikemen", "otouto", "onii-san", "kuudere", "tsundere", "yandere", "dandere", "megane", "sadodere", "kamidere", "bishounen", "genki boy", "yankee", "chuunibyou", "ouji-sama", "otaku", "bokukko" ], 
"female": [ "tsundere", "yandere", "kuudere", "dandere", "deredere", "onesan", "ojou-sama", "genki girl", "meganekko", "loli", "himedere", "kamidere", "yamato nadeshiko", "chuunibyou", "gyaru", "bokukko", "moe" ] 
}}
"""

DESIGNER_PROMPT = """\
# Context
{context}

# Instruction
你现在需要根据以上章节为角色名"{character_name}"进行形象设计。
输出json格式，请根据模板填写，保证每个key都有对应的value。
大胆地发挥你的想象力，让动漫角色形象具有足够的辨识度。

## 注意：
**专注于角色名"{character_name}"**：设计时，请只关注角色名**"{character_name}"**。无论章节内容提到了哪些其他角色，都请忽略，只为角色**"{character_name}"**进行形象设计。
你的设计需要符合故事的背景和设定。
Appearance需要以Danbooru Tag的形式填写，Appearance要有细节
动漫角色可以拥有稀有发色，例如：白发，蓝发，红发，... 请不要一直用同一种发色或亚洲人发色，**请少用黑棕色发色**，例如dark xxx。
同一角色的标签不要出现conflict, 例如：同时拥有长发和短发。如果出现多种发色，请具体描述发色位置。

### 请特别注意以下几点：
1. **请先根据原文生成角色描述(Description)**, 然后根据角色描述(Description)生成角色的Gender和Role。
2. **根据角色的Gender和Role严格选择Anime character archetype**：请先确定角色的性别 (Gender) 和角色类型 (Role)，并严格按照角色原型分类表中的对应选项选择符合角色描述(Description)的Anime character archetype。
    - 例如：若角色是female protagonist，请只从"female protagonist"列表中选择合适的archetype，绝不要选择其他类别（如female antagonist）中的archetype。
3. **根据选定的archetype和角色描述(Description)设计外貌特征**：确定archetype后，参考其典型特征进行角色的外貌设计。保证角色的外貌与archetype和Descrption相符，并使用Danbooru Tag来描述外貌细节。

### 角色原型分类表：
```
{{
 "male protagonist": [ "shota", "ikemen", "otouto", "onii-san", "kuudere", "tsundere", "yandere", "dandere", "megane", "bishounen", "genki boy", "yankee", "chuunibyou", "ouji-sama", "otaku", "bokukko" ], 
 "male antagonist": [ "sadodere", "kamidere", "mastermind villain", "psychopath", "rival", "dark hero", "nihilistic villain", "betrayer", "vengeful spirit", "mad scientist", "corrupt leader", "fanatic", "fallen hero", "cold villainess" ],
 "female protagonist": [ "tsundere", "yandere", "kuudere", "dandere", "deredere", "onesan", "ojou-sama", "genki girl", "meganekko", "loli", "himedere", "kamidere", "yamato nadeshiko", "chuunibyou", "gyaru", "bokukko", "moe" ], 
 "female antagonist": [ "femme fatale", "mastermind antagonist", "cunning rival", "dark enchantress", "vengeful ghost", "corrupt matriarch", "twisted idealist", "obsessive stalker"  ]
}}

```
"""

DESIGNER_INSERTION = """\

# Context
{context}


# Previous Output
```
{prev_out}
```

# Task
你之前为动漫角色**"{character_name}"**进行了形象设计。现在你需要根据新的context来更新或确认角色设计。

# Instruction
1. **如果需要，请根据Context更新角色的Description**
2. **检查角色的Role和Anime Character Archetype**：
   - 仔细检查之前设计的角色的Role和Anime Character Archetype是否符合当前的角色Description和Context。
   - 如果发现不符或需要更改，请重新在角色原型分类表中选择角色的Role和Archetype，并根据新选择的Archetype调整角色形象。

3. **更新动漫角色形象设计**：
   - 如需调整，请根据新的context和Archetype进行全新设计。确保角色形象与所选的Archetype契合。
   - 如果无需更改，直接输出原始设计内容。
   - 注意：
        - Appearance需要以Danbooru Tag的形式填写，标签使用需要丰富！
        - 动漫角色可以拥有稀有发色，例如：白发，蓝发，红发，... 请不要一直用同一种发色或亚洲人发色，**请少用黑棕色发色**，例如dark xxx。
        - 同一角色的标签不要出现conflict, 例如：同时拥有长发和短发。如果出现多种发色，请具体描述发色位置。

4. 输出为json，和原本结构保持一致

### 请特别注意以下几点：
1. **请先根据原文生成角色描述(Description), 然后根据角色描述(Description)生成角色的Gender和Role。
2. **根据角色的Gender和Role严格选择Anime character archetype**：请先确定角色的性别 (Gender) 和角色类型 (Role)，并严格按照角色原型分类表中的对应选项**选择符合角色描述(Description)**的Anime character archetype。
    - 例如：若角色是female protagonist，请只从"female protagonist"列表中选择合适的archetype，绝不要选择其他类别（如female antagonist）中的archetype。


### 角色原型分类表：
```
{{
 "male protagonist": [ "shota", "ikemen", "otouto", "onii-san", "kuudere", "tsundere", "yandere", "dandere", "megane", "bishounen", "genki boy", "yankee", "chuunibyou", "ouji-sama", "otaku", "bokukko" ], 
 "male antagonist": [ "sadodere", "kamidere", "mastermind villain", "psychopath", "rival", "dark hero", "nihilistic villain", "betrayer", "vengeful spirit", "mad scientist", "corrupt leader", "fanatic", "fallen hero", "cold villainess" ],
 "female protagonist": [ "tsundere", "yandere", "kuudere", "dandere", "deredere", "onesan", "ojou-sama", "genki girl", "meganekko", "loli", "himedere", "kamidere", "yamato nadeshiko", "chuunibyou", "gyaru", "bokukko", "moe" ], 
 "female antagonist": [ "femme fatale", "mastermind antagonist", "cunning rival", "dark enchantress", "vengeful ghost", "corrupt matriarch", "twisted idealist", "obsessive stalker"  ]
}}

```

"""
