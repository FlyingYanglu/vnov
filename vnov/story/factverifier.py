from transformers import BertForSequenceClassification, BertTokenizer, pipeline
import nltk

class FactCCVerifier:
    """
    A class to handle FactCC-based factual consistency verification for texts.
    """

    def __init__(self, model_path='manueldeprada/FactCC'):
        """
        Initialize the FactCCVerifier with the specified model and tokenizer.
        """
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model = BertForSequenceClassification.from_pretrained(model_path)
        self.pipeline = pipeline(model=model_path)

    def verify_summary(self, summary, reference_text):
        """
        Verifies the factual consistency of each sentence in the summary against the reference text.

        Args:
            summary (str): The summarized text to be verified.
            reference_text (str): The reference text against which the summary is verified.

        Returns:
            list of dict: Each dictionary contains a sentence, its label, and the score.
        """
        # Split the summary into individual sentences
        sentences = nltk.tokenize.sent_tokenize(summary)

        # Prepare input pairs for verification
        input_pairs = [[[sentence, reference_text]] for sentence in sentences]

        # Perform predictions
        results = self.pipeline(input_pairs, truncation='only_first', padding='max_length')

        # Combine sentences with results
        verification_results = [
            {
                "sentence": sentence,
                "label": result['label'],
                "score": result['score']
            }
            for sentence, result in zip(sentences, results)
        ]

        return verification_results

# Example usage
if __name__ == "__main__":
    # Define example texts
    text = '''Alice was beginning to get very tired of sitting by her sister...'''
    summary = '''Alice, a curious and imaginative girl, grows bored sitting by her sister...'''

    # Initialize the FactCC verifier
    verifier = FactCCVerifier()

    # Verify the summary against the original text
    results = verifier.verify_summary(summary, text)

    # Print the results
    for result in results:
        print(f"Sentence: {result['sentence']}\nLabel: {result['label']}\nScore: {result['score']:.4f}\n")
