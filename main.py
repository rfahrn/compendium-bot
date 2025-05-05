from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import os
from dotenv import load_dotenv

from Tools_agent.compendium_tool import get_compendium_info
from Tools_agent.faiss_tool import search_faiss
from Tools_agent.openfda_tool import search_openfda
from Tools_agent.tavily_tool import smart_tavily_answer
from Tools_agent.alerts_tool import search_medication_alerts

load_dotenv()

app = FastAPI()

# Allow CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ideally restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question_type: str
    input_type: str
    medication_name: str

# Define tools
tools = [
    Tool(name="CompendiumTool", func=get_compendium_info, description="Medikamenteninfos von Compendium.ch"),
    Tool(name="FAISSRetrieverTool", func=search_faiss, description="Lokale medizinische FAISS-Datenbank"),
    Tool(name="OpenFDATool", func=search_openfda, description="OpenFDA-Datenbank"),
    Tool(name="TavilySearchTool", func=smart_tavily_answer, description="Websuche"),
    Tool(name="MedicationAlertsTool", func=search_medication_alerts, description="Medikamentenwarnungen"),
]

# LangChain agent setup
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    openai_api_key=os.getenv("OPENAI_KEY"),
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    agent_kwargs={
        "system_message": (
            "Du bist ein klinischer Assistent. Nutze Tools. "
            "Lies sorgfältig Antworten. Antworte auf Deutsch und präzise."
        ),
        "return_intermediate_steps": True,
        "max_iterations": 5,
    }
)

@app.post("/query")
async def query_agent(q: Query):
    prompt = f"{q.question_type} {q.medication_name}? ({q.input_type})"

    try:
        result = agent.invoke({"input": prompt}, return_only_outputs=False)

        # Prepare structured response
        final = result["output"]
        steps = []
        for step in result.get("intermediate_steps", []):
            thought = step[0].log
            tool = step[1].tool
            tool_input = step[1].tool_input
            tool_output = step[1].tool_response

            steps.append({
                "thought": thought,
                "tool": tool,
                "input": tool_input,
                "output": str(tool_output),
                "links": [w for w in str(tool_output).split() if w.startswith("http")]
            })

        return {"final_answer": final, "steps": steps}

    except Exception as e:
        return {"error": str(e)}