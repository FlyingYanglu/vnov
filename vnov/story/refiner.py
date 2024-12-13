from vnov.story.prompts import (
    REFINE_CHAPTERS,
    REFINE_GREETING, 
    REFINE_SYSTEM_MSG
)
from vnov.role import Role
from vnov.data import Novel
from vnov.utils import extract_json_from_string
import json
import time
import os
import tqdm
import re

class Refiner(Role):
    role = "refiner"
    bot_id = "vnoRefiner"
    bot_token_max_length = 4000

    def refine_chapters(self, chapter1, chapter2, main_character):
        while True:
            try:
                response = self.model(REFINE_CHAPTERS.format(chapter1=chapter1, chapter2=chapter2, main_character=main_character),
                                    bot_id=self.bot_id,
                                    system_msg=REFINE_SYSTEM_MSG)
                response_json = self.parse_response(response)
                first_half_response, second_half_response = response_json["chapter_1_refined"], response_json["chapter_2_refined"]
                return first_half_response, second_half_response
            except Exception as e:
                print(f"Failed to generate response for chapters, retrying...")
                print(e)
                if "Rate limit exceeded" in str(e):
                    print("Rate limit exceeded, waiting for 5 minutes...")
                    time.sleep(60*5)
                    self.send_greeting_message()
                continue



    def parse_response(self, response):
        # response = response[response.index("{"):response.rindex("}")+1]
        # response_json = json.loads(response)
        # return response_json
        response_json = extract_json_from_string(response)
        return response_json
    
    def send_greeting_message(self):
        self.model(REFINE_GREETING, bot_id=self.bot_id, new_chat=True, system_msg=REFINE_SYSTEM_MSG)

    def save_prompt(self, save_dir):
        prompts = {
            "REFINE_CHAPTERS": REFINE_CHAPTERS,
            "REFINE_GREETING": REFINE_GREETING,
            "REFINE_SYSTEM_MSG": REFINE_SYSTEM_MSG
        }
        with open(os.path.join(save_dir, "refine_prompts.json"), "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=4)

    def refine_novel(self, novel: Novel, start_chapter=1, end_chapter=None, save_dir=None, main_character="史金", skip_refine=False, **kwargs):
        if save_dir is None:
            save_dir = os.path.join(novel.dir, Novel.dirs_dict["refined"])
        
        # Save the prompts for consistency
        self.save_prompt(save_dir)

        # Skip refinement and copy novel content if specified
        if skip_refine:
            print("Skipping refinement, copying original novel content...")
            self.copy_novel_to_refined(novel, save_dir)
            return

        self.send_greeting_message()
        if end_chapter is None:
            end_chapter = novel.num_chapters + 1
        
        last_context = ""
        for chapter_num in tqdm.tqdm(range(start_chapter, end_chapter + 1)):
            chapter_content = novel.load_chapter(chapter_num, mode=Novel.NOVEL_MODE.SCRIPT)
            chapter_chunks = Novel.split_chapter(
                chapter_content,
                self.bot_token_max_length - len(REFINE_CHAPTERS) - len(last_context)
            )
            for part, chapter_content in enumerate(chapter_chunks):
                if not last_context:
                    last_context = chapter_content
                    last_part_tuple = (chapter_num, part)
                    continue
                first_half_response, second_half_response = self.refine_chapters(last_context, chapter_content, main_character)
                last_chapter_num = last_part_tuple[0]
                last_part_num = last_part_tuple[1]
                self.save_refined(first_half_response, last_chapter_num, last_part_num, save_dir=save_dir)
                last_context = second_half_response
                last_part_tuple = (chapter_num, part)
        
        if last_context:
            self.save_refined(second_half_response, chapter_num, part, save_dir=save_dir)

        self.concatenate_refined(save_dir)

    
    def save_refined(self, content, chapter_num, part_num, save_dir, delimiter="|"):
        if delimiter:
            content = content.replace(delimiter, "\n")
        dir = os.path.join(save_dir, f'{chapter_num}_part{part_num}.txt')
        with open(dir, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def concatenate_refined(save_dir, file_name="combined_commentaries"):
        refined_script_dir = save_dir
        all_chapters = sorted([f for f in os.listdir(refined_script_dir) if re.match(r"\d+_part\d+.txt", f)],
                               key=lambda v:(int(v.split("_part")[0]) , int(v.split("_part")[1].split(".")[0])))
        with open(os.path.join(refined_script_dir, file_name + ".txt"), 'w', encoding='utf-8') as outfile:
            # Iterate through all the .txt files
            for txt_file in all_chapters:
                # Open each .txt file in read mode
                with open(os.path.join(refined_script_dir, txt_file), 'r', encoding='utf-8') as infile:
                    # Read the content of the file and write it to the output file
                    outfile.write(infile.read())
                    outfile.write('\n')  # Optionally add a newline between files


    def copy_novel_to_refined(self, novel: Novel, save_dir=None):
        """Copy the original novel to the refined folder."""
        if save_dir is None:
            save_dir = os.path.join(novel.dir, Novel.dirs_dict["refined_script"])
        
        # Ensure the save directory exists
        os.makedirs(save_dir, exist_ok=True)

        for chapter_num in range(1, novel.num_chapters + 1):
            chapter_content = novel.load_chapter(chapter_num, mode=Novel.NOVEL_MODE.SCRIPT)
            file_path = os.path.join(save_dir, f"{chapter_num}_part0.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(chapter_content)