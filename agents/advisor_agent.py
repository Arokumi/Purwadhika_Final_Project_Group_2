import os
import operator
from typing import List, Dict, Annotated, Any
from datetime import datetime
from dotenv import load_dotenv

# LangChain / LangGraph Imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain.agents import create_agent
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models

load_dotenv()
QDRANT_URL = os.getenv("QDRANT_ENDPOINT")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)


vector_store = QdrantVectorStore.from_existing_collection(
    collection_name="uploaded_cvs",
    embedding=embeddings,
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

client = vector_store.client

client.create_payload_index(
    collection_name="uploaded_cvs",
    field_name="metadata.session_id",
    field_schema=models.PayloadSchemaType.KEYWORD,
    wait=True
)

# Tool to retrieve user data
@tool
def review_user_cv(session_id: str) -> str:
    """
    Retrieves the user's CV(s) from the database using their session_id.
    Returns the CV summaries and contents.
    """

    print("---- retrieving user CV for advisor chatbot")

    try:
        points, _ = client.scroll(
            collection_name="uploaded_cvs",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.session_id",
                        match=models.MatchValue(value=session_id)
                    )
                ]
            ),
            limit=10,  # Assumption: User won't have more than 10 CVs uploaded in one session
            with_payload=True
        )

        if not points:
            print("No CVs found for this session ID.")
            return "No CVs found for this session ID."

        # Sort by creation time (descending) -> Newest first
        sorted_points = sorted(
            points, 
            key=lambda x: x.payload.get("metadata", {}).get("created", 0), 
            reverse=True
        )

        results = []
        for i, point in enumerate(sorted_points):
            payload = point.payload
            metadata = payload.get("metadata", {})
            created_ts = metadata.get("created", 0)
            date_str = datetime.fromtimestamp(created_ts).strftime('%Y-%m-%d %H:%M:%S')
            
            summary = payload.get("page_content", "No summary available.")
            full_contents = metadata.get("cv_contents", "No detailed contents available.")

            label = "MOST RECENT CV" if i == 0 else f"OLDER CV (Uploaded: {date_str})"
            
            entry = (
                f"=== {label} ===\n"
                f"Date Uploaded: {date_str}\n"
                f"Summary: {summary}\n"
                f"Full Content Snippet: {full_contents}...\n"
                f"=======================\n"
            )
            results.append(entry)
            print(entry)

        return "\n".join(results)

    except Exception as e:
        print(f"Error retrieving CV: {str(e)}")
        return f"Error retrieving CV: {str(e)}"



# ======================================= Agent =======================================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=OPENAI_API_KEY)

advisor_agent = create_agent(
    model=llm,
    tools=[review_user_cv],
    system_prompt=
    """You are a helpful Career Advisor. STRATEGY FOR CV DATA:
        1. You have a 'user_summary' in your context. Use this for general questions (e.g., "What is my experience level?", "Suggest a career path").
        2. However, if the user asks for a CRITIQUE, REWRITE, specific FEEDBACK, or formatting advice, the summary is NOT enough. 
        3. In those cases, you MUST call the 'review_user_cv' tool to fetch the raw, full text of the CV to ensure you don't miss details."""
)

# Endpoint Function revealed to fastAPI app
def invoke_advisor(messages: List[Dict[str, str]], session_id: str) -> Dict[str, Any]:
    
    system_instruction = SystemMessage(
        content=f"SYSTEM CONTEXT: The current session_id is '{session_id}'. When calling tools, you MUST use this specific session_id."
    )
    
    formatted_inputs = {"messages": [system_instruction] + messages}

    # Invoke the agent
    result = advisor_agent.invoke(formatted_inputs)
    
    # Extract the last message (the AI's response)
    last_message = result["messages"][-1]
    full_messages = result["messages"]
    
    # print("The following are the returned messages:\n\n")
    # for i, message in enumerate(full_messages):
    #     print(f"---- MESSAGE NUMERO {i} ----")
    #     print(message)
    #     print("")
    # print(full_messages)

    return {
        "response": last_message.content,
        "full_messages": full_messages # Return full history
    }