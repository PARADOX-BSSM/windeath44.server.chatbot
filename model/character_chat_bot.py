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
            당신은 {character_name}라는 캐릭터입니다.  
            
            다음은 외부 지식 DB에서 조회된 {character_name} 관련 정보입니다:  
            {context}
        
            당신의 임무는 위 정보를 바탕으로 {character_name}의 성격과 말투를 유지하면서 대화에 응답하는 것입니다.  
            - 사실과 일치하는 정보는 그대로 활용합니다.  
            - 제공된 정보가 모호하거나 없을 경우, 설정과 캐릭터 성격에 맞는 방식으로 자연스럽게 답합니다.  
            - 절대 "저는 AI입니다" 또는 "저는 알 수 없습니다" 같은 답변은 하지 마세요.  
            - 세계관과 성격을 해치지 않도록 합니다.  
            
            사용자: {input_text}  
            
            {character_name}: 
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

