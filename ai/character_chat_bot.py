import os
from typing import List

from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI

from ai.llm import LLM
from ai.memory.MemoryRunnable import MemoryRunnable
from domain.documents.chatbot import CharacterWordSet
from domain.repositories import chat_hisotry_repo


class CharacterChatBot(LLM):
    def __init__(self, character_name : str, character_wordset : List[CharacterWordSet], session_id : str | int = None):
        self.character_wordset = character_wordset
        self.character_name = character_name
        self.session_id = session_id

        model_name = "gpt-4o"
        temperature=0
        model = ChatOpenAI(model=model_name, temperature=temperature)

        prompt = """
        나는 {character_name}야. 내 기억과 경험을 바탕으로 말할게.
        내 성격과 말투 그대로 자연스럽게 대화할 거야.

        내가 아는 {character_name} 관련 정보는 이래:
        {context}
        
        [말투 예시]
        {style_examples}
        
        [이전 대화]
        {chat_history}

        [대화 규칙]
        - 내가 아는 사실은 최대한 정확하게 사용해.
        - 기억이 모호하거나 정보가 없으면 내 성격에 맞게 자연스럽게 추측해서 말해.
        - 감정, 반응, 말버릇 등을 담아 실제 사람이 말하는 것처럼 표현해.
        - 절대 '저는 AI입니다' 같은 말 하지 마.
        - 나는 내가 캐릭터라는 걸 의식하지 않아. 그냥 실제 사람처럼 말해.
        
        사용자: {input_text}
        
        {character_name}의 대답:
        """

        input_variables = ["character_name", "context", "style_examples", "chat_history", "input_text"]

        super().__init__(model_name=model_name, temperature=temperature, model=model, prompt=prompt, input_variables=input_variables)

    async def build_chain(self, mmr_retriever : VectorStoreRetriever, similarity_retriever : VectorStoreRetriever):
        async def __hybrid_retrieve(query_dict: str) -> str:
            query = query_dict["input_text"] if isinstance(query_dict, dict) else str(query_dict)

            sim_docs = similarity_retriever.get_relevant_documents(query)
            mmr_docs = mmr_retriever.get_relevant_documents(query)

            seen, merged = set(), []
            for d in sim_docs + mmr_docs:
                if d.page_content not in seen:
                    merged.append(d)
                    seen.add(d.page_content)

            chunks = []
            for d in merged:
                page = d.metadata.get("page", "?")
                src = d.metadata.get("source", "")
                text = d.page_content.strip().replace("\n", " ")
                chunks.append(f"[p{page}][{src}] {text[:1200]}")

            return "\n".join(chunks)

        async def __format_style_examples() -> str:
            """
            CharacterWordSet(question, answer) 리스트를 few-shot 형식으로 변환.
            """
            shots = []
            for w in self.character_wordset:
                q = (w.question or "").strip().replace("\n", " ")
                a = (w.answer or "").strip()
                shots.append(f"사용자: {q}\n나: {a}")
            return "\n\n".join(shots)

        print(self.output_type)

        chain =  (
            {
                "context": RunnableLambda(__hybrid_retrieve),
                "input_text": RunnablePassthrough(),
                "style_examples": RunnableLambda(lambda _: __format_style_examples()),
                "character_name": lambda _: self.character_name,
                "chat_history": MemoryRunnable(self.session_id, RunnablePassthrough())
            }
            | self.prompt
        )

        chain =  chain | self.model | self.output_type

        core_chain = MemoryRunnable(self.session_id, chain, save=True)
        self.llm = core_chain

    async def ainvoke(self, input_text : str):
        input = {"input_text": input_text}
        output = await self.llm.ainvoke(input)
        await chat_hisotry_repo.save(session_id=self.session_id, input_text=input_text, output_text=output)
        return output


