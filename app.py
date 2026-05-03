import gradio as gr
import os
import json
from groq import Groq
from docx import Document

# 🔑 API KEY
os.environ["GROQ_API_KEY"] = "gsk_your_key_here"
client = Groq(api_key=os.environ["GROQ_API_KEY"])

# ---------------------------
# AI GENERATION FUNCTION
# ---------------------------
def generate_exam_data(topic, difficulty, level, mcq_n, short_n, long_n, blooms):

    prompt = f"""
You are an expert exam paper generator.

Topic: {topic}
Difficulty: {difficulty}
Level: {level}

Generate JSON:
{{
"mcqs":[{{"q":"","options":["","","",""],"answer":""}}],
"short":[{{"q":"","answer":""}}],
"long":[{{"q":"","answer":""}}]
}}

Rules:
- {mcq_n} MCQs
- {short_n} Short questions
- {long_n} Long questions
"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return json.loads(res.choices[0].message.content)


# ---------------------------
# FORMAT OUTPUT
# ---------------------------
def format_output(data):

    mcq, short, longq, ans = "", "", "", ""

    mcq += "MCQs:\n\n"
    for i, q in enumerate(data["mcqs"], 1):
        mcq += f"{i}. {q['q']}\n"

    short += "Short:\n\n"
    for i, q in enumerate(data["short"], 1):
        short += f"{i}. {q['q']}\n"

    longq += "Long:\n\n"
    for i, q in enumerate(data["long"], 1):
        longq += f"{i}. {q['q']}\n"

    ans += "Answer Key:\n\n"
    for i, q in enumerate(data["mcqs"], 1):
        ans += f"{i}. {q['answer']}\n"

    return mcq, short, longq, ans


# ---------------------------
# DOCX EXPORT
# ---------------------------
def create_docx(text):
    doc = Document()
    doc.add_paragraph(text)
    path = "/content/exam.docx"
    doc.save(path)
    return path


# ---------------------------
# PIPELINE
# ---------------------------
def run_all(topic, difficulty, level, mcq_n, short_n, long_n, blooms):

    data = generate_exam_data(topic, difficulty, level, mcq_n, short_n, long_n, blooms)

    mcq, short, longq, ans = format_output(data)

    full = mcq + "\n" + short + "\n" + longq + "\n" + ans

    file = create_docx(full)

    return mcq, short, longq, ans, file


# ---------------------------
# UI
# ---------------------------
with gr.Blocks(theme=gr.themes.Soft()) as demo:

    gr.Markdown("# 🎓 AI Exam Generator")

    topic = gr.Textbox(label="Topic")
    level = gr.Dropdown(["School","College","University","Research","PhD"])

    difficulty = gr.Dropdown(["Easy","Medium","Hard"])
    blooms = gr.Checkbox(label="Bloom's Taxonomy")

    mcq_n = gr.Slider(1,20,5)
    short_n = gr.Slider(1,10,3)
    long_n = gr.Slider(1,5,2)

    btn = gr.Button("Generate")

    with gr.Tabs():

        mcq_out = gr.Textbox(label="MCQs")
        short_out = gr.Textbox(label="Short")
        long_out = gr.Textbox(label="Long")
        ans_out = gr.Textbox(label="Answer Key")
        file_out = gr.File(label="Download DOCX")

    btn.click(
        run_all,
        [topic,difficulty,level,mcq_n,short_n,long_n,blooms],
        [mcq_out,short_out,long_out,ans_out,file_out]
    )

demo.launch()
