from abc import abstractmethod

class BaseLLM:
    max_length = 1000
    @abstractmethod
    def generate(self, context):
        pass

    @abstractmethod
    def token_length(self, context):
        pass

    def __call__(self, context, **kwargs):
        return self.generate(context, **kwargs)