import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add ../live_tracking to sys.path

from fastapi import FastAPI
from tracker import track_all_stocks

app = FastAPI()

@app.get("/api/predictions")
def get_predictions():
    return track_all_stocks()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
