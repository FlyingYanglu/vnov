def calculate_cur_max_length(model, instruction_length, last_context_length):
    """Calculate the current maximum length for the content."""
    return model.max_length - instruction_length - last_context_length

# def create_prompt(template, context, summary_length):
#     """Create a summarization prompt."""
#     return template.format(novel_context=context, summary_length=summary_length)
