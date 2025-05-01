# src/llm_setup.py

from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from tools import get_query_tool, update_score_tool, enroll_student_tool

class ManualAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        # map tool name → callable
        self.tools = {t.metadata.name: t for t in tools}
        self.chat_history = []

    def chat(self, user_message: str) -> str:
        # 1) add user message
        self.chat_history.append(ChatMessage(role="user", content=user_message))

        # 2) ask LLM (with tools enabled)
        resp = self.llm.chat_with_tools(
            list(self.tools.values()),
            chat_history=self.chat_history
        )
        tool_calls = self.llm.get_tool_calls_from_response(resp,
                                                           error_on_no_tool_call=False)

        # 3) if there are tool calls, execute them
        while tool_calls:
            # push the LLM’s tool‐invocation message into history
            self.chat_history.append(resp.message)
            for call in tool_calls:
                fn = self.tools.get(call.tool_name)
                if not fn:
                    # unknown tool name
                    self.chat_history.append(
                        ChatMessage(role="tool",
                                    content=f"[Error] no tool named {call.tool_name}")
                    )
                    continue
                # run the tool
                output = fn(**call.tool_kwargs)
                self.chat_history.append(
                    ChatMessage(role="tool",
                                content=str(output),
                                additional_kwargs={"tool_call_id": call.tool_id})
                )
            # ask the LLM again, with updated history
            resp = self.llm.chat_with_tools(
                list(self.tools.values()),
                chat_history=self.chat_history
            )
            tool_calls = self.llm.get_tool_calls_from_response(
                resp, error_on_no_tool_call=False
            )

        # 4) final assistant message
        self.chat_history.append(resp.message)
        return resp.message.content


def get_chat_engine():
    # choose your cheaper model here
    llm = OpenAI(model="gpt-3.5-turbo", temperature=0.2, max_tokens=1024)

    tools = [
        get_query_tool(),     # your SQL‐to‐text query engine
        update_score_tool,    # updates a student’s score
        enroll_student_tool,  # enrolls a student
    ]

    # wrap in our ManualAgent
    agent = ManualAgent(llm, tools)

    # memory is optional, but shows how to keep a buffer
    _ = ChatMemoryBuffer.from_defaults(token_limit=2000)

    # **We return the agent directly** (no ContextChatEngine)
    return agent
