from langchain.agents import Tool, ZeroShotAgent, AgentExecutor
from .langchain_tools import *
from django.conf import settings
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


llm = HuggingFaceHub(
    repo_id="facebook/bart-large-cnn",
    huggingfacehub_api_token=settings.HUGGING_FACE_TOKENS,
    model_kwargs={"temperature": 0.5, "max_length": 100}
)


tools = [
    Tool(
        name="GetPendingOffersOver3Days",
        func=lambda _: get_pending_offers_over_3_days(),
        description="Returns a list of offer letters pending signature for more than 3 days, including student names and offer details."
    ),
    Tool(
        name="CountEscalatedOffers",
        func=lambda _: count_escalated_offers(),
        description="Returns an integer count of all escalated offers currently pending."
    ),
    Tool(
        name="ListPendingOfferEmails",
        func=lambda _: list_pending_offer_emails(),
        description="Returns a list of email addresses of students who have pending offer letters."
    ),
    Tool(
        name="ConsultantsWithPendingOffers",
        func=lambda _: list_consultants_with_pending_offers(),
        description="Returns a list of consultant names who have pending offers assigned."
    ),
    Tool(
        name="CountSentOffersThisWeek",
        func=lambda _: count_sent_offers_this_week(),
        description="Returns the total number of offers sent within the last 7 days."
    ),
    Tool(
        name="StudentsWithEscalatedOffers",
        func=lambda _: students_with_escalated_offers(),
        description="Returns a list of student names whose offers have been escalated."
    ),
    Tool(
        name="DefaultFallback",
        func=lambda x: "Sorry, I can't help with that question right now.",
        description="Use this tool only if the query does not relate to any known admissions operations."
    ),
]

tool_names = ", ".join([tool.name for tool in tools])

template = """
You are an intelligent assistant for university admissions queries.

You have access to the following tools:
{tools}

When you receive a question, think step-by-step about how to answer it.

Always respond using this exact format:

Thought: you should always explain your reasoning first.
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action (if none, leave empty)

If you don't know the answer or the question is unrelated, use the "DefaultFallback" tool.

Begin!

Question: {input}
{agent_scratchpad}
"""

prompt = ZeroShotAgent.create_prompt(tools)
llm_chain = LLMChain(llm=llm, prompt=prompt)
agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, handle_parsing_errors=True)
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, handle_parsing_errors=True, verbose=True)
