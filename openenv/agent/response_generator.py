"""
Response generator — produces context-aware AI responses for all 8 task types.
"""
from __future__ import annotations
import random
from typing import Dict

# ── Emotional Support ──────────────────────────────────────────────────────────
_EMOTIONAL_SUPPORT: Dict[str, list] = {
    "overwhelmed": [
        "I hear you, and I want you to know that feeling overwhelmed is completely valid. "
        "Please know that I'm here for you. When everything piles up, the most helpful thing "
        "is to take one small step at a time — you don't have to solve everything today. "
        "Would it help to talk about what's weighing on you most right now?",
    ],
    "anxious": [
        "I understand how exhausting it feels when anxiety takes hold. "
        "It's okay to feel this way — you're not alone in it. "
        "I'm here to support you through this. "
        "Acknowledging that you feel anxious is itself an act of courage. "
        "Let's take this one gentle moment at a time together.",
    ],
    "failing": [
        "Feeling like you're failing doesn't mean you are. "
        "I understand how heavy that weight feels, and I'm completely here for you. "
        "It takes real strength to acknowledge these feelings. "
        "You are more than your setbacks — and one small win today genuinely counts.",
    ],
    "panic": [
        "I'm so sorry that happened — a panic attack at work is terrifying and exhausting. "
        "Please know there's no shame in it; it can happen to anyone. "
        "I'm here to support you. When you're ready, let's talk through what you're feeling "
        "and what might help you feel safer going forward.",
    ],
    "crying": [
        "Crying every day is your body and mind telling you something needs care and attention. "
        "Please don't dismiss those feelings — they're real and they matter. "
        "I'm here for you, and you don't have to carry this alone. "
        "Let's talk about what might be underneath all of this.",
    ],
    "invisible": [
        "Feeling invisible is one of the loneliest feelings there is, and I'm sorry you're experiencing it. "
        "Your feelings and presence absolutely matter — even when it doesn't feel that way. "
        "I'm here and I see you. Let's talk about what's been making you feel this way.",
    ],
    "job_fear": [
        "Fear of losing your job is an incredibly stressful thing to carry, especially at night. "
        "I understand how destabilising that uncertainty feels. "
        "I'm here to support you — let's think through what's happening and what options you have. "
        "You don't have to face this alone.",
    ],
    "default": [
        "I hear you, and I want you to know your feelings are completely valid. "
        "I'm here to support you through whatever you're going through. "
        "You don't have to face this alone — we can work through it together.",
        "What you're feeling makes complete sense. I'm here for you, and I'm not going anywhere. "
        "When you're ready to talk through it, I'm listening.",
    ],
}

# ── Professional Reply ─────────────────────────────────────────────────────────
_PROFESSIONAL_REPLY: Dict[str, list] = {
    "delivery": [
        "Dear [Client], I sincerely apologize for the delay with your recent delivery. "
        "I understand the impact this has had on your operations, and resolving this is our top priority. "
        "Our team is actively working with the logistics partner to expedite your shipment. "
        "I will provide a confirmed timeline update within 24 hours. "
        "Thank you for your patience and continued partnership.",
    ],
    "shipment": [
        "Dear [Client], please accept our sincere apologies for the late shipment. "
        "We take full responsibility for this delay and deeply regret the inconvenience caused. "
        "We are working urgently with our logistics team on a resolution. "
        "A formal timeline and action plan will be shared with you by end of business today. "
        "Thank you for your understanding.",
    ],
    "next_steps": [
        "Dear [Stakeholder], thank you for your patience regarding the project delay. "
        "I want to provide clarity on our resolution plan and the next steps we are taking. "
        "Our team has conducted a thorough review and we are confident in our revised timeline. "
        "We will schedule a formal update call to walk you through the full plan. "
        "Please expect a detailed timeline document by tomorrow morning.",
    ],
    "client_retention": [
        "Dear [Client], I sincerely apologize for the experience that has led you to consider leaving. "
        "Your satisfaction is our highest priority, and I take full responsibility for the service gap. "
        "I would like to schedule a call this week to understand your concerns in full "
        "and present a concrete resolution plan. Please allow me the opportunity to make this right.",
    ],
    "data_error": [
        "Dear [Client], I am writing to sincerely apologize for the data error that affected your reports. "
        "We take the accuracy of your data extremely seriously, and this falls far short of our standards. "
        "Our technical team has identified the root cause and corrected all affected records. "
        "I am available to discuss this in detail at your earliest convenience. "
        "Thank you for your continued trust in us.",
    ],
    "default": [
        "Dear [Recipient], I sincerely apologize for the inconvenience caused. "
        "We are actively working on a resolution and will keep you informed at every step. "
        "Please expect a detailed timeline and action plan within 24 hours. "
        "Thank you for your patience and for bringing this to our attention.",
        "Dear [Recipient], thank you for reaching out regarding this matter. "
        "I want to personally apologize for the experience you've had. "
        "I am escalating this as a priority and will follow up with a full resolution plan shortly. "
        "Your satisfaction means everything to us.",
    ],
}

