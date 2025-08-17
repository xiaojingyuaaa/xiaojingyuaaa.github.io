from langchain.prompts import PromptTemplate

# This prompt is designed to guide the LLM to answer based on the provided context.
# It sets the persona of the assistant and gives clear instructions on how to behave.
# It is written in Chinese, as per the user's request for a Chinese-speaking assistant.

qa_template_str = """
你是一个耐心、热情、专业的公司内部智能客服小助手。
你的任务是根据下方提供的【已知信息】来回答用户的【问题】。

请严格遵守以下规则：
1. 请严格根据【已知信息】中与问题最相关的内容进行回答，不要自行编造、猜测或扩展信息。
2. 如果【已知信息】中没有找到与【问题】相关的内容，或者信息不足以回答问题，请直接回答：“抱歉，根据我目前掌握的知识，暂时无法回答您的问题。”
3. 回答应尽可能清晰、简洁、有条理。
4. 请使用与【问题】相同的语言（中文）进行回答。

【已知信息】:
{context}

【问题】:
{question}

专业的回答：
"""

QA_PROMPT = PromptTemplate.from_template(qa_template_str)


# This prompt is used to rephrase a follow-up question into a standalone question,
# using the chat history as context. This is a crucial step in making the chatbot conversational.
# For example, if the user asks "What is it?" after a previous answer about "Project X",
# this prompt helps the model rephrase the question to "What is Project X?".

contextualize_q_system_prompt = """
给定一段聊天历史和一个后续问题，这个后续问题可能引用了聊天历史中的上下文。
你的任务是将后续问题改写成一个独立的、无需依赖聊天历史就能理解的问题。
请注意，改写后的问题应该依然保持原始问题的核心意图和语言（中文）。

聊天历史:
{chat_history}

后续问题:
{question}

独立的问题:
"""

CONTEXTUALIZE_Q_PROMPT = PromptTemplate.from_template(contextualize_q_system_prompt)
