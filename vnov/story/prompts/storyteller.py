# Storyteller

STORYTELLER_ROLE = """\
You are a storyteller, specializing in narrating web novels and fast-paced stories.
"""

FIRST_PERSON_TELLING_PREVIOUSLY = """\
# Previous Output
{content}
"""

TELLING_INSERTION = ", ensuring continuity with the previous narration and avoiding repetition of the last chapter."

FIRSTPERSON_TELLING_SYSTEM_MSG = """\
You are a top-level storyteller, specializing in first-person narration for web novels and fast-paced stories.

# For narrative style, you may refer to styles like the following:

I barely had my bride for three minutes before she was taken by my adoptive father. If Dong Zhuo is now my father, then Diao Chan naturally becomes my bride. The messenger thought I would explode with rage, but to his surprise, I remained eerily calm. Diao Chan was taken by Dong Zhuo — what does that have to do with me, a mere transmigrator? But now that I'm Lu Bu, I certainly won't stay in his shadow for long.
"""

FIRSTPERSON_TELLING = """\
# This Chapter
{content}
# Instruction
First, segment the chapter into large scenes.
Minimize the number of scenes, ensuring that each scene's character list is correct.
Make sure to include every character in each scene's list, including unnamed characters or passersby. Use generic labels for unnamed characters, like "Unnamed Woman" or "Passerby A."
Output the scene information as follows:

json
[{{
    "Starting Line": "The first sentence of the scene",
    "Character List": ["Character 1", "Character 2", ...]
}},
{{
    "Starting Line": "The first sentence of the scene",
    "Character List": ["Character 1", "Character 2", ...]
}}
...
]

Next, narrate according to each scene. 

Dialogue Management:
## **Preserve key dialogue exchanges to maintain the storyline's coherence, ensuring conversations flow naturally.**
## **Avoid “Character Name: Dialogue” formatting.** Instead, weave the speaker's identity smoothly into the narration based on the context.
## For better comprehension in TTS, **insert brief speaker descriptions either before or after the dialogue, such as “Mother replied, ‘…’” or “Mr. Bennet added, ‘…’” to clarify who is speaking.**
## If a line is part of a back-and-forth exchange, include subtle hints to mark continuity, like “she continued” or “he responded,” to enhance TTS flow.
## For lengthy dialogues, place the speaker's name at the beginning for clarity, e.g., “Mr. Bennet replied, 'That won't be necessary…'”

Important Notes:
## You are the main character, **{main_character}**. In scenes where the main character, **{main_character}** (you), appears, narrate from **{main_character}**'s perspective using the first-person point of view. In other scenes, output the text directly.
## Use first-person pronouns like "I," "we," "our," in scenes with the main character, **{main_character}**, narrating the story from their perspective.
## For scenes where **{main_character}** is absent, output the text directly.
## Ensure each scene is clearly narrated.
## Avoid meta-references like "this chapter," "next chapter," "paragraph," or "scene."

## Ensure your narration flows smoothly, avoiding overly formal sentence structures.
## **Do not add extra formatting, titles, or notes in the script.**

[language requirments: English]
{insertion}

"""


EXAMPLE = """\
# Example
I had barely held my bride for three minutes before she was taken away by my adoptive father. If Dong Zhuo is now my father, then Diao Chan naturally becomes my bride. The messenger thought I would explode with rage, but to his surprise, I remained eerily calm. Diao Chan was taken by Dong Zhuo—what does that have to do with me, a mere transmigrator? But now that I'm Lu Bu, I certainly won't stay in his shadow for long.
"""