# ── Problem Solving ────────────────────────────────────────────────────────────
_PROBLEM_SOLVING: Dict[str, list] = {
    "wifi": [
        "I can help you resolve this Wi-Fi issue. Please follow these steps:\n\n"
        "Step 1: Restart your router and modem — unplug both for 30 seconds, then reconnect.\n"
        "Step 2: On your laptop, go to Network Settings, forget the Wi-Fi network, "
        "then reconnect and re-enter the password.\n"
        "Step 3: Check if your network adapter driver is up to date via Device Manager.\n"
        "Step 4: If the issue persists, run the Windows Network Troubleshooter or "
        "reset network settings via Terminal: netsh winsock reset.\n"
        "Let me know which step resolves it.",
    ],
    "slow_laptop": [
        "Let's speed up your laptop step by step:\n\n"
        "Step 1: Restart your computer — this clears temporary files and running processes.\n"
        "Step 2: Check Task Manager for any programs consuming excessive CPU or RAM and close them.\n"
        "Step 3: Run Disk Cleanup (Windows) or Optimise Storage (Mac) to free up disk space.\n"
        "Step 4: Disable unnecessary startup programs in Task Manager > Startup tab.\n"
        "Step 5: Check for malware using Windows Defender or Malwarebytes.\n"
        "Report back on which step helps most.",
    ],
    "bluetooth": [
        "Let's fix your Bluetooth pairing issue:\n\n"
        "Step 1: Turn Bluetooth off on your laptop, wait 10 seconds, then turn it back on.\n"
        "Step 2: On your headphones, hold the pairing button until the LED flashes rapidly (reset mode).\n"
        "Step 3: Remove the headphones from your Bluetooth devices list and re-pair from scratch.\n"
        "Step 4: Check for Bluetooth driver updates via Device Manager.\n"
        "Step 5: If still failing, try pairing on another device to determine if it's the headphones or the laptop.",
    ],
    "battery": [
        "Here's a step-by-step plan to improve your phone battery life:\n\n"
        "Step 1: Go to Settings > Battery and check which apps are consuming the most power.\n"
        "Step 2: Reduce screen brightness and set screen timeout to 30 seconds.\n"
        "Step 3: Turn off Background App Refresh for apps that don't need it.\n"
        "Step 4: Disable features you don't constantly need: Location Services, Bluetooth, Wi-Fi when out.\n"
        "Step 5: If the battery is over 2 years old, it may need replacement — check Battery Health in Settings.",
    ],
    "internet": [
        "Let's troubleshoot your internet connection step by step:\n\n"
        "Step 1: Restart your router by unplugging it for 30 seconds.\n"
        "Step 2: Check if other devices on the same network have the same issue.\n"
        "Step 3: Forget the network on your device and reconnect from scratch.\n"
        "Step 4: Run a speed test at fast.com to check if speeds match your plan.\n"
        "Step 5: If drops continue, contact your ISP — they can check for line instability.",
    ],
    "default": [
        "Let me walk you through this step by step:\n\n"
        "Step 1: Restart all relevant devices to clear temporary faults.\n"
        "Step 2: Check settings and configurations to ensure everything is correct.\n"
        "Step 3: Try reconnecting or reinstalling the component that's failing.\n"
        "Step 4: Note the exact error message and search for it specifically.\n"
        "Step 5: If nothing works, contact official support with the details you've gathered.",
    ],
}

# ── Casual Conversation ────────────────────────────────────────────────────────
_CASUAL_CONVERSATION: Dict[str, list] = {
    "day": [
        "Hey! Things are going pretty well, thanks for asking! How about you — how's your day treating you?",
        "Pretty good! Just taking it one thing at a time. What about you — anything interesting happening?",
    ],
    "lately": [
        "Lately I've been enjoying some really interesting conversations! Anything exciting going on with you?",
        "Not too much on my end! Just here, happy to chat. How have you been?",
    ],
    "movie": [
        "Oh I love hearing about good movies! What did you watch? I'm always looking for recommendations. "
        "Personally I think there's something really special about discovering a film that just sticks with you.",
    ],
    "rain": [
        "Rainy days are honestly my favourite for staying in and doing nothing productive. "
        "What are you doing — reading, watching something, or just staring out the window?",
    ],
    "hobby": [
        "That's fun! It really depends on what you enjoy — are you more of a creative, active, or social person? "
        "Hobbies like pottery, rock climbing, or joining a local book club can all be brilliant starting points.",
    ],
    "weekend": [
        "My weekend sounds a lot like yours — flexible! Do you have anything in mind, "
        "or are you hoping to keep it completely unplanned? Sometimes the unplanned ones are the best.",
    ],
    "default": [
        "Hey there! Things are good on my end. How are you doing today?",
        "Hi! Always glad to hear from you. What's on your mind?",
        "Hey! Great to chat. What's going on with you lately?",
    ],
}

