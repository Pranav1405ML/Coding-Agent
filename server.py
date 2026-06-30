from fastapi import FastAPI
from pydantic import BaseModel
from agent.chat import send_message
from database import init_db, save_message, load_history

app = FastAPI()

all_histories = {}

class ChatRequest(BaseModel):
    user_id : str
    message : str

@app.post("/chat")
def chat(request : ChatRequest):
    init_db()
    history = load_history(request.user_id)
    old_hist_length = len(history)
    response_text, updated_history = send_message(history, request.message)

    for row in updated_history[old_hist_length : ]:
        role = row["role"]
        content = row["parts"]
        saved, trace = save_message(request.user_id, role, content)
        if not saved:
            return {"response": response_text, "Error": trace}

    return {"response": response_text}