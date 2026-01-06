from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

# Agents
from agents.advisor_agent import invoke_advisor
from agents.document_agent import analysis_compile
from agents.search_agent import search_compile


from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import traceback
from livekit import api as livekit_api
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, '..', 'data', 'jobs_database.db')

conn = sqlite3.connect(db_path, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


# ==================================== CV ANALYZER AGENT ====================================
class CVRequest(BaseModel):
    summary: str
    cv_contents: str
    best_jobs: list[dict]
    file_bytes: str
    session_id: str
    assessment: str

@app.post("/analyze-cv")
def cv_analyzer(request: CVRequest):
    response = analysis_compile(request.model_dump())
    return response


# ==================================== JOB SEARCHER AGENT ====================================
class JobSearchRequest(BaseModel):
    query: str
    summary: str
    best_jobs: list[dict]
    messages: list

@app.post("/job-search")
def job_searcher(request: JobSearchRequest):
    response = search_compile(request.model_dump())
    return response



# ==================================== RETRIEVE JOB INFORMATION FROM VECTOR DB / DIRECT ANSWER ====================================
class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]
    session_id: str

@app.post("/invoke-advisor")
def ask_advisor(request: ChatRequest):
    try:
        # Parse Pydantic object
        result = invoke_advisor(
            messages=request.messages,
            session_id=request.session_id
        )

        final_message = result["response"]

        # The result["full_messages"] contains LangChain objects
        steps_log = []
        full_history_objects = result.get("full_messages", [])[:-1]

        # print("The following are the returned messages:\n\n")
        # for i, message in enumerate(reversed(full_history_objects)):
            # print(f"---- MESSAGE NUMERO {i} ----")
            # print(message)
            # print("")


        # Iterate using '.type'
        for msg in reversed(full_history_objects):
            # CASE A: The AI deciding to call a tool
            if isinstance(msg, AIMessage) and msg.tool_calls:
                tool_calls = getattr(msg, "tool_calls", [])
                for tool in tool_calls:
                    steps_log.append({
                        "type": "tool_call",
                        "tool": tool['name'],
                        "message": f"Consulting {tool['name']}..."
                    })

            # CASE B: The Tool returning data
            elif isinstance(msg, ToolMessage):
                content_str = str(msg.content)

                # Create a snippet for readability
                snippet = content_str[:150] + "..." if len(content_str) > 150 else content_str
                steps_log.append({
                    "type": "tool_result",
                    "tool": msg.name,
                    "message": f"Received data:\n{snippet}"
                })

            elif isinstance(msg, HumanMessage):
                break

        # reverse back the steps
        steps_log.reverse()

        # print("STEPS_LOGS ARE:")
        # for message in steps_log:
        #     print(message)

        print("The following are the tool calls (if any):")
        print(steps_log if not [] else "No tool calls were used.")
        return {
            "response": final_message,
            "steps": steps_log
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



# ======================================================= GET LIVEKIT TOKEN ===================================================
class TokenRequest(BaseModel):
    room_name: str
    participant_name: str

@app.post("/get-livekit-token")
async def get_livekit_token(req: TokenRequest):
    try:
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")

        if not api_key or not api_secret:
            raise HTTPException(status_code=500, detail="LiveKit credentials not set")

        grant = livekit_api.VideoGrants(
            room_join=True,
            room=req.room_name,
            can_publish=True,
            can_subscribe=True,
        )

        token = livekit_api.AccessToken(api_key, api_secret) \
            .with_identity(req.participant_name) \
            .with_name(req.participant_name) \
            .with_grants(grant) \
            .to_jwt()

        return {"token": token}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================================================== GET JOBS FROM SQL DB ===============================================

@app.get("/get-all-jobs")
async def get_all_jobs():
    
    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()
    return [
        {
            "job_title": row['job_title'],
            "company_name": row['company_name'],
            "location": row['clean_location'],
            "work_style": row['work_style'],
            "work_type": row['work_type'],
            "min_salary": row['min_salary'],
            "max_salary": row['max_salary'],
            "job_description": row['job_description']
        }
        for row in rows
    ]
    

   