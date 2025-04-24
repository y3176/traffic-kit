

import logging
import base.logs
logger = logging.getLogger(__name__)


from fastapi import FastAPI
from fastapi.responses import FileResponse 
from fastapi.staticfiles import StaticFiles 


app = FastAPI()


from api.web import router as api_router
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=FileResponse)
async def read_index():
    return FileResponse("static/demo2/index.html")

app.mount("/", StaticFiles(directory="static/demo2/"), name="static")

if __name__ == "__main__":  
    host="0.0.0.0"
    port=8008
    import webbrowser
    webbrowser.open(f"http://127.0.0.1:{port}/")
    import uvicorn 
    uvicorn.run(app, host=host, port=port)

