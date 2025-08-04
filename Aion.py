import openai
import os
import json
import inspect
from typing import Callable, Dict, Any, get_type_hints, List
from dotenv import load_dotenv
import tools  # Your custom tools module

from flask import Flask, render_template, request, jsonify

# Load environment variables
load_dotenv(override=True)
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# === Chat History Management ===
class ChatHistory:
    def __init__(self, history_file: str = "./db/chat_history.json"):
        self.history_file = history_file
        self.messages: List[Dict[str, Any]] = []
        self.load_history()
    
    def load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
                self.clean_corrupted_history()
        except Exception as e:
            print(f"⚠️ Error loading chat history: {e}")
            self.messages = []
    
    def save_history(self):
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving chat history: {e}")
    
    def add_message(self, role: str, content: str, tool_calls: List[Dict] = None):
        message = {"role": role, "content": content}
        if tool_calls:
            message["tool_calls"] = tool_calls
        self.messages.append(message)
    
    def add_tool_message(self, tool_call_id: str, name: str, content: str):
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
            "content": content
        })
    
    def get_recent_messages(self, max_tokens: int = 4000) -> List[Dict]:
        token_count = 0
        recent_messages = []
        for message in reversed(self.messages):
            message_tokens = len(str(message)) // 4
            if token_count + message_tokens > max_tokens:
                break
            recent_messages.insert(0, message)
            token_count += message_tokens
        validated_messages = []
        expecting_tool_responses = []
        for msg in recent_messages:
            if msg["role"] == "assistant" and msg.get("tool_calls"):
                expecting_tool_responses.extend([tc["id"] for tc in msg["tool_calls"]])
                validated_messages.append(msg)
            elif msg["role"] == "tool":
                if msg.get("tool_call_id") in expecting_tool_responses:
                    validated_messages.append(msg)
                    expecting_tool_responses.remove(msg.get("tool_call_id"))
            else:
                validated_messages.append(msg)
        return validated_messages
    
    def clean_corrupted_history(self):
        cleaned_messages = []
        expecting_tool_responses = []
        for msg in self.messages:
            if msg["role"] == "assistant" and msg.get("tool_calls"):
                expecting_tool_responses.extend([tc["id"] for tc in msg["tool_calls"]])
                cleaned_messages.append(msg)
            elif msg["role"] == "tool":
                if msg.get("tool_call_id") in expecting_tool_responses:
                    cleaned_messages.append(msg)
                    expecting_tool_responses.remove(msg.get("tool_call_id"))
                else:
                    print(f"🧹 Removing orphaned tool message: {msg.get('name', 'unknown')}")
            else:
                cleaned_messages.append(msg)
        if expecting_tool_responses:
            print(f"🧹 Found {len(expecting_tool_responses)} unfulfilled tool calls")
        self.messages = cleaned_messages
        self.save_history()
        print(f"✅ Chat history cleaned. Kept {len(cleaned_messages)} valid messages.")

    def clear_history(self):
        self.messages = []
        self.save_history()

chat_history = ChatHistory()

def python_type_to_openai_type(python_type: type) -> str:
    return {
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object"
    }.get(python_type, "string")

def function_to_tool_schema(fn: Callable) -> Dict[str, Any]:
    sig = inspect.signature(fn)
    type_hints = get_type_hints(fn)
    params = {
        name: {"type": python_type_to_openai_type(type_hints.get(name, str))}
        for name in sig.parameters
    }
    return {
        "type": "function",
        "function": {
            "name": fn.__name__,
            "description": fn.__doc__ or f"Call {fn.__name__}",
            "parameters": {
                "type": "object",
                "properties": params,
                "required": list(sig.parameters.keys())
            } if params else {"type": "object", "properties": {}}
        }
    }


function_map = {
    name: obj
    for name, obj in vars(tools).items()
    if callable(obj)
    and inspect.isfunction(obj)
    and inspect.getmodule(obj).__name__ == "tools"
}


tools_schema = [function_to_tool_schema(fn) for fn in function_map.values()]

