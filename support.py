from graph import create_graph_chat, graph
from dotenv import load_dotenv
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import Command
load_dotenv()
import os
MONGODB_URI = os.getenv("MONGODB_URI")

def connect_to_mongodb():
    if MONGODB_URI is None:
        raise ValueError("MONGODB_URI is not set in the environment variables.")
    return MongoDBSaver.from_conn_string(MONGODB_URI)

def init():
    thread_id = "8"
    config = {"configurable": {"thread_id": thread_id}}

    try:
        with connect_to_mongodb() as checkpointer:
            print("Successfully connected to MongoDB.")
            graph_with_mongo = create_graph_chat(checkpointer=checkpointer)

            state = graph_with_mongo.get_state(config)
            interrupts = getattr(state, "interrupts", ())
            if not interrupts:
                print("No pending interrupt found for this thread.")
                return

            payload = getattr(interrupts[0], "value", {}) or {}
            prompt = payload.get("query") or payload.get("message") or "resolve the issue"
            ans = input(f"{prompt}\n> ")

            resume_command = Command(resume={"data": ans})
            for event in graph_with_mongo.stream(resume_command, config=config, stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()
    except Exception as e:
        raise ValueError(f"Failed to connect to MongoDB during initialization: {e}")
    


init()