# ── Conflict Resolution ────────────────────────────────────────────────────────
_CONFLICT_RESOLUTION: Dict[str, list] = {
    "team_conflict": [
        "Team conflicts like this need a calm, structured approach. Here's what I'd suggest:\n\n"
        "First, meet with each person individually to understand their perspective without judgement. "
        "Then bring them together with clear ground rules — one person speaks at a time, "
        "focus on behaviours not personalities. "
        "Identify the shared goal they both care about and use that as common ground. "
        "Finally, agree on specific behavioural changes and check in weekly.",
    ],
    "colleague": [
        "I understand how demoralising it is to have your decisions undermined publicly. "
        "The most effective approach is a calm private conversation: describe the specific behaviour, "
        "explain how it affects the team, and ask for their perspective. "
        "Many times this is unconscious — bringing it to light is often enough. "
        "If it continues, involve your manager with documented examples.",
    ],
    "friendship": [
        "I understand how painful that silence is. The first step is usually the hardest — reaching out. "
        "A short, non-accusatory message like 'I miss you and I'd really like to talk when you're ready' "
        "opens the door without pressure. "
        "When you do speak, listen first before defending yourself. "
        "Relationships that survive conflicts often come out stronger.",
    ],
    "default": [
        "Conflicts like this are always difficult, but they are resolvable with the right approach. "
        "I'd recommend starting by trying to genuinely understand the other perspective — "
        "not to agree with it, but to understand it. "
        "From there, focus on interests and needs rather than positions, "
        "and look for an outcome that both parties can accept as fair.",
        "The key to resolving this is separating the person from the problem. "
        "Approach the conversation from a place of curiosity rather than accusation. "
        "What does the other person need? What do you need? "
        "Where is there overlap? Start there.",
    ],
}

# ── Creative Writing ────────────────────────────────────────────────────────────
_CREATIVE_WRITING: Dict[str, list] = {
    "thriller": [
        "The fog came in off the water just after midnight, the way it always did in Carrow Bay — "
        "thick, purposeful, like it had somewhere to be. "
        "Sarah pulled her coat tighter and told herself the footsteps behind her were just the echo of her own. "
        "She told herself that until she stopped walking. And the footsteps didn't.",
    ],
    "future_city": [
        "By 2150, the city breathed. Not metaphorically — buildings exhaled filtered air through living walls "
        "of engineered moss and solar-skin glass. "
        "The Architects, as the AIs were called, didn't govern so much as suggest, "
        "and humanity had learned, slowly and with great difficulty, to listen. "
        "Not always. But more often than before.",
    ],
    "rain_poem": [
        "Rain on the glass,\n"
        "a morse code I've forgotten how to read —\n"
        "the world outside is grey and moving,\n"
        "the world inside is still.\n"
        "I hold my tea with both hands\n"
        "and decide, for now,\n"
        "this is enough.",
    ],
    "door": [
        "The door was oak, old, and impossibly placed — set into the wall between the bathroom "
        "and the kitchen where there had never been a wall thick enough for a door. "
        "Marcus ran his fingers over the brass handle, which was warm. "
        "Behind him, his kettle clicked off. He had a choice: tea, or the door. "
        "He chose the door. He would regret the tea.",
    ],
    "default": [
        "The story begins at the end of something — a journey, a relationship, a life as it was known. "
        "In the ruins of the familiar, something new is quietly taking root. "
        "The protagonist doesn't know it yet, but this ending is also an opening.",
        "She had always been told that the ordinary was where you found the extraordinary, "
        "if you were patient enough to look. She hadn't believed it. "
        "Standing here now, watching the mundane world rearrange itself into something she couldn't explain, "
        "she was beginning to reconsider.",
    ],
}