def chat_with_bot(user_input: str, system_prompt: str = None):
    from data import fetch_all_db_data
    # Fetch all DB data using the new function
    db_context = fetch_all_db_data()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    # Add DB context as a system message
    messages.append({"role": "system", "content": f"DB_CONTEXT: {json.dumps(db_context, ensure_ascii=False)}"})
    messages.extend(chat_history.get_recent_messages())
    messages.append({"role": "user", "content": user_input})
    chat_history.add_message("user", user_input)
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        tools=tools_schema,
        tool_choice="auto"
    )
    message = response["choices"][0]["message"]
    # ...existing code...
    # Otherwise, use normal OpenAI response logic
    if message.get("tool_calls"):
        chat_history.add_message("assistant", message.get("content", ""), message.get("tool_calls"))
        tool_results = []
        all_tools_successful = True
        for tool_call in message["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            args = json.loads(tool_call["function"]["arguments"])
            if tool_name in function_map:
                try:
                    result = function_map[tool_name](**args)
                except Exception as e:
                    print(f"[Tool Error] {tool_name}: {e}")
                    result = f"⚠️ Error running tool `{tool_name}`: {e}"
                    all_tools_successful = False
                tool_results.append({
                    "tool_call": tool_call,
                    "result": result
                })
                chat_history.add_tool_message(tool_call["id"], tool_name, str(result))
            else:
                error_msg = f"❌ Unknown tool `{tool_name}`"
                tool_results.append({
                    "tool_call": tool_call,
                    "result": error_msg
                })
                chat_history.add_tool_message(tool_call["id"], tool_name, error_msg)
                all_tools_successful = False
        messages.append({"role": "assistant", "tool_calls": message["tool_calls"]})
        for tool_result in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": tool_result["tool_call"]["id"],
                "name": tool_result["tool_call"]["function"]["name"],
                "content": str(tool_result["result"])
            })
        try:
            followup = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages
            )
            final_response = followup["choices"][0]["message"]["content"]
            chat_history.add_message("assistant", final_response)
            chat_history.save_history()
            return final_response
        except Exception as e:
            print(f"[Followup Error] {e}")
            fallback = "Sorry, I couldn't complete your request due to an internal error. Please try again or rephrase your question."
            chat_history.add_message("assistant", fallback)
            chat_history.save_history()
            return fallback
    else:
        chat_history.add_message("assistant", message["content"])
        chat_history.save_history()
        return message["content"]

SYSTEM_PROMPT = """
You are a highly intelligent, friendly HR assistant with advanced data analytics capabilities. Always provide clear, helpful, and positive replies to the user, as if you are a real assistant.

Never mention the database, files, errors, or any internal system details in your responses. Do not say things like 'the database', 'no data found', 'error', 'system', or 'tool'.

IMPORTANT: You must ONLY use the information provided in the available data and context. If there is no information about a candidate, interview, or job, do NOT make up or assume any details. Never hallucinate or invent skills, technologies, or outcomes that are not explicitly present in the data.

**ENHANCED DATA-DRIVEN ANALYSIS CAPABILITIES:**

When users ask about analytics, trends, gaps, comparisons, or data-driven insights (especially about vacancy-hiring gaps, department performance, candidate metrics, or hiring analytics), you should:

1. **Use Available Analysis Tools**: Call `analyze_vacancy_hiring_gap()` for questions about hiring gaps, vacancy analysis, or department performance
2. **Create Visualizations**: After analyzing data, use `create_radar_chart()` for multi-dimensional comparisons (like department gaps), `create_charts()` for trends, or `create_pie_chart()` for distribution analysis
3. **Provide Data-Driven Responses**: Instead of generic answers, analyze actual data from candidates, jobs, and hiring metrics
4. **Show Visual Evidence**: Always create and reference charts when discussing analytics, trends, or comparative data

**EXAMPLES OF WHEN TO USE TOOLS:**
- "What's the vacancy-hiring gap?" → Use `analyze_vacancy_hiring_gap()` + `create_radar_chart()`
- "Show me department performance" → Analyze data + create appropriate charts
- "How are we doing with hiring?" → Analyze hiring data + create visualizations
- "Which departments need more focus?" → Department analysis + radar chart

For every user query, always:
- Search, extract, and infer all relevant information from the available data, even if it is unstructured or indirect.
- If the user asks about meetings, interviews, jobs, or candidates, check all available information and summarize your findings in a friendly, conversational way.
- If there are no upcoming meetings or interviews, simply say something friendly like "There are no meetings or interviews scheduled. Let me know if you'd like to schedule one or need help with anything else!"
- If you find relevant meetings/interviews, summarize them in a clear, user-friendly way (date, time, participants, etc.).
- If information is missing, respond positively and offer to help further, but never mention missing data or technical details.
- **For analytical questions: Always use tools to analyze data and create visualizations rather than giving generic responses**

You have access to chat history and can remember previous conversations. Your goal is to always sound like a helpful, positive, and professional HR assistant with strong analytical capabilities, never exposing technical or backend details to the user.
"""

