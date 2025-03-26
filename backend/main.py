from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chatbot import SupplyChainChatbot

app = FastAPI()

# Initialize the chatbot
chatbot = SupplyChainChatbot()

class QueryRequest(BaseModel):
    query: str

@app.post("/query/")
async def handle_query(request: QueryRequest):
    try:
        # Process the user query
        response = chatbot.handle_query(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Supply Chain Chatbot is running!"}