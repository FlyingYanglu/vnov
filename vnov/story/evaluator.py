from .base_processor import BaseProcessor
from vnov.data import Novel
import os

class Evaluator(BaseProcessor):

    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self.role = "evaluator"

    