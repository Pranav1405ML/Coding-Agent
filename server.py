from fastapi import FastAPI
from pydantic import BaseModel
from agent.chat import send_message

app = FastAPI()

all_histories = {}

class ChatRequest(BaseModel):
    user_id : str
    message : str

@app.post("/chat")
def chat(request : ChatRequest):
    if request.user_id not in all_histories:
        all_histories[request.user_id] = []

    history = all_histories[request.user_id]
    response_text, updated_history = send_message(history, request.message)
    all_histories[request.user_id] = updated_history

    return {"response": response_text}