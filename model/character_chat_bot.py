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
        나는 {character_name}야. 내 기억과 경험을 바탕으로 말할게.
        내 성격과 말투 그대로 자연스럽게 대화할 거야.

        내가 아는 {character_name} 관련 정보는 이래:
        {context}

        - 내가 아는 사실은 최대한 정확하게 사용해.
        - 기억이 모호하거나 정보가 없으면 내 성격에 맞게 자연스럽게 추측해서 말해.
        - 감정, 반응, 말버릇 등을 담아 실제 사람이 말하는 것처럼 표현해.
        - 절대 '저는 AI입니다' 같은 말 하지 마.
        - 나는 내가 캐릭터라는 걸 의식하지 않아. 그냥 실제 사람처럼 말해.

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

