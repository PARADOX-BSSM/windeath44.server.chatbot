from exception.business_exception import BaseException


class UpsertPineconeFailedException(BaseException):
    def __init__(self, namespace : str):
        self.message = f"upsert pinecone failed || namespace : {namespace}"
        self.status_code = 500
        super().__init__(self.message, self.status_code)