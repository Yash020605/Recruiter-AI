class InvalidDocumentError(Exception):
    def __init__(self, message: str):
        self.message = message

class DatabaseOperationError(Exception):
    def __init__(self, message: str):
        self.message = message

class LLMTimeoutError(Exception):
    def __init__(self, message: str):
        self.message = message
