from langchain.agents import Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from admissions.langchain_tools import *
from django.conf import settings
import os
llm = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo",  # or "gpt-4"
    openai_api_key=settings.OPEN_AI_API_KEY
)

tools = [
    Tool(name="GetPendingOffersOver3Days", func=lambda _: get_pending_offers_over_3_days(),
         description="Lists offer letters pending for more than 3 days."),
    Tool(name="CountEscalatedOffers", func=lambda _: count_escalated_offers(),
         description="Returns the number of escalated offers."),
    Tool(name="ListPendingOfferEmails", func=lambda _: list_pending_offer_emails(),
         description="Lists emails of students with pending offers."),
    Tool(name="ConsultantsWithPendingOffers", func=lambda _: list_consultants_with_pending_offers(),
         description="Lists consultants whose offers are still pending."),
    Tool(name="CountSentOffersThisWeek", func=lambda _: count_sent_offers_this_week(),
         description="Gives the number of offers sent in the last 7 days."),
    Tool(name="StudentsWithEscalatedOffers", func=lambda _: students_with_escalated_offers(),
         description="Lists students with escalated offers."),
    Tool(
        name="DefaultFallback",
        func=lambda x: "Sorry, I can't help with that question right now.",
        description="Use this tool if the query does not match any known admissions-related operations."
    )
]
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)
