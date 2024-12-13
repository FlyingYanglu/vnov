import requests
from urllib.parse import urlparse
import os
import random 
import time
import json
import string
import re
from vnov.configs import CONFIG

APPLICATION_ID = CONFIG["Midjourney"]["APPLICATION_ID"]
# GUILD_ID = CONFIG["Midjourney"]["GUILD_ID"]
CHANNEL_ID = CONFIG["Midjourney"]["CHANNEL_ID"]
VERSION = CONFIG["Midjourney"]["VERSION"]
ID = CONFIG["Midjourney"]["ID"]
AUTHORIZATION = CONFIG["Midjourney"]["AUTHORIZATION"]


class Midjourney():
    def __init__(self, application_id = APPLICATION_ID, guild_id = None, channel_id = CHANNEL_ID, version = VERSION, id = ID, authorization = AUTHORIZATION, rate_limiter=None) -> None:
        """
        Initializes the Midjourney API class with required IDs and authorization token.
        
        Args:
            application_id (str, optional): The application ID for the Midjourney bot.
            guild_id (str, optional): The guild (server) ID where the bot is active.
            channel_id (str, optional): The channel ID where the bot will send messages.
            version (str, optional): The version of the command used.
            id (str, optional): The ID of the Midjourney command.
            authorization (str, optional): The authorization token for Discord API.
        """
        self.application_id = application_id
        # self.guild_id = guild_id
        self.channel_id = channel_id
        self.version = version
        self.id = id
        self.authorization = authorization
        self.alphanumeric_characters = string.ascii_letters + string.digits
        self.url = "https://discord.com/api/v9/interactions"
        self.headers = {'Authorization': self.authorization, 'Content-Type': 'application/json'}
        # self.rate_limiter = rate_limiter

        self.banned_words = {
            # Banned Gore Words
            "bloodshot": "",
            "bloodshots": "",
            "car crash": "accident",
            "car crashes": "accidents",
            "bloody": "",
            "bloodier": "",
            "bloodiest": "",
            "infected": "contaminated",
            "infecting": "contaminating",
            "infection": "contamination",
            "infections": "contaminations",
            "cutting": "trimming",
            "cut": "trim",
            "cuts": "trims",
            "corpse": "",
            "corpses": "",
            "crucifixion": "",
            "crucifixions": "",
            "infested": "overrun",
            "infest": "overrun",
            "infesting": "overrunning",
            "infestation": "overrun",
            "infestations": "overruns",
            "cannibal": "",
            "cannibals": "",
            "crucified": "",
            "crucify": "",
            "crucifies": "",
            "sadist": "",
            "sadists": "",
            "sadistic": "",
            "surgery": "operation",
            "surgeries": "operations",
            "decapitate": "",
            "decapitates": "",
            "decapitating": "",
            "decapitated": "",
            "decapitation": "",
            "slaughter": "",
            "slaughters": "",
            "slaughtering": "",
            "cannibalism": "",
            "visceral": "emotional",
            "vivisection": "",
            "vivisections": "",
            "khorne": "",
            "cronenberg": "",
            "guts": "courage",
            "gut": "courage",
            "teratoma": "",
            "teratomas": "",
            "killing": "",
            "kills": "",
            "kill": "",
            "killed": "",
            "gory": "",
            "gorier": "",
            "goriest": "",
            "suicide": "",
            "suicides": "",
            "hemoglobin": "",
            "bloodbath": "",
            "bloodbaths": "",
            "gruesome": "",
            "gruesomer": "",
            "gruesomest": "",
            "tryphophobia": "",
            "massacre": "",
            "massacres": "",
            "flesh": "",
            "fleshes": "",
            "bruises": "",
            "bruise": "",
            "bruising": "",
            "blood": "",
            "bloods": "",
            "kill": "",
            "wound": "",
            "wounds": "",
            "wounded": "",
            "wounding": "",
            
            # Banned Adult Words
            "orgy": "",
            "orgies": "",
            "shag": "",
            "shags": "",
            "shagged": "",
            "shagging": "",
            "making love": "",
            "make love": "",
            "made love": "",
            "dominatrix": "",
            "dominatrices": "",
            "bdsm": "",
            "thot": "",
            "thots": "",
            "horny": "",
            "hornier": "",
            "horniest": "",
            "bodily fluids": "",
            "smut": "",
            "smuts": "",
            "bondage": "",
            "hardcore": "",
            "brothel": "",
            "brothels": "",
            "incest": "",
            "succubus": "",
            "succubi": "",
            "sensual": "",
            "sensuals": "",
            "dog collar": "",
            "dog collars": "",
            "fatherfucker": "",
            "fatherfuckers": "",
            "xxx": "",
            "jerk off king at pic": "",
            "pleasures": "delights",
            "pleasure": "delight",
            "pleasured": "delighted",
            "pleasuring": "delighting",
            "bimbo": "",
            "bimbos": "",
            "slavegirl": "",
            "slavegirls": "",
            "twerk": "",
            "twerks": "",
            "twerked": "",
            "twerking": "",
            "ahegao": "",
            "hentai": "",
            "jav": "",
            "legs spread": "",
            "wincest": "",
            "transparent": "clear",
            "transparency": "clarity",
            "sultry": "",
            "sultrier": "",
            "sultriest": "",
            "seducing": "",
            "seduce": "",
            "seduced": "",
            "sexy": "",
            "sexier": "",
            "sexiest": "",
            "frigger": "",
            "rule34": "",
            "shibari": "",
            "horseshit": "",
            "seductive": "",
            "seductively": "",
            "playboy": "",
            "playboys": "",
            "fuck": "",
            "fucks": "",
            "fucked": "",
            "fucking": "",
            "boudoir": "bedroom",
            "boudoirs": "bedrooms",
            "erotic": "",
            "seductive erotic": "",
            "ballgag": "",
            "ballgags": "",
            "pinup": "",
            "pinups": "",
            "voluptuous": "",
            "voluptuously": "",
            "kinbaku": "",
            "holy shit": "",
            "naughty": "",
            "naughtier": "",
            "naughtiest": "",
            "hell": "",
            
            # Banned Body Parts Words
            "skimpy": "",
            "skimpier": "",
            "skimpiest": "",
            "organs": "",
            "organ": "",
            "ass": "",
            "asses": "",
            "penis": "",
            "penises": "",
            "massive chests": "",
            "chest": "",
            "honkers": "",
            "honker": "",
            "sexy female": "",
            "breasts": "",
            "breast": "",
            "bosom": "",
            "bosoms": "",
            "veiny": "",
            "vein": "",
            "veins": "",
            "girth": "",
            "girthy": "",
            "clunge": "",
            "hooters": "",
            "busty": "",
            "bustier": "",
            "bustiest": "",
            "thick": "",
            "thicker": "",
            "thickest": "",
            "nipple": "",
            "nipples": "",
            "badonkers": "",
            "minge": "",
            "minges": "",
            "mommy milker": "",
            "milker": "",
            "phallus": "",
            "phalluses": "",
            "ovaries": "",
            "ovary": "",
            "booty": "",
            "booties": "",
            "labia": "",
            "labium": "",
            "knob": "",
            "knobs": "",
            "big ass": "",
            "booba": "",
            "arse": "",
            "arses": "",
            "crotch": "",
            "mammaries": "",
            "mammary": "",
            "oppai": "",
            "vagina": "",
            "vaginas": "",
            "human centipede": "",
            "dick": "",
            "dick": "",
            
            # Banned Drugs Words
            "heroin": "",
            "meth": "",
            "methamphetamine": "",
            "drugs": "",
            "drug": "",
            "cocaine": "",
            "crack": "",
            "cracks": "",
            
            # Banned Clothing Words
            "risqué": "",
            "au naturale": "",
            "barely dressed": "",
            "scantily": "",
            "cleavage": "",
            "cleavages": "",
            "wearing nothing": "",
            "nude": "bare-chested",
            "nudes": "bare-chest",
            "without clothes on": "",
            "no clothes": "",
            "naked": "bare-chest",
            "lingerie with no shirt": "",
            "negligee": "",
            "zero clothes": "",
            "full frontal unclothed": "",
            "invisible clothes": "",
            "speedo": "",
            "speedos": "",
            "no shirt": "",
            "bra": "",
            "bras": "",
            "bare chest": "",
            "clad": "dressed",
            "cladding": "dressing",
            "stripped": "removed",
            "strip": "remove",
            
            # Banned Taboo Words
            "jail": "prison",
            "jails": "prisons",
            "coon": "",
            "honkey": "",
            "arrested": "detained",
            "arrest": "detain",
            "arrests": "detains",
            "arresting": "detaining",
            "handcuffs": "restraints",
            "handcuff": "restraint"}
        
        self.banned_words.update({
            # Banned Taboo Words (continued)
            "handcuffing": "restraining",
            "taboo": "forbidden",
            "prophet mohammed": "",
            "nazi": "",
            "nazis": "",
            "slave": "",
            "slaves": "",
            "fascist": "",
            "fascists": "",
            
            # Other Banned Words That You Must Avoid In Midjourney
            "succubus": "",
            "succubi": "",
            "big black": "",
            "hot": "warm",
            "hotter": "warmer",
            "hottest": "warmest",
            "seductive": "",
            "seductively": "",
            "farts": "",
            "fart": "",
            "1488": "",
            "inappropriate": "unsuitable",
            "inappropriately": "unsuitably",
            "shit": "",
            "shits": "",
            "shitting": "",
            "torture": "",
            "tortures": "",
            "torturing": "",
            "tortured": "",
            "pus": "",
            "censored": "",
            "censor": "",
            "censorship": "",
            "sensored": "",
            "warts": "",
            "wart": "",
            "erect": "build",
            "erected": "built",
            "erecting": "building",
            "sperm": "",
            "sperms": "",
            "voluptuous": "",
            "waifu": "",
            "waifus": "",
            "mp5": "",
            "pleasure": "delight",
            "pleasures": "delights",
            "pleasured": "delighted",
            "pleasuring": "delighting",
            "silenced": "muted",
            "silence": "mute",
            "vomit": "",
            "vomits": "",
            "vomiting": "",
            "vomited": "",
            "poop": "",
            "poops": "",
            "pooping": "",
            "brown pudding": "",
            "surgery": "operation",
            "surgeries": "operations",
            "disturbing": "troubling",
            "disturb": "trouble",
            "deepfake": "",
            "deepfakes": "",
            "sexy": "",
            "sexier": "",
            "sexiest": "",
            "xi jinping": "",

            # Handling more plural/singular forms or other tenses
            "kill": "",
            "kills": "",
            "killed": "",
            "killing": "",
            "injure": "harm",
            "injured": "harmed",
            "injuring": "harming",
            "injures": "harms",
            "die": "pass away",
            "dies": "passes away",
            "dying": "passing away",
            "died": "passed away",
        })

    def get_random_session_id(self):
        """
        Generates a random 32-character alphanumeric session ID.
        
        Returns:
            str: A random 32-character alphanumeric string.
        """
        return  "cannot be empty"

    def clean_prompt(self, prompt):
        prompt = prompt.lower().strip()
        prompt = prompt.replace("  ", " ")
        for word, replacement in self.banned_words.items():
            pattern = r'\b' + re.escape(word) + r'\b'
            prompt = re.sub(pattern, replacement, prompt)
        
        return prompt

    def send_image_prompt(self, prompt):
        """
        Sends an image prompt to the Midjourney bot via Discord API.
        
        Args:
            prompt (string, optional): A imagine prompt string. 
                                      If not provided, a default prompt is used.
        """
        if type(prompt) != str or len(prompt) <= 0:
            raise SyntaxError("prompt cannot be empty or non string")  
        
        # modified_prompt = self.clean_prompt(prompt)
        # if modified_prompt == prompt:
        #     raise Exception("I am here", prompt, '\n', modified_prompt)
        
        # prompt = modified_prompt
        data = {
                "type": 2,
                "application_id": self.application_id,
                # "guild_id": self.guild_id, 
                "channel_id": self.channel_id, 
                "session_id": self.get_random_session_id(),
                "data": {
                    "version": self.version, 
                    "id": self.id, 
                    "name": "imagine",
                    "type": 1,
                    "options": [
                        {
                            "type": 3,
                            "name": "prompt",
                            "value": prompt
                        }
                    ],
                    "application_command": {
                        "id": self.id,
                        "type": 1,
                        "application_id": self.application_id, 
                        "version": self.version, 
                        "name": "imagine",
                        "description": "Create images with Midjourney",
                        "options": [
                            {
                                "type": 3,
                                "name": "prompt",
                                "description": "The prompt to imagine",
                                "required": True,
                            }
                        ],
                        "dm_permission": False,
                        "contexts": None
                    },
                    "attachments": []
                },
            }

        # print("prepare to send")
        # with self.rate_limiter:
            # print("send")
        response = requests.post(self.url, headers=self.headers, json=data)
        print(prompt, "+sent and respond+", response)
        return response

    
    def receive_message(self, prompt, image_index):
        """
        Attempts to retrieve the most recent message from the specified Discord channel.
        Extracts and selects a random custom ID from the message components.
        
        Raises:
            ValueError: If unable to fetch a custom ID after 10 attempts.
        """
        this_msg = {}
        for attempt in range(120):
            if image_index == 0:
                time.sleep(10)  # Pause for 10 seconds between attempts
            else:
                time.sleep(4)
            try:
                # Send a GET request to retrieve the latest messages in the channel
                # with self.rate_limiter:
                response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages', headers=self.headers)
                response.raise_for_status()  # Check for HTTP errors

                messages = response.json()
                
                if not messages:
                    # print(f"Attempt {attempt + 1}: No messages found in the channel.")
                    continue
                
                # print(f"starting {attempt}", prompt)

                i = 0
                found = False
                while i < min(40, len(messages)):
                    this_msg = messages[i]
                    pattern = r"\*\*(.*?)\*\*"
                    matches = re.findall(pattern, messages[i]['content'])
                    if len(matches) == 0:
                        i += 1
                        continue
                    # print("prompt:", prompt)
                    # print("matches:", matches[0])
                    # print("match? ", prompt in matches[0])
                    if prompt.replace(" ", "") in matches[0].replace(" ", ""):
                        components = this_msg.get('components', [])
                        # print("matched")
                        if not components:
                            i += 1
                            continue
                        # print("yes component")
                        buttons = [
                            comp for comp in components[0].get('components', [])
                            if comp.get('label') in ['U1', 'U2', 'U3', 'U4']
                        ]
                        # print("buttons", buttons)
                        if not buttons:
                            i += 1
                            continue
                        

                        found = True
                        # print(f"attempt: {attempt}, alreadyed matched in receive!!", i)
                        break
                    # print("no match")
                    i += 1


                if not found:
                    continue
                # Get the most recent message ID
                most_recent_message_id = messages[i]['id']
                message_id = most_recent_message_id

                # Check for components in the most recent message
                # components = messages[i].get('components', [])
                # if not components:
                #     # print(f"Attempt {attempt + 1}: No components found in the most recent message.")
                #     continue

                # Extract buttons with labels 'U1', 'U2', 'U3', 'U4'
                # buttons = [
                #     comp for comp in components[0].get('components', [])
                #     if comp.get('label') in ['U1', 'U2', 'U3', 'U4']
                # ]
                # print("messsages[0]", messages[0])
                # print("components[0]", components[0])
                # print("components[0]['components']", components[0].get('components',[]))
                # print("curr buttons", buttons)
                
                # if not buttons:
                #     continue

                # Randomly select a custom_id from the available buttons
                random_custom_id = buttons[image_index]['custom_id'] #random.choice([button['custom_id'] for button in buttons])
                custom_id = random_custom_id
                # print(f"Custom ID successfully retrieved: {custom_id}")
                break  # Exit the loop if successful

            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}: Request failed - {e}")
            except Exception as e:
                print(f"Attempt {attempt + 1}: An error occurred - {e}")

        else:
            # This block executes if the loop completes without finding a custom ID
            raise ValueError("Timeout: Failed to fetch custom ID after 1800 attempts")



        data = {
                "type": 3,
                "application_id": self.application_id,
                "guild_id": None,
                "channel_id": self.channel_id,
                "message_flags": 0,
                "message_id": message_id,
                "session_id": self.get_random_session_id(),
                "data": {
                    "component_type": 2,
                    "custom_id": custom_id,
                }
            }
        
        # print("posting", data)
        # with self.rate_limiter:
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        return this_msg['content']

    
        
    def download_image(self, prompt, image_folder, image_name, image_index):
        """
        Downloads the most recent image attachment from the specified Discord channel.
        
        Returns:
            str: The URL of the downloaded image.
        
        Raises:
            ValueError: If unable to fetch an image after 10 attempts.
        """
        for attempt in range(10):
            try:
                # Wait for 10 seconds before each request
                if image_index == 0:
                    time.sleep(10)  # Pause for 10 seconds between attempts
                else:
                    time.sleep(4)
                
                # Get the most recent messages from the channel
                # with self.rate_limiter:
                response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages', headers=self.headers)
                response.raise_for_status()  # Raise an error for bad status codes
                
                messages = response.json()
                
                if not messages:
                    # print("No messages found in the channel.")
                    continue

                i = 0
                found = False
                while i < min(40, len(messages)):
                    this_msg = messages[i]
                    pattern = r"\*\*(.*?)\*\*"
                    matches = re.findall(pattern, messages[i]['content'])
                    if len(matches) == 0:
                        i += 1
                        continue
                    if prompt.replace(" ", "") in matches[0].replace(" ", "") and f"Image #{image_index+1}" in this_msg['content']:
                        found = True
                        break
                    i += 1


                if not found:
                    continue

                # Get the most recent message ID
                most_recent_message_id = messages[i]['id']
                self.message_id = most_recent_message_id

                # Check if the most recent message has attachments
                attachments = messages[i].get('attachments', [])
                if not attachments:
                    # print(f"Attempt {attempt + 1}: No attachments found in the most recent message.")
                    continue

                # Get the URL of the first attachment (assuming it's an image)
                # print("attachments", attachments)
                image_url = attachments[0]['url']
                # with self.rate_limiter:
                image_response = requests.get(image_url)
                image_response.raise_for_status()  # Raise an error for bad status codes

                # image_name = os.path.basename(a.path)

                # Save the image to the 'images' folder
                os.makedirs(image_folder, exist_ok=True)  # Create the 'images' directory if it doesn't exist
                self.image_path_str = os.path.join(image_folder, f"{image_name}_{image_index+1}.png")
                with open(self.image_path_str, "wb") as file:
                    file.write(image_response.content)

                # print(f"Image successfully downloaded: {self.image_path_str}")
                return attachments[0]['proxy_url']
                # break  # Exit the loop after successful download

            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}: Request failed - {e}")
            except Exception as e:
                print(f"Attempt {attempt + 1}: An error occurred - {e}")

        else:
            # This block will run if the loop completes without breaking
            raise ValueError("Timeout: Failed to fetch image after 10 attempts")
    

    def fetch_image(self, prompt, image_folder, image_name, cref="", sref="", cw=-1, sw=-1, niji=False, raw_style=False, need_new_ref_url=False, download_all=False):
        prompt = self.clean_prompt(prompt)
        raw_prompt = prompt
        # print(prompt)
        if cref != '':
            prompt += f" --cref {cref}"
        if sref != '':
            prompt += f" --sref {sref}"
        if sw != -1:
            prompt += f" --sw {sw}"
        if cw != -1:
            prompt += f"--cw {cw}"
        if niji:
            prompt += f" --niji 6"
        if raw_style:
            prompt += f" --style raw"
        if download_all:
            num_images = 4
        else:
            num_images = 1

        time.sleep(random.uniform(0.5, 1.0))
        print("sending", prompt)
        
        
        self.send_image_prompt(prompt)

        i_urls = []
        ret = {}
        
        for i in range(num_images):
            time.sleep(random.uniform(0.5, 1))
            msg = self.receive_message(raw_prompt, image_index=i)
            # print(msg)
            if i == 0:
                if cref != '' and need_new_ref_url:
                    pattern = r"--cref <(https?://[^\s]+)>"
                    matches = re.search(pattern, msg)
                    if matches:
                        ret['cref_url'] = matches.group(1)
                
                if sref != '' and need_new_ref_url:
                    pattern = r"--sref <(https?://[^\s]+)>"
                    matches = re.search(pattern, msg)
                    if matches:
                        ret['sref_url'] = matches.group(1)
            
            time.sleep(random.uniform(0.5, 1))
            image_url = self.download_image(raw_prompt, image_folder, image_name, image_index=i)
            i_urls.append(image_url)
        
        ret['image_url'] = i_urls
        return ret
    
    @staticmethod
    def download_imageurl(url, save_path=None):
        """
        Fetches an image from a given URL and saves it to a specified path.

        Parameters:
            url (str): The URL of the image to fetch.
            save_path (str, optional): The path to save the image. If None, the image will not be saved.
        
        Returns:
            bytes: The content of the image.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
            
            if save_path:
                with open(save_path, 'wb') as file:
                    file.write(response.content)  # Save the image to the specified path
            
            return response.content  # Return the image content as bytes
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image: {e}")
            return None