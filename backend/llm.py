from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

model=ChatGoogleGenerativeAI(model="gemini-2.5-flash")

prompt=PromptTemplate(
    template="""
You are an AI tutor.

Rewrite the following content clearly:
- Fix spacing and symbols
- Use proper sentences
- Keep the meaning exactly the same
- Make it readable for a student

Content = {topic}
    """,
    input_variables=['topic']
)

parser=StrOutputParser()

chain=prompt | model | parser 
