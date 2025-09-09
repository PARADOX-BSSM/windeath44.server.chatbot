from core.exceptions.business_exception import BusinessException


class UpsertPineconeFailedException(BusinessException):
    def __init__(self, namespace : str):
        self.message = f"upsert pinecone failed || namespace : {namespace}"
        self.status_code = 500
        super().__init__(self.message, self.status_code)