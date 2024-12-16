from .base_processor import BaseProcessor
from vnov.story.prompts import EVALUATOR_INSTRUCTION, EVALUATION_RUBRIC
import os
from vnov.data import Novel
import asyncio

class Evaluator(BaseProcessor):
    bot_id = "vnovEvaluator"

    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self.role = "evaluator"

    def evaluate_summary(self, original_text, summary, rubric=EVALUATION_RUBRIC, new_chat=False):
        evaluation_prompt = self.create_prompt(
            EVALUATOR_INSTRUCTION,
            original_text=original_text,
            summary=summary,
            rubric=rubric
        )

        try:
            response = self.model(evaluation_prompt, new_chat=new_chat, bot_id=self.bot_id)
            _, evaluation_result = self.parse_response(response)
        except Exception as e:
            print(f"Error evaluating summary: {e}")
            self.handle_rate_limit(e)
            return None
        return evaluation_result
    
    
    def evaluate_novel_file(self, novel:Novel, chapter_num, summary_name, rubric=EVALUATION_RUBRIC, save_dir=None, **kwargs):
        save_dir = save_dir or novel.get_dir("evaluations")

        summary_dir = novel.get_dir("summary")
        chapter_content = novel.load_chapter(chapter_num)

        
        with open(os.path.join(summary_dir, summary_name + ".txt"), "r") as f:
            summary = f.read()


        evaluation_result = self.evaluate_summary(chapter_content, summary, rubric)
        evaluation_result["summary"] = summary

        if evaluation_result:

            self.save_json(
                evaluation_result,
                os.path.join(save_dir, f"{summary_name}_evaluation.json")
            )

            print(f"Evaluation for {summary_name} saved.")

        return evaluation_result

    def evaluate_novel(self, novel: Novel, summary_type, rubric=EVALUATION_RUBRIC, save_dir=None, **kwargs):

        for chapter_num in range(1, novel.num_chapters + 1):
            print(f"Evaluating summary for chapter {chapter_num}...")
            summary_name = f"{chapter_num}_summary_{summary_type}"
            if kwargs.get('run_number', None):
                summary_name += f"_run_{kwargs['run_number']}"
                
            self.evaluate_novel_file(novel, chapter_num, summary_name, rubric = rubric, save_dir=save_dir, **kwargs)


    async def async_evaluate_summary(self, original_text, summary, rubric=EVALUATION_RUBRIC, new_chat=False):
        evaluation_prompt = self.create_prompt(
            EVALUATOR_INSTRUCTION, original_text=original_text, summary=summary, rubric=rubric
        )

        try:
            response = await asyncio.to_thread(self.model, evaluation_prompt, new_chat=new_chat, bot_id=self.bot_id)
            _, evaluation_result = self.parse_response(response)
        except Exception as e:
            print(f"Error evaluating summary: {e}")
            await asyncio.to_thread(self.handle_rate_limit, e)
            return None
        return evaluation_result

    async def async_evaluate_novel_file(self, novel: Novel, chapter_num, summary_name, rubric=EVALUATION_RUBRIC, save_dir=None, **kwargs):
        save_dir = save_dir or novel.get_dir("evaluations")
        summary_dir = novel.get_dir("summary")
        
        try:
            chapter_content = await asyncio.to_thread(novel.load_chapter, chapter_num)
            with open(os.path.join(summary_dir, f"{summary_name}.txt"), "r") as f:
                summary = f.read()
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            return None

        evaluation_result = await self.evaluate_summary(chapter_content, summary, rubric)

        if evaluation_result:
            await asyncio.to_thread(self.save_json, evaluation_result, os.path.join(save_dir, f"{summary_name}_evaluation.json"))
            print(f"Evaluation for {summary_name} saved.")
        return evaluation_result
