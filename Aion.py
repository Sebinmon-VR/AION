import openai
import os
import json
import inspect
from typing import Callable, Dict, Any, get_type_hints, List
from dotenv import load_dotenv
import tools  # Your custom tools module

# Load environment variables
load_dotenv(override=True)
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Chat History Management ===
class ChatHistory:
    def __init__(self, history_file: str = "./db/chat_history.json"):
        self.history_file = history_file
        self.messages: List[Dict[str, Any]] = []
        self.load_history()
    
    def load_history(self):
        """Load chat history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
                # Clean corrupted history on load
                self.clean_corrupted_history()
        except Exception as e:
            print(f"⚠️ Error loading chat history: {e}")
            self.messages = []
    
    def save_history(self):
        """Save chat history to file"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving chat history: {e}")
    
    def add_message(self, role: str, content: str, tool_calls: List[Dict] = None):
        """Add a message to history"""
        message = {"role": role, "content": content}
        if tool_calls:
            message["tool_calls"] = tool_calls
        self.messages.append(message)
    
    def add_tool_message(self, tool_call_id: str, name: str, content: str):
        """Add a tool response message to history"""
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
            "content": content
        })
    
    def get_recent_messages(self, max_tokens: int = 4000) -> List[Dict]:
        """Get recent messages within token limit (approximate)"""
        # Simple token estimation: ~4 chars per token
        token_count = 0
        recent_messages = []
        
        for message in reversed(self.messages):
            message_tokens = len(str(message)) // 4
            if token_count + message_tokens > max_tokens:
                break
            recent_messages.insert(0, message)
            token_count += message_tokens
        
        # Validate message sequence to ensure tool messages have corresponding tool_calls
        validated_messages = []
        expecting_tool_responses = []
        
        for msg in recent_messages:
            if msg["role"] == "assistant" and msg.get("tool_calls"):
                # Track which tool responses we're expecting
                expecting_tool_responses.extend([tc["id"] for tc in msg["tool_calls"]])
                validated_messages.append(msg)
            elif msg["role"] == "tool":
                # Only include tool messages that have corresponding tool_calls
                if msg.get("tool_call_id") in expecting_tool_responses:
                    validated_messages.append(msg)
                    expecting_tool_responses.remove(msg.get("tool_call_id"))
                # Skip orphaned tool messages
            else:
                # Include user, system, and regular assistant messages
                validated_messages.append(msg)
        
        return validated_messages
    
    def clean_corrupted_history(self):
        """Clean up corrupted chat history by removing orphaned tool messages"""
        cleaned_messages = []
        expecting_tool_responses = []
        
        for msg in self.messages:
            if msg["role"] == "assistant" and msg.get("tool_calls"):
                # Track which tool responses we're expecting
                expecting_tool_responses.extend([tc["id"] for tc in msg["tool_calls"]])
                cleaned_messages.append(msg)
            elif msg["role"] == "tool":
                # Only keep tool messages that have corresponding tool_calls
                if msg.get("tool_call_id") in expecting_tool_responses:
                    cleaned_messages.append(msg)
                    expecting_tool_responses.remove(msg.get("tool_call_id"))
                else:
                    print(f"🧹 Removing orphaned tool message: {msg.get('name', 'unknown')}")
            else:
                # Keep user, system, and regular assistant messages
                cleaned_messages.append(msg)
        
        # Clear remaining expected tool responses (they were never fulfilled)
        if expecting_tool_responses:
            print(f"🧹 Found {len(expecting_tool_responses)} unfulfilled tool calls")
        
        self.messages = cleaned_messages
        self.save_history()
        print(f"✅ Chat history cleaned. Kept {len(cleaned_messages)} valid messages.")

    def clear_history(self):
        """Clear all chat history"""
        self.messages = []
        self.save_history()

# Initialize chat history
chat_history = ChatHistory()

# === Tool schema helpers ===
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

# === Dynamically collect valid tools ===
function_map = {
    name: obj
    for name, obj in vars(tools).items()
    if callable(obj)
    and inspect.isfunction(obj)
    and inspect.getmodule(obj).__name__ == "tools"
}

# Optional: print loaded tools for debug
print("🛠️ Loaded tools:", list(function_map.keys()))

# Convert to OpenAI tool format
tools_schema = [function_to_tool_schema(fn) for fn in function_map.values()]

