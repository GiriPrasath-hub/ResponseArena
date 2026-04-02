from fastapi import FastAPI
from openenv.environment import OpenEnvWrapper
from fastapi.responses import JSONResponse

app = FastAPI()
env = OpenEnvWrapper()

@app.get("/")
def health():
    return JSONResponse(content={"status": "running"})

@app.post("/reset")
def reset():
    return env.reset()

@app.post("/step")
def step(action: dict):
    return env.step(action)

@app.get("/state")
def state():
    return env.state()


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()