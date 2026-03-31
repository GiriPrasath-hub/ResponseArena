from flask import Flask, request, jsonify, render_template

from environment.env import LoveEnv
from agent.agent import LoveAgent
from reward.reward_system import RewardSystem

#  CREATE APP FIRST
app = Flask(__name__, template_folder="templates")

#  INIT SYSTEM
env = None
agent = None
reward_system = None
state = None


#  HOME ROUTE
@app.route("/", methods=["GET"])
def home():
    print(" HOME ROUTE HIT ")
    return """
    <h2>LOVE vH Assistant</h2>
    <input id='msg' placeholder='Type message'/>
    <button onclick='send()'>Send</button>
    <pre id='out'></pre>

    <script>
    async function send(){
        let msg = document.getElementById('msg').value;
        let res = await fetch('/chat',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({message:msg})
        });
        let data = await res.json();
        document.getElementById('out').innerText = JSON.stringify(data,null,2);
        }
    </script>
    """


#  CHAT ROUTE
@app.route("/chat", methods=["POST"])
def chat():
    global state, env, agent, reward_system

    # Lazy init (VERY IMPORTANT)
    if env is None:
        print("🔥 Initializing system...")
        env = LoveEnv()
        agent = LoveAgent()
        reward_system = RewardSystem()
        state = env.reset()

    user_input = request.json.get("message", "")
    state["user_message"] = user_input

    action = agent.act(state)
    next_state, reward, done, info = env.step(action)

    state = next_state

    return jsonify({
        "response": action["response"],
        "reward": reward,
        "done": done
    })