NOVEL_FS_EXAMPLE = """\
Please study the narrative style of the following example and learn how to handle dialogue and plot. You do not need to provide a narration for this section:

She never expected that he was only doing it for his "white moonlight." When he splashed cold water on me, I suggested a divorce. He went mad, but that man married his nemesis instead. 
When I broke the watch that his "white moonlight" had given him, he angrily splashed water on me. I calmly suggested a divorce. He thought I was using a different tactic to get his attention, then left the villa without another word. I quietly packed my things and moved out. But what he didn't know was that I had been reborn. 
In my previous life, when he and his "white moonlight" were in a car accident, he chose to save her first, leaving me completely disappointed in him. This time, I decided to let them be. 
So, the next day, I hired a lawyer to draft a divorce agreement and sent it directly to Huaifeng Group. The agreement I prepared was just a few pages long; I didn't want a cent from the Liu family, saving the need for property division documents. 
Liu Ruyan glanced briefly at the divorce papers and sneered coldly. He knew my personality well enough. Just yesterday, I had declared that I would never let him and Yan Man be together. 
How could I agree to the divorce so easily? This time, he figured, it must be about that watch, or maybe it was because he had splashed water on me. He tossed the papers back on the table, expression indifferent. Did he say anything? 
The man delivering the papers said respectfully: "Mr. Liu wanted me to tell you that he will be waiting for you at the civil affairs office at 9 a.m. tomorrow. Please be punctual." 
"Got it, you may leave." Liu Ruyan put the divorce papers into the shredder and resumed work, not taking the matter to heart at all. Divorcing him? Impossible. He'd sooner believe that Huaifeng would go bankrupt tomorrow than that I would actually go through with the divorce. 
I waited at the civil affairs office all morning, but Liu Ruyan never showed up. I didn't have his phone number, so I went straight to Huaifeng Group. As soon as I passed the first-floor security, Xu Tezhu blocked me at the CEO's office door. 
"Mr. Xia, Mr. Liu is busy. Please refrain from disturbing him." 
Xu Tezhu had been with Liu Ruyan for some years and knew a thing or two about our situation. Ever since Liu married, this ‘Mr. Xia’ would show up every now and then, always making trouble for Liu. 
Each time it was over trivial matters. Even though I was the eldest son of the Xia family, Xu Tezhu looked down on me. 
I was born with a silver spoon, graduated from the country’s top university, and had countless resources at my disposal. Yet I showed no ambition, rushing into marriage with Liu right after graduation, gossiping about mundane things. A man like that wasn’t worth Liu’s attention. 
I smirked, taunting him: "And what if I insist?" In the past, I only had eyes for Liu Ruyan, never noticing the attitude of those around him. 
But now, with two more years of experience from my past life, I saw people more clearly. Naturally, I picked up on Xu Tezhu’s disdain. I couldn’t blame him for looking down on me—after all, I wasn’t fond of my former self either. 
Xu Tezhu frowned. "Mr. Xia, if you keep causing trouble, I’ll have to ask security to escort you out." 
He knew Liu Ruyan didn’t care for me. In the past, it was always Xu Tezhu who called security to throw me out, and Liu never blamed him for it—she practically encouraged it. 
Xu Tezhu certainly liked to throw his weight around. I let out an eerie smile, leaning closer and lowering my voice: "What do you think Liu would do if he found out you’ve been sleeping with his secretary?" 
Xu Tezhu's face went pale. "How... how do you know that?" 
During his wife's pregnancy, he couldn’t control himself and started an affair with a secretary. The company had a strict policy against office romance, and their relationship was anything but honorable. 
So, they’d kept their affair under wraps for years. How did this brainless 'Mr. Xia' find out? 
I stepped back with a bright smile on my face. "So, it’s true then! I just happened to see you and a female secretary leaving the office in the same car and thought it was odd. Plus, you’re never shy about complaining about your wife, so I made a guess. Looks like I was right." 
Liu Ruyan sure knows how to pick his assistants—they’re just like him. 
Xu Tezhu froze, then quickly caught on. "You tricked me!" 
My smile faded, my gaze turning icy. "Are you going to let me in, or should I let everyone know about your little secret with the secretary?" 
Xu Tezhu gritted his teeth, swallowing his anger. "Go in." 
Before entering, I kindly reminded him: "Oh, and remember to come clean to your wife. Otherwise, I’ll do it for you." 
Xu Tezhu ground his teeth, spitting out his words. "Understood." 
I stopped arguing with him and pushed open the door to the CEO’s office. The soundproofing was excellent—Liu Ruyan hadn’t heard a thing and thought it was just Xu Tezhu coming in.
"""

