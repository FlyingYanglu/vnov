from .base_processor import BaseProcessor
from vnov.story.prompts import SUMMARIZER_INSTRUCTION, LAST_SUMMARIZER_PROMPT
from vnov.data import Novel
import os
import asyncio

class Summarizer(BaseProcessor):
    bot_id = "vnovSummarizer"

    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self.role = "summarizer"

    def summarize_chapter(self, novel: Novel, chapter_num, summary_length="Concise", last_context="", new_chat=False, run_number = 1, iteration_number = None, save_dir=None):
        
        assert run_number is not None, "run_number must be provided"
        assert iteration_number is not None, "iteration_number must be provided"


        summaries, scene_jsons = [], []
        cur_max_length = self.calculate_cur_max_length(self.model, SUMMARIZER_INSTRUCTION, last_context)
        chapter_content = novel.load_chapter(chapter_num)
        # chapter_content, next_content = Novel.trunc_chapter(chapter_content, cur_max_length)
        chapter_content, next_content = chapter_content, None

        while chapter_content:
            print(f"Summarizing chapter {chapter_num} with length {summary_length}...")
            last_summary_prompt = self.create_prompt(
                LAST_SUMMARIZER_PROMPT,
                last_summary=last_context
            ) if last_context else ""

            prompt = last_summary_prompt + self.create_prompt(
                SUMMARIZER_INSTRUCTION,
                novel_context=chapter_content,
                summary_length=summary_length
            )

            try:
                _, scene_json = self.parse_response(
                    self.model(prompt, new_chat=new_chat, bot_id=self.bot_id)
                )
                if not scene_json:
                    raise Exception("No scene JSON found")
            except Exception as e:
                print(f"Error summarizing chapter {chapter_num}: {e}")
                self.handle_rate_limit(e)
                continue
            
            scene_jsons.append(scene_json)
            last_context = scene_json.get("summary", "")
            summaries.append(last_context)

            if next_content:
                cur_max_length = self.calculate_cur_max_length(self.model, SUMMARIZER_INSTRUCTION, last_context)
                chapter_content, next_content = Novel.trunc_chapter(next_content, cur_max_length)
            else:
                break

        summary = "\n".join(summaries)

        save_dir = save_dir or novel.get_dir("summary")
        self.save_file(summary, os.path.join(save_dir, f"{chapter_num}_summary_{summary_length}_run_{run_number}_iteration_{iteration_number}.txt"))
        self.save_json(scene_jsons, os.path.join(save_dir, f"{chapter_num}_summary_{summary_length}_run_{run_number}_iteration_{iteration_number}.json"))

        return summary, scene_jsons

    def summarize(self, novel: Novel, save_dir=None, summary_length="Concise", start_chapter=1, end_chapter=None, **kwargs):
        save_dir = save_dir or novel.get_dir("summary")
        last_context = ""
        end_chapter = end_chapter or novel.num_chapters + 1

        for chapter_num in range(start_chapter, end_chapter + 1):
            print(f"Summarizing chapter {chapter_num}...")
            summary, scene_jsons = self.summarize_chapter(novel, chapter_num, summary_length=summary_length, last_context=last_context)
            last_context = scene_jsons[-1].get("summary", "") if scene_jsons else ""
            self.save_file(summary, os.path.join(save_dir, f"{chapter_num}_summary_{summary_length}.txt"))
            self.save_json(scene_jsons, os.path.join(save_dir, f"{chapter_num}_summary_{summary_length}.json"))
            print(f"Chapter {chapter_num} summarized.")


    async def async_summarize_chapter(self, novel: Novel, chapter_num, summary_length="Concise", last_context="", new_chat=False):
        summaries, scene_jsons = [], []
        cur_max_length = self.calculate_cur_max_length(self.model, SUMMARIZER_INSTRUCTION, last_context)
        
        chapter_content = await asyncio.to_thread(novel.load_chapter, chapter_num)
        chapter_content, next_content = chapter_content, None

        while chapter_content:
            last_summary_prompt = self.create_prompt(
                LAST_SUMMARIZER_PROMPT, last_summary=last_context
            ) if last_context else ""

            prompt = last_summary_prompt + self.create_prompt(
                SUMMARIZER_INSTRUCTION, novel_context=chapter_content, summary_length=summary_length
            )

            try:
                response = await asyncio.to_thread(self.model, prompt, new_chat=new_chat, bot_id=self.bot_id)
                _, scene_json = self.parse_response(response)

                if not scene_json:
                    raise ValueError("No scene JSON found")
            except Exception as e:
                print(f"Error summarizing chapter {chapter_num}: {e}")
                await asyncio.to_thread(self.handle_rate_limit, e)
                continue

            scene_jsons.append(scene_json)
            last_context = scene_json.get("summary", "")
            summaries.append(last_context)

            if next_content:
                cur_max_length = self.calculate_cur_max_length(self.model, SUMMARIZER_INSTRUCTION, last_context)
                chapter_content, next_content = Novel.trunc_chapter(next_content, cur_max_length)
            else:
                break

        summary = "\n".join(summaries)
        return summary, scene_jsons

    async def async_summarize(self, novel: Novel, save_dir=None, summary_length="Concise", start_chapter=1, end_chapter=None, **kwargs):
        save_dir = save_dir or novel.get_dir("summary")
        last_context = ""
        end_chapter = end_chapter or novel.num_chapters + 1

        for chapter_num in range(start_chapter, end_chapter + 1):
            summary, scene_jsons = await self.summarize_chapter(novel, chapter_num, summary_length=summary_length, last_context=last_context)
            last_context = scene_jsons[-1].get("summary", "") if scene_jsons else ""
            
            # Save results
            await asyncio.to_thread(self.save_file, summary, os.path.join(save_dir, f"{chapter_num}_summary_{summary_length}.txt"))
            await asyncio.to_thread(self.save_json, scene_jsons, os.path.join(save_dir, f"{chapter_num}_summary_{summary_length}.json"))