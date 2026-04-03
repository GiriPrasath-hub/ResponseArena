from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from openenv.environment import OpenEnvWrapper

app = FastAPI()
env = OpenEnvWrapper()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LOVE vH Environment</title>
    </head>
    <body>
        <h1>LOVE vH Environment ✅</h1>

        <button onclick="resetEnv()">Reset</button>
        <button onclick="getState()">Get State</button>

        <br><br>

        <input id="actionInput" placeholder='{"action": "your_action"}' size="40"/>
        <button onclick="stepEnv()">Step</button>

        <pre id="output"></pre>

        <script>
            async function resetEnv() {
                const res = await fetch('/reset', {method: 'POST'});
                const data = await res.json();
                document.getElementById('output').innerText = JSON.stringify(data, null, 2);
            }

            async function getState() {
                const res = await fetch('/state');
                const data = await res.json();
                document.getElementById('output').innerText = JSON.stringify(data, null, 2);
            }

            async function stepEnv() {
                const input = document.getElementById('actionInput').value;
                const res = await fetch('/step', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: input
                });
                const data = await res.json();
                document.getElementById('output').innerText = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """

@app.post("/reset")
def reset():
    return env.reset()

@app.post("/step")
def step(action: dict):
    return env.step(action)

@app.get("/state")
def state():
    return env.state()