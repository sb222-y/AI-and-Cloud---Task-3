import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import random
import ast
import operator

# -------------------
# Safe math evaluator
# -------------------
# Allow only simple arithmetic operations by parsing AST
_allowed_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.FloorDiv: operator.floordiv,
}

def safe_eval(expr):
    """
    Evaluate a math expression safely using AST. Supports numbers and binary/unary ops.
    Raises ValueError on invalid expressions.
    """
    def _eval(node):
        if isinstance(node, ast.Num):  # <number>
            return node.n
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type in _allowed_operators:
                return _allowed_operators[op_type](left, right)
            raise ValueError("Operation not allowed")
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op_type = type(node.op)
            if op_type in _allowed_operators:
                return _allowed_operators[op_type](operand)
            raise ValueError("Unary operation not allowed")
        raise ValueError("Invalid expression")

    try:
        parsed = ast.parse(expr, mode='eval')
        return _eval(parsed.body)
    except Exception as e:
        raise ValueError(str(e))

# -------------------
# Chatbot logic
# -------------------
STATIC_ANSWERS = {
    "what is your name": "I'm an AI rule-based chatbot.",
    "who created you": "I was created by a human developer (you!).",
    "how are you": "I'm a program — I don't have feelings, but thanks for asking!",
    "help": "Try asking me about the time, doing arithmetic (e.g. 2+2), or say hello!",
}

GREETINGS = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
FAREWELLS = ["bye", "goodbye", "see you", "see ya"]

SMALL_TALK = [
    "Nice to chat with you!",
    "Tell me more.",
    "Cool! 😎",
    "I like learning from conversation.",
    "Ha — that's interesting!"
]

JOKES = [
    "Why did the programmer quit his job? Because he didn't get arrays.",
    "There are only 10 types of people in this world: those who understand binary and those who don't.",
    "Why do Java developers wear glasses? Because they don't see sharp."
]

FAQ_ANSWERS = {
    "what is ai": "AI stands for Artificial Intelligence — systems that perform tasks that usually require human intelligence.",
    "what is python": "Python is a popular high-level programming language used for many tasks: web, data, automation, and more.",
    "what is chatbot": "A chatbot is software that can simulate conversation with human users."
}

def normalized(text):
    return text.strip().lower()

def get_response(user_text, mode="Normal"):
    txt = normalized(user_text)

    # Mode-specific replies
    if mode == "FAQ":
        for q, a in FAQ_ANSWERS.items():
            if q in txt:
                return a
    elif mode == "Joke":
        # In Joke mode, reply with a joke for many inputs
        return random.choice(JOKES)

    # Greeting detection
    if any(txt.startswith(g) for g in GREETINGS):
        return random.choice(["Hello!", "Hi there!", "Hey! How can I help?"])

    # Farewell detection
    if any(f in txt for f in FAREWELLS):
        return random.choice(["Goodbye!", "See you later!", "Take care!"])

    # Static Q/A
    for q, a in STATIC_ANSWERS.items():
        if q in txt:
            return a

    # Time/Date detection
    if "time" in txt:
        return "Current time: " + datetime.now().strftime("%H:%M:%S")
    if "date" in txt or "day" in txt:
        return "Today's date: " + datetime.now().strftime("%Y-%m-%d")

    # Math detection: attempt safe eval if expression looks arithmetic
    # crude heuristic: contains digits and one of arithmetic symbols
    if any(ch.isdigit() for ch in txt) and any(sym in txt for sym in "+-*/%^"):
        # remove unwanted characters
        expr = txt.replace("^", "**")
        expr = expr.replace(" ", "")
        try:
            val = safe_eval(expr)
            return f"Result: {val}"
        except ValueError:
            # fall through to error handling
            pass

    # Small talk detection by keywords
    if any(word in txt for word in ["weather", "movie", "music", "food", "hobby"]):
        return random.choice(SMALL_TALK)

    # If nothing matched
    return "Sorry, I don't understand that yet. Try asking for the time, a math problem, or say 'help'."

# -------------------
# GUI / Application
# -------------------
class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rule-Based AI Chatbot")
        self.minsize(420, 460)
        self.configure(bg="#222")  # dark-ish background

        # Top frame: title and mode selector
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        top_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(top_frame, text="AI Chatbot (Rule-Based)", font=("Segoe UI", 14, "bold"))
        title_label.grid(row=0, column=0, sticky="w")

        self.mode_var = tk.StringVar(value="Normal")
        modes = ("Normal", "FAQ", "Joke")
        mode_menu = ttk.OptionMenu(top_frame, self.mode_var, self.mode_var.get(), *modes)
        mode_menu.grid(row=0, column=1, sticky="e")

        # Chat display (scrolled)
        self.chat_display = ScrolledText(self, wrap=tk.WORD, state="disabled", height=18)
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        self.chat_display.configure(font=("Segoe UI", 10), bg="white")

        # Input frame: entry + send button
        input_frame = ttk.Frame(self)
        input_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        input_frame.columnconfigure(0, weight=1)

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var)
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.input_entry.bind("<Return>", self.on_send)

        send_btn = ttk.Button(input_frame, text="Send", command=self.on_send)
        send_btn.grid(row=0, column=1, sticky="e")

        # Make the grid respond when window is resized
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Intro message
        self.bot_say("Hello! I'm an AI chatbot. Type 'help' for tips. You can switch modes (Normal/FAQ/Joke).")

    def bot_say(self, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, "Bot: " + message + "\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.configure(state="disabled")

    def user_say(self, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, "You: " + message + "\n")
        self.chat_display.see(tk.END)
        self.chat_display.configure(state="disabled")

    def on_send(self, event=None):
        user_text = self.input_var.get().strip()
        if not user_text:
            return
        self.user_say(user_text)
        self.input_var.set("")
        mode = self.mode_var.get()
        # compute response
        try:
            response = get_response(user_text, mode=mode)
        except Exception as e:
            response = "Error processing your input."
        # simulate a little typing delay (non-blocking) could be added; keeping simple
        self.bot_say(response)

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