# === Core chat function ===
def chat_with_bot(user_input: str, system_prompt: str = None):
    # Build messages with history
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # Add recent chat history for context
    messages.extend(chat_history.get_recent_messages())
    
    # Add current user input
    messages.append({"role": "user", "content": user_input})
    chat_history.add_message("user", user_input)

    print("\n📤 Asking GPT...")
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        tools=tools_schema,
        tool_choice="auto"
    )

    message = response["choices"][0]["message"]

    if message.get("tool_calls"):
        # Add assistant message with tool calls to history
        chat_history.add_message("assistant", message.get("content", ""), message.get("tool_calls"))
        
        # Execute all tool calls first
        tool_results = []
        all_tools_successful = True
        
        for tool_call in message["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            args = json.loads(tool_call["function"]["arguments"])
            print(f"\n🔧 GPT wants to call: {tool_name}({args})")

            if tool_name in function_map:
                try:
                    result = function_map[tool_name](**args)
                    print(f"✅ Tool {tool_name} executed successfully")
                except Exception as e:
                    result = f"⚠️ Error running tool `{tool_name}`: {e}"
                    print(f"❌ Tool {tool_name} failed: {e}")
                    all_tools_successful = False

                # Store tool result
                tool_results.append({
                    "tool_call": tool_call,
                    "result": result
                })
                
                # Add tool response to history
                chat_history.add_tool_message(tool_call["id"], tool_name, str(result))
            else:
                error_msg = f"❌ Unknown tool `{tool_name}`"
                tool_results.append({
                    "tool_call": tool_call,
                    "result": error_msg
                })
                chat_history.add_tool_message(tool_call["id"], tool_name, error_msg)
                all_tools_successful = False
                print(f"❌ Unknown tool: {tool_name}")

        # Add all tool calls and results to messages for GPT
        messages.append({"role": "assistant", "tool_calls": message["tool_calls"]})
        
        for tool_result in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": tool_result["tool_call"]["id"],
                "name": tool_result["tool_call"]["function"]["name"],
                "content": str(tool_result["result"])
            })

        print(f"\n📋 All {len(tool_results)} tools executed. Sending results back to GPT...")
        
        # Get final response from GPT after all tools are executed
        followup = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )
        final_response = followup["choices"][0]["message"]["content"]
        
        # Add final response to history
        chat_history.add_message("assistant", final_response)
        chat_history.save_history()
        
        return final_response
    else:
        # Add assistant response to history
        chat_history.add_message("assistant", message["content"])
        chat_history.save_history()
        return message["content"]

# === Run chatbot loop ===
if __name__ == "__main__":
    
    
    system_prompt = """
You are a helpful AI assistant. You can call Python tools to complete user tasks.
The default database folder is './db'. If the user asks about the database without specifying a folder path, assume './db'.
Do not ask the user for info you can infer. Use tools whenever needed.
You have access to chat history and can remember previous conversations.
    """
    
    print("🤖 AI Assistant with Memory - Ready to chat!")
    print("💡 Tips: Type 'exit' or 'quit' to leave, 'clear history' to reset memory")
    print("🧹 Commands: 'clean history' to fix corrupted messages, 'show history' to view recent")
    print("📁 Chat history is automatically saved to ./db/chat_history.json")
    print("-" * 50)
    
    while True:
        user_input = input("\n👤 You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("👋 Goodbye! Your chat history has been saved.")
            break
        elif user_input.strip().lower() == "clear history":
            chat_history.clear_history()
            print("✅ Chat history cleared!")
            continue
        elif user_input.strip().lower() == "clean history":
            chat_history.clean_corrupted_history()
            print("✅ Chat history cleaned!")
            continue
        elif user_input.strip().lower() == "show history":
            messages = chat_history.get_recent_messages(1000)
            if messages:
                print("\n📜 Recent Chat History:")
                for i, msg in enumerate(messages[-5:], 1):  # Show last 5 messages
                    role = msg["role"].title()
                    content = msg.get("content", "")
                    if len(content) > 100:
                        content = content[:100] + "..."
                    print(f"{i}. {role}: {content}")
            else:
                print("No chat history available.")
            continue
        
        reply = chat_with_bot(user_input, system_prompt=system_prompt)
        print(f"🤖 Bot: {reply}")
