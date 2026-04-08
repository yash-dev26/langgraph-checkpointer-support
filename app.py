from graph import create_graph_chat
from dotenv import load_dotenv
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import Command
load_dotenv()
import os

MONGODB_URI = os.getenv("MONGODB_URI")
THREAD_ID = os.getenv("THREAD_ID", "8")

def connect_to_mongodb():
    if MONGODB_URI is None:
        raise ValueError("MONGODB_URI is not set in the environment variables.")
    return MongoDBSaver.from_conn_string(MONGODB_URI)


def init():
    thread_id = THREAD_ID

    try:
        with connect_to_mongodb() as checkpointer:
            print("Successfully connected to MongoDB.")
            graph_with_mongo = create_graph_chat(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": thread_id}}

            while True:
                state = graph_with_mongo.get_state(config)
                interrupts = getattr(state, "interrupts", ())

                
                if interrupts:

                    print("Your request is being handled by support. Please wait...")
                    continue

                user_input = input("> ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                for chunk in graph_with_mongo.stream(
                    {"messages": [{"role": "user", "content": user_input}]},
                    config=config,
                    stream_mode="values",
                ):
                    if "messages" in chunk:
                        chunk["messages"][-1].pretty_print()
    except Exception as e:
        raise ValueError(f"Failed to connect to MongoDB during initialization: {e}")


if __name__ == "__main__":
    init()