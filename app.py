import os
from flask import Flask, render_template_string, request, jsonify
import openai
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image

# Set your OpenAI API Key (use env variable for GitHub safety)
openai.api_key = os.getenv(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)

app = Flask(__name__)

# Simple HTML + JS frontend served from backend
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AkinBest AI</title>
    <style>
        body { font-family: Arial; background: #f2f2f2; }
        #chat { width: 80%; margin: auto; padding: 20px; background: white; border-radius: 10px; }
        #messages { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; }
        .msg { margin: 5px 0; }
        .user { font-weight: bold; color: blue; }
        .bot { font-weight: bold; color: green; }
    </style>
</head>
<body>
    <div id="chat">
        <h2>AkinBest AI (ChatGPT + Gauth)</h2>
        <div id="messages"></div>
        <input id="user_input" type="text" placeholder="Ask me anything..." style="width:70%;">
        <button onclick="sendMessage()">Send</button>
        <br><br>
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" name="image" id="imageInput">
            <button type="submit">Upload & Solve</button>
        </form>
    </div>
    <script>
        async function sendMessage() {
            let input = document.getElementById("user_input").value;
            if (input.trim() === "") return;
            addMessage("You", input, "user");
            document.getElementById("user_input").value = "";
            let res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: input })
            });
            let data = await res.json();
            addMessage("AI", data.reply, "bot");
        }
        function addMessage(sender, text, cls) {
            let msgDiv = document.createElement("div");
            msgDiv.classList.add("msg", cls);
            msgDiv.innerHTML = `<b>${sender}:</b> ${text}`;
            document.getElementById("messages").appendChild(msgDiv);
            document.getElementById("messages").scrollTop = document.getElementById("messages").scrollHeight;
        }
        document.getElementById("uploadForm").onsubmit = async (e) => {
            e.preventDefault();
            let formData = new FormData();
            formData.append("image", document.getElementById("imageInput").files[0]);
            let res = await fetch("/upload", { method: "POST", body: formData });
            let data = await res.json();
            addMessage("Image OCR", data.text, "bot");
            addMessage("AI", data.answer, "bot");
        };
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system","content":"You are AkinBest AI, a helpful assistant with math & OCR abilities."},
                  {"role":"user","content":user_message}]
    )
    reply = response.choices[0].message["content"]
    return jsonify({"reply": reply})

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["image"]
    filename = secure_filename(file.filename)
    filepath = os.path.join("uploads", filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(filepath)

    # OCR (read text from image)
    text = pytesseract.image_to_string(Image.open(filepath))

    # Ask GPT to solve / explain text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system","content":"You are a tutor that explains text and solves math problems."},
                  {"role":"user","content":f"Here is the OCR text from image:\n{text}\nSolve or explain it."}]
    )
    answer = response.choices[0].message["content"]

    return jsonify({"text": text, "answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
