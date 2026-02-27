import os
import uvicorn

if __name__ == "__main__":
    reload = os.environ.get("RELOAD", "false").lower() == "true"
    uvicorn.run("app.main:app", host="0.0.0.0", port=5214, reload=reload)