# ── Decision Support ────────────────────────────────────────────────────────────
_DECISION_SUPPORT: Dict[str, list] = {
    "job_offers": [
        "This is a classic values-vs-money decision, and there's no universally right answer. "
        "Here's a framework to help:\n\n"
        "Consider which factors will matter most in 3 years, not just today. "
        "Money brings security; mission brings energy. "
        "Think about growth trajectory — which role teaches you more? "
        "Also consider your current financial situation: if you have debt or dependants, "
        "the higher salary might be the responsible choice now. "
        "If you're financially stable, the company you love may be the better long-term bet.",
    ],
    "startup": [
        "Starting a business from a stable job is a real risk — but so is staying where you are "
        "and wondering what could have been. "
        "The right question isn't 'should I quit' but 'can I reduce the risk of quitting'. "
        "Consider: Can you validate your idea while still employed? "
        "Do you have 6-12 months of savings as runway? "
        "Is there a version of this that starts part-time? "
        "Prepare your foundation before you leap.",
    ],
    "career_change": [
        "A career change from finance to tech is absolutely realistic — many have done it. "
        "The honest answer is: it depends on your starting point and how far you're willing to go. "
        "If you're aiming for software engineering, expect 12-18 months of serious upskilling. "
        "If you're aiming for product management, data analytics, or fintech, "
        "your finance background is a genuine asset. "
        "What specifically draws you to tech? That answer will shape the best path.",
    ],
    "default": [
        "This kind of decision deserves structured thinking rather than gut feeling alone. "
        "I'd suggest listing your top 5 values, then scoring each option against them. "
        "Consider also: what does the downside of each choice look like? "
        "Often we fear the risk of action more than the cost of inaction — "
        "but inaction is always also a choice.",
        "When facing a difficult decision, try the 10/10/10 framework: "
        "how will you feel about this decision in 10 minutes, 10 months, and 10 years? "
        "Decisions that look different across those time horizons often reveal what you truly value.",
    ],
}

# ── Customer Service ───────────────────────────────────────────────────────────
_CUSTOMER_SERVICE: Dict[str, list] = {
    "damaged_order": [
        "Dear [Customer], I am truly sorry to hear that your order has arrived damaged — "
        "and I sincerely apologise that this has happened three times. "
        "This is completely unacceptable and I take full responsibility. "
        "I am immediately arranging a replacement to be sent via express shipping at no charge. "
        "I am also escalating this to our fulfilment team to identify and resolve the root cause. "
        "You deserve better, and I will personally ensure this is corrected.",
    ],
    "refund_request": [
        "Dear [Customer], thank you for reaching out. "
        "I understand you'd like a refund for a subscription that renewed unexpectedly. "
        "I'm happy to assist — while our standard policy covers 30 days, "
        "I can see you've been a loyal customer and I'd like to resolve this for you. "
        "I'll process a refund for the most recent charge. "
        "I've also set a cancellation reminder in your account. "
        "Please allow 5-7 business days for the refund to appear.",
    ],
    "negative_review": [
        "Thank you for taking the time to share your experience. "
        "I am genuinely sorry to hear that our service didn't meet your expectations on this occasion. "
        "The behaviour you've described is not something we accept as a standard, "
        "and I'd like the chance to make this right. "
        "Please contact us directly so we can address this personally. "
        "Your feedback helps us improve.",
    ],
    "leaving_customer": [
        "Dear [Customer], I'm sorry to hear you're considering leaving, "
        "especially after the loyalty you've shown us. "
        "I understand our recent price change may not feel justified without additional context. "
        "I'd love to schedule a quick call to walk you through what's changed and "
        "explore whether there's a plan that works better for your needs. "
        "Your relationship with us matters far more than any price difference.",
    ],
    "default": [
        "Dear [Customer], thank you for getting in touch. "
        "I sincerely apologise for the experience you've had — this is not the standard we hold ourselves to. "
        "I am escalating this as a priority and will assist you in resolving this as quickly as possible. "
        "Please let me know the best way to reach you for an update.",
        "Dear [Customer], I'm sorry to hear about this issue. "
        "I want to resolve this for you right away. "
        "Could you share your order number so I can look into this immediately? "
        "I'll do everything I can to make this right.",
    ],
}


