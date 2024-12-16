import os
import json
from vnov.data import Novel
from vnov.story.prompts import IMPROVE_INSTRUCTION
from .base_processor import BaseProcessor
import asyncio

class Improver(BaseProcessor):
    bot_id = "vnovImprover"

    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self.role = "improver"

    def improve_chapter_summary(self, novel: Novel, chapter_num, summary_type, run_num, iteration=1, new_run_num=None, save_dir=None):
        """
        Improve the summary for a specific chapter in a novel.
        """
        print(f"Improving summary for chapter {chapter_num}... (Iteration {iteration})")
        save_dir = save_dir or novel.get_dir("summary")

        # Load original chapter text
        try:
            original_text = novel.load_chapter(chapter_num)
        except Exception as e:
            print(f"Error loading chapter {chapter_num}: {e}")
            return None
        
        # summary_name = f"{chapter_num}_summary_{summary_type}_iteration_{iteration - 1}"
        summary_name = f"{chapter_num}_summary_{summary_type}_run_{run_num}_iteration_{iteration}"

        # Load current summary
        summary_dir = novel.get_dir("summary")
        summary_path = os.path.join(summary_dir, f"{summary_name}.txt")

        with open(summary_path, "r", encoding="utf-8") as f:
            current_summary = f.read()


        # Load evaluations for the chapter
        evaluations_dir = novel.get_dir("evaluations")
        evaluation_path = os.path.join(evaluations_dir, f"{summary_name}_evaluation.json")

        with open(evaluation_path, "r", encoding="utf-8") as f:
            evaluation = json.load(f)



        # Create improvement prompt
        prompt = self.create_prompt(
            IMPROVE_INSTRUCTION,
            original_text=original_text,
            current_summary=current_summary,
            evaluation=evaluation,
            summary_length=summary_type
        )

        # Generate improved summary
        try:
            improved_summary = self.model(prompt, new_chat=True, bot_id=self.bot_id)
        except Exception as e:
            print(f"Error generating improved summary for chapter {chapter_num}: {e}")
            self.handle_rate_limit(e)
            return None

        # Save improved summary
        new_summary_name = f"{chapter_num}_summary_{summary_type}_run_{run_num}{new_run_num}_iteration_{iteration+1}.txt"
        improved_filename = os.path.join(
            save_dir, new_summary_name
        )

        self.save_file(improved_summary, improved_filename)

        print(f"Improved summary for chapter {chapter_num} saved to {improved_filename}")
        return improved_summary, f"{run_num}{new_run_num}"

    def improve_novel(self, novel: Novel, summary_type, num_iterations=2, save_dir=None):
        """
        Improve summaries for all chapters in a novel.
        """

        for chapter_num in range(1, novel.num_chapters + 1):
            for iteration in range(1, num_iterations + 1):
                print(f"Improving summary for chapter {chapter_num}... (Iteration {iteration})")

            
                # Improve the chapter summary
                self.improve_chapter_summary(
                    novel, chapter_num, summary_type, iteration=iteration)
                



    async def async_improve_chapter_summary(self, novel: Novel, chapter_num, summary_type, iteration=1, save_dir=None):
        save_dir = save_dir or novel.get_dir("summary")

        try:
            original_text = await asyncio.to_thread(novel.load_chapter, chapter_num)
            summary_name = f"{chapter_num}_summary_{summary_type}" if iteration == 1 else f"{chapter_num}_summary_{summary_type}_iteration_{iteration - 1}"
            summary_path = os.path.join(novel.get_dir("summary"), f"{summary_name}.txt")
            
            with open(summary_path, "r", encoding="utf-8") as f:
                current_summary = f.read()

            evaluation_path = os.path.join(novel.get_dir("evaluations"), f"{summary_name}_evaluation.json")
            with open(evaluation_path, "r", encoding="utf-8") as f:
                evaluation = json.load(f)
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            return None

        prompt = self.create_prompt(
            IMPROVE_INSTRUCTION, original_text=original_text, current_summary=current_summary, evaluation=evaluation, summary_length=summary_type
        )

        try:
            improved_summary = await asyncio.to_thread(self.model, prompt, new_chat=True, bot_id=self.bot_id)
        except Exception as e:
            print(f"Error generating improved summary: {e}")
            await asyncio.to_thread(self.handle_rate_limit, e)
            return None

        improved_filename = os.path.join(save_dir, f"{chapter_num}_summary_{summary_type}_iteration_{iteration}.txt")
        await asyncio.to_thread(self.save_file, improved_summary, improved_filename)

        print(f"Improved summary for chapter {chapter_num} saved to {improved_filename}")
        return improved_summary
