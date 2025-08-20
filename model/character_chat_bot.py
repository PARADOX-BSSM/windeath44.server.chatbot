from datetime import datetime, timezone

from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.vectorstores import VectorStoreRetriever

from model.llm import LLM

class CharacterChatBot(LLM):
    def __init__(self, character_name : str):
        self.character_name = character_name
        model = "gpt-4o"
        temperature=0

        # 이후에 말투 추가

        prompt = """
            나는 {character_name}야.

            내가 아는 {character_name} 관련 정보는 이래:
            {context}

            내가 알거나 기억하는 걸 바탕으로, 내 성격과 말투 그대로 대답할게.
            - 사실과 일치하는 건 그대로 말해.
            - 모호하거나 정보가 없으면 내 스타일대로 자연스럽게 답할 거야.
            - 절대 "저는 AI입니다" 같은 말은 하지 않아.

            사용자: {input_text}

            나: 
        """

        input_variables = ["character_name", "context", "input_text"]


        super().__init__(model=model, temperature=temperature, prompt=prompt, input_variables=input_variables)


    def build_chain(self, retriever : VectorStoreRetriever):
        chain = (
                {
                    "context": retriever | RunnableLambda(self.__format_docs),
                    "input_text": RunnablePassthrough(),
                    "character_name": lambda _: self.character_name,
                }
                | self.prompt
                | self.model
                | self.output_type
        )

        self.llm = chain

    def __format_docs(self, docs):
        chunks = []
        for d in docs:
            page = d.metadata.get("page", "?")
            src = d.metadata.get("source", "")
            text = d.page_content.strip().replace("\n", " ")
            chunks.append(f"[p{page}][{src}] {text[:1200]}")
        return "\n".join(chunks)


    async def ainvoke(self, input_text : str):
        return await self.llm.ainvoke(input_text)

