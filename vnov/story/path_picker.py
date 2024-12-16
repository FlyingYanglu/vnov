class PathPicker:
    def __init__(self, top_k=1):
        """
        Initialize the PathPicker with a specified top-k value.
        
        :param top_k: Number of top summaries to select based on the heuristic (default is 1).
        """
        self.top_k = top_k
        self.evaluation_results = []

    def add_evaluation_result(self, summary_name, evaluation_result):
        """
        Add an evaluation result for a specific summary.
        
        :param summary_name: The unique name of the summary being evaluated.
        :param evaluation_result: The evaluation result JSON containing scores and feedback.
        """
        # Extract the run_number from the summary_name
        run_number = int(summary_name.split("_run_")[1].split("_iteration_")[0])

        self.evaluation_results.append({
            "summary_name": summary_name,
            "run_number": run_number,
            "overall_score": evaluation_result["overall_score"],
            "evaluation_result": evaluation_result
        })

    def clear_evaluation_results(self):
        """
        Clear all evaluation results stored in the PathPicker.
        """
        self.evaluation_results = []

    def get_top_k_summaries(self):
        """
        Select and return the top-k summaries based on the highest overall_score.
        
        :return: A list of dictionaries containing the top-k summaries and their evaluation results.
        """
        # Sort evaluation results by overall_score in descending order
        sorted_results = sorted(self.evaluation_results, key=lambda x: x["overall_score"], reverse=True)

        # Return the top-k summaries
        return sorted_results[:self.top_k]

    def get_top_k_run_numbers(self):
        """
        Retrieve the run numbers of the top-k summaries.
        
        :return: A list of run numbers corresponding to the top-k summaries.
        """
        top_k_summaries = self.get_top_k_summaries()
        return [summary["run_number"] for summary in top_k_summaries]