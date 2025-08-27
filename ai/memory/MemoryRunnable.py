import os

from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables import Runnable
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

class MemoryRunnable(Runnable):
    def __init__(self, session_id: str, runnable: Runnable, save : bool = False):
        self.runnable = runnable
        self.memory = None
        self.save = save
        self.session_id = session_id
        if session_id:
            model = "gpt-3.5-turbo"
            summary_llm = ChatOpenAI(model=model, temperature=0)

            self.memory = ConversationSummaryBufferMemory(
            memory_key="chat_history",
            chat_memory=RedisChatMessageHistory(
                session_id=str(session_id),
                url=os.getenv("REDIS_URL", "redis://localhost:6379"),
                ttl=60 * 60 * 24,
            ),
            return_messages=True,
            max_token_limit=500,
            llm=summary_llm
        )

    def _format_chat_history(self, messages):
        if not messages: return ""
        return "\n".join(
            f"사용자: {m.content}" if m.type == "human" else f"나: {m.content}"
            for m in messages
        )

    def invoke(self, input_dict, config=None):
        chat_history = ""
        if self.memory:
            raw_history = self.memory.load_memory_variables({})["chat_history"]
            if raw_history:
                chat_history = (
                    self._format_chat_history(raw_history)
                    if isinstance(raw_history, list)
                    else raw_history
                )

        merged_input = {**input_dict, "chat_history": str(chat_history)}
        output = self.runnable.invoke(merged_input, config)
        if self.memory and self.save:
            self.memory.save_context(
                {"input_text": merged_input["input_text"]},
                {"output_text": output}
            )
        return output

    async def ainvoke(self, input_dict, config=None):
        chat_history = ""
        if self.memory:
            raw_history = self.memory.load_memory_variables({})["chat_history"]
            if raw_history:
                chat_history = self._format_chat_history(raw_history) if isinstance(raw_history, list) else raw_history

        merged_input = {**input_dict, "chat_history": str(chat_history)}
        output = await self.runnable.ainvoke(merged_input, config)
        if self.memory and self.save:
            self.memory.save_context(
                {"input_text": merged_input["input_text"]},
                {"output_text": output}
            )
        return output