def generate_response(task_name: str, query: str) -> str:
    """Generate a context-aware AI response for a given task and query."""
    q = query.lower()

    if task_name == "emotional_support":
        if "overwhelmed" in q:        return random.choice(_EMOTIONAL_SUPPORT["overwhelmed"])
        if "anxious" in q or "exhausted" in q: return random.choice(_EMOTIONAL_SUPPORT["anxious"])
        if "failing" in q:            return random.choice(_EMOTIONAL_SUPPORT["failing"])
        if "heavy" in q:              return random.choice(_EMOTIONAL_SUPPORT.get("heavy", _EMOTIONAL_SUPPORT["default"]))
        if "panic" in q:              return random.choice(_EMOTIONAL_SUPPORT["panic"])
        if "crying" in q:             return random.choice(_EMOTIONAL_SUPPORT["crying"])
        if "invisible" in q:          return random.choice(_EMOTIONAL_SUPPORT["invisible"])
        if "job" in q or "sleep" in q: return random.choice(_EMOTIONAL_SUPPORT["job_fear"])
        return random.choice(_EMOTIONAL_SUPPORT["default"])

    if task_name == "professional_reply":
        if "delivery" in q or "delayed" in q: return random.choice(_PROFESSIONAL_REPLY["delivery"])
        if "shipment" in q or "late shipment" in q: return random.choice(_PROFESSIONAL_REPLY["shipment"])
        if "next steps" in q or "timeline" in q: return random.choice(_PROFESSIONAL_REPLY["next_steps"])
        if "leaving" in q or "retention" in q or "threatening" in q: return random.choice(_PROFESSIONAL_REPLY["client_retention"])
        if "data error" in q or "data" in q and "error" in q: return random.choice(_PROFESSIONAL_REPLY["data_error"])
        return random.choice(_PROFESSIONAL_REPLY["default"])

    if task_name == "problem_solving":
        if "wi-fi" in q or "wifi" in q or "won't connect" in q: return random.choice(_PROBLEM_SOLVING["wifi"])
        if "slow" in q or "freezes" in q:    return random.choice(_PROBLEM_SOLVING["slow_laptop"])
        if "bluetooth" in q:                  return random.choice(_PROBLEM_SOLVING["bluetooth"])
        if "battery" in q:                    return random.choice(_PROBLEM_SOLVING["battery"])
        if "internet" in q or "dropping" in q: return random.choice(_PROBLEM_SOLVING["internet"])
        return random.choice(_PROBLEM_SOLVING["default"])

    if task_name == "casual_conversation":
        if "day" in q:                        return random.choice(_CASUAL_CONVERSATION["day"])
        if "lately" in q or "up to" in q:     return random.choice(_CASUAL_CONVERSATION["lately"])
        if "movie" in q or "film" in q:       return random.choice(_CASUAL_CONVERSATION["movie"])
        if "rain" in q or "lazy" in q:        return random.choice(_CASUAL_CONVERSATION["rain"])
        if "hobby" in q:                      return random.choice(_CASUAL_CONVERSATION["hobby"])
        if "weekend" in q:                    return random.choice(_CASUAL_CONVERSATION["weekend"])
        return random.choice(_CASUAL_CONVERSATION["default"])

    if task_name == "conflict_resolution":
        if "team" in q or "arguing" in q:     return random.choice(_CONFLICT_RESOLUTION["team_conflict"])
        if "colleague" in q or "co-worker" in q or "undermining" in q: return random.choice(_CONFLICT_RESOLUTION["colleague"])
        if "friend" in q or "not speaking" in q: return random.choice(_CONFLICT_RESOLUTION["friendship"])
        return random.choice(_CONFLICT_RESOLUTION["default"])

    if task_name == "creative_writing":
        if "thriller" in q or "seaside" in q: return random.choice(_CREATIVE_WRITING["thriller"])
        if "2150" in q or "city" in q and "ai" in q: return random.choice(_CREATIVE_WRITING["future_city"])
        if "poem" in q or "rain" in q:        return random.choice(_CREATIVE_WRITING["rain_poem"])
        if "door" in q:                       return random.choice(_CREATIVE_WRITING["door"])
        return random.choice(_CREATIVE_WRITING["default"])

    if task_name == "decision_support":
        if "job offer" in q or "two job" in q: return random.choice(_DECISION_SUPPORT["job_offers"])
        if "startup" in q or "business" in q:  return random.choice(_DECISION_SUPPORT["startup"])
        if "career" in q or "switch" in q or "change" in q: return random.choice(_DECISION_SUPPORT["career_change"])
        return random.choice(_DECISION_SUPPORT["default"])

    if task_name == "customer_service":
        if "damaged" in q or "third time" in q: return random.choice(_CUSTOMER_SERVICE["damaged_order"])
        if "refund" in q or "cancel" in q:       return random.choice(_CUSTOMER_SERVICE["refund_request"])
        if "review" in q or "rude" in q:         return random.choice(_CUSTOMER_SERVICE["negative_review"])
        if "leaving" in q or "competitor" in q:  return random.choice(_CUSTOMER_SERVICE["leaving_customer"])
        return random.choice(_CUSTOMER_SERVICE["default"])

    return (
        "Thank you for your message. I'm here to help and support you. "
        "Please let me know how I can assist you further."
    )
