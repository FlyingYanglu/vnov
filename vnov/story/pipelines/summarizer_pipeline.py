import asyncio
from vnov.story import Summarizer, Evaluator, Improver, PathPicker
from vnov.data import Novel

class PipelineProcessor:
    def __init__(self, summarizer:Summarizer, evaluator:Evaluator, improver:Improver, path_picker:PathPicker):
        self.summarizer = summarizer
        self.evaluator = evaluator
        self.improver = improver
        self.path_picker = path_picker

    async def process_chapter(self, novel, chapter_num, summary_type, num_span=3, num_iterations=2):
        


        for run_num in range(1, num_span + 1):
            print(f"Starting summarization for Chapter {chapter_num}")
            summary, scene_jsons = await asyncio.to_thread(
                self.summarizer.summarize_chapter, 
                novel, chapter_num, summary_type, "", new_chat=True, run_number=run_num, iteration_number=1
            )
            print(f"Completed summarization for Chapter {chapter_num}")

        summary_run_nums = list(range(1, num_span + 1))
        for iteration in range(1, num_iterations + 1):
            for run_num in summary_run_nums:
                last_summary_name = f"{chapter_num}_summary_{summary_type}_run_{run_num}_iteration_{iteration}"
                
                
                print(f"Evaluating and improving Chapter {chapter_num}, Iteration {iteration}")
                # Evaluate
                evaluation_result = await asyncio.to_thread(
                    self.evaluator.evaluate_novel_file,
                    novel, chapter_num, last_summary_name
                )

                # Add evaluation result to path picker
                self.path_picker.add_evaluation_result(last_summary_name, evaluation_result)
            
            # path picker do the job of selecting the top-k summaries

            top_k_run_numbers = self.path_picker.get_top_k_run_numbers()
            self.path_picker.clear_evaluation_results()

            summary_run_nums = []
            for run_num in top_k_run_numbers:
                # last_summary_name = f"{chapter_num}_summary_{summary_type}_run_{run_num}_iteration_{iteration}"
                for new_run_num in range(1, num_span + 1):
                    print(f"Improving Chapter {chapter_num}, Iteration {iteration}, Run {run_num}, New Run {new_run_num}")
                    # Improve
                    improved_summary, new_run_num = await asyncio.to_thread(
                        self.improver.improve_chapter_summary,
                        novel, chapter_num, summary_type, run_num, iteration, new_run_num
                    )
                    summary_run_nums.append(new_run_num)
                    print(f"Improved Chapter {chapter_num}, Iteration {iteration}, Run {run_num}, New Run {new_run_num}")

        for run_num in summary_run_nums:
            # Update summary name for the next iteration
            last_summary_name = f"{chapter_num}_summary_{summary_type}_run_{run_num}_iteration_{num_iterations+1}"
            print(f"Iteration {iteration} complete for Chapter {chapter_num}")

            # evaluate the final improved summary
            evaluation_result = await asyncio.to_thread(
                self.evaluator.evaluate_novel_file,
                novel, chapter_num, last_summary_name
            )

    async def run_pipeline(self, novel:Novel, summary_type="concise", num_span = 3, num_iterations=2, num_chapters = None):
        tasks = []
        num_chapters = num_chapters or novel.num_chapters
        for chapter_num in range(1, num_chapters + 1):
            tasks.append(
                self.process_chapter(novel, chapter_num, summary_type, num_span, num_iterations)
            )

        # Run all tasks concurrently
        await asyncio.gather(*tasks)

# Example Usage
# Instantiate the summarizer, evaluator, and improver with your respective classes
# summarizer = Summarizer(...)
# evaluator = Evaluator(...)
# improver = Improver(...)
# processor = PipelineProcessor(summarizer, evaluator, improver)

# asyncio.run(processor.run_pipeline(novel, summary_type="Concise", num_iterations=2))
