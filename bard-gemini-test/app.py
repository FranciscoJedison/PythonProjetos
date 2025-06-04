from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import google.generativeai as genai
import pathlib
import textwrap
from IPython.display import display
from IPython.display import Markdown

load_dotenv()
genai.configure(api_key=os.getenv("Sua API Key aqui"))

model = genai.GenerativeModel('gemini-1.5-flash') #Selecionar o modelo da AI aqui

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


@app.route("/perguntar", methods=["POST"])
def perguntar():
    data = request.get_json()
    pergunta = data.get("mensagem", "")

    try:
        response = model.generate_content(pergunta, stream=True)
        to_markdown(response.resolve())
        return jsonify({"resposta": response.text})
    except Exception as e:
        return jsonify({"resposta": f"Ocorreu um erro: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