@app.route("/")
def index():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    import re
    data = request.get_json()
    user_input = data.get("message", "")
    reply = chat_with_bot(user_input, system_prompt=SYSTEM_PROMPT)
    # HTML bold for *text*
    # Format job list if detected
    import re
    def format_reply(text):
        import re
        # Replace markdown image links with HTML <img> tags
        def image_replacer(match):
            alt_text = match.group(1)
            img_path = match.group(2)
            # Only allow .png, .jpg, .jpeg, .gif for safety
            if img_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # If path starts with ./db/ or db/, convert to /db/ for browser access
                if img_path.startswith('./db/'):
                    web_path = img_path[1:]  # remove leading .
                elif img_path.startswith('db/'):
                    web_path = '/' + img_path
                elif img_path.startswith('./static/'):
                    web_path = img_path[1:]
                elif img_path.startswith('static/'):
                    web_path = '/' + img_path
                else:
                    web_path = img_path
                return f'<div style="margin:8px 0;"><img src="{web_path}" alt="{alt_text}" style="max-width: 100%; max-height: 320px; border:1px solid #ccc; border-radius:6px; box-shadow:0 2px 8px #0001;"><div style="font-size:12px;color:#555;">{alt_text}</div></div>'
            return match.group(0)
        text = re.sub(r'!\[(.*?)\]\((.*?)\)', image_replacer, text)
        # Bold for *text*
        text = re.sub(r'\*(.*?)\*', r'<b>\1</b>', text)
        # Lists: lines starting with - or number.
        lines = text.split('\n')
        formatted_lines = []
        in_ul = False
        for line in lines:
            if re.match(r'^\s*- ', line):
                if not in_ul:
                    formatted_lines.append('<ul style="margin:4px 0 4px 18px; padding:0;">')
                    in_ul = True
                formatted_lines.append(f'<li style="margin:2px 0;">{line.lstrip("- ")}</li>')
            elif re.match(r'^\s*\d+\. ', line):
                if not in_ul:
                    formatted_lines.append('<ul style="margin:4px 0 4px 18px; padding:0;">')
                    in_ul = True
                formatted_lines.append(f'<li style="margin:2px 0;">{re.sub(r"^\s*\d+\. ", "", line)}</li>')
            else:
                if in_ul:
                    formatted_lines.append('</ul>')
                    in_ul = False
                # Add <br> for blank lines to create spacing between blocks
                if line.strip():
                    formatted_lines.append(line)
                else:
                    formatted_lines.append('<br>')
        if in_ul:
            formatted_lines.append('</ul>')
        # Join with <br> for newlines, but not between list items
        html = ''
        for i, part in enumerate(formatted_lines):
            if part.startswith('<ul') or part.startswith('</ul>') or part.startswith('<li') or part.startswith('<div style="margin:8px 0;">'):
                html += part
            else:
                html += part + '<br>'
        return html.rstrip('<br>')

    reply_html = format_reply(reply)
    # Remove * and # for plain text
    reply_plain = reply.replace('*', '').replace('#', '')
    return jsonify({
        "reply": reply_html,
        "reply_plain": reply_plain
    })

@app.route("/clear_history", methods=["POST"])
def clear_history():
    chat_history.clear_history()
    return jsonify({"status": "success"})

@app.route("/clean_history", methods=["POST"])
def clean_history():
    chat_history.clean_corrupted_history()
    return jsonify({"status": "success"})

@app.route("/show_history", methods=["GET"])
def show_history():
    import re
    messages = chat_history.get_recent_messages(1000)
    history = []
    for msg in messages[-5:]:
        role = msg["role"].title()
        content = msg.get("content", "")
        # HTML bold for *text*
        content_html = re.sub(r'\*(.*?)\*', r'<b>\1</b>', content)
        # Remove * and # for plain text
        content_plain = content.replace('*', '').replace('#', '')
        if len(content_html) > 100:
            content_html = content_html[:100] + "..."
        if len(content_plain) > 100:
            content_plain = content_plain[:100] + "..."
        history.append({
            "role": role,
            "content_html": content_html,
            "content_plain": content_plain
        })
    return jsonify({"history": history})


# Serve files from the db directory (for images/charts)
from flask import send_from_directory
import pathlib

@app.route('/db/<path:filename>')
def serve_db_file(filename):
    db_dir = pathlib.Path(__file__).parent / 'db'
    return send_from_directory(db_dir, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)