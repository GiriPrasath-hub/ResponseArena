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

print(" Correct app loaded ")
#  HOME ROUTE
@app.route("/", methods=["GET"])
def home():
    print(" HOME ROUTE HIT ")
    return "Home Working"


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