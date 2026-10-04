import streamlit as st
import google.generativeai as genai
import json

# Page Configuration
st.set_page_config(page_title="অসমীয়া স্বয়ংক্ৰিয় পৰীক্ষা", layout="centered")

st.title("📚 অসমীয়া ভাষাৰ স্বয়ংক্ৰিয় অনলাইন পৰীক্ষা")
st.write("এই ছিষ্টেমটোৱে AI (Gemini) ব্যৱহাৰ কৰি নিজেই প্ৰশ্নকাকত প্ৰস্তুত কৰে আৰু পৰীক্ষা লয়।")

# Sidebar for API Key
st.sidebar.header("ছেটিংছ (Settings)")
api_key = st.sidebar.text_input("আপোনাৰ Google API Key ইয়াত দিয়ক:", type="password")
st.sidebar.markdown("[নতুন API Key বনাবলৈ ইয়াত ক্লিক কৰক](https://aistudio.google.com/app/apikey)")

if not api_key:
    st.warning("পৰীক্ষা আৰম্ভ কৰিবলৈ অনুগ্ৰহ কৰি বাওঁফালৰ মেনুত আপোনাৰ Google Gemini API Key দিয়ক।")
    st.stop()

# Configure Gemini API
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})

def generate_exam():
    prompt = """
    Generate an Assamese language exam in JSON format with the following structure:
    {
      "passage": "A short story or informative passage in Assamese (approx 60-80 words).",
      "comprehension_questions": [
        {"question": "Question in Assamese", "options": ["option1", "option2", "option3", "option4"], "answer": "option1"}
      ],
      "grammar_questions": [
        {"question": "Grammar question in Assamese", "options": ["option1", "option2", "option3", "option4"], "answer": "option2"}
      ],
      "pedagogy_questions": [
        {"question": "Assamese language pedagogy question", "options": ["option1", "option2", "option3", "option4"], "answer": "option3"}
      ]
    }
    Provide 2 questions for each category. All content MUST be in the Assamese language.
    For the "answer" field, provide the EXACT text of the correct option from the options list.
    """
    response = model.generate_content(prompt)
    return json.loads(response.text)

# Session State to store exam data
if "exam_data" not in st.session_state:
    st.session_state.exam_data = None

if st.button("নতুন প্ৰশ্নকাকত প্ৰস্তুত কৰক 📝"):
    with st.spinner("AI-য়ে প্ৰশ্নকাকত বনাই আছে... অনুগ্ৰহ কৰি ১০-১৫ ছেকেণ্ড অপেক্ষা কৰক।"):
        try:
            st.session_state.exam_data = generate_exam()
            st.session_state.submitted = False
        except Exception as e:
            st.error(f"এটা সমস্যা হৈছে। আপোনাৰ API Key টো শুদ্ধ নে পৰীক্ষা কৰক। Error: {e}")

# Display Exam
if st.session_state.exam_data:
    exam = st.session_state.exam_data
    
    st.markdown("### 📖 অনুচ্ছেদ (Passage):")
    st.info(exam["passage"])

    # Combine all questions
    questions = []
    for q in exam["comprehension_questions"]: questions.append(("বোধ পৰীক্ষা", q))
    for q in exam["grammar_questions"]: questions.append(("ব্যাকৰণ", q))
    for q in exam["pedagogy_questions"]: questions.append(("পেডাগজী", q))

    st.markdown("### ✍️ প্ৰশ্নসমূহ:")
    
    with st.form("exam_form"):
        user_answers = {}
        for i, (category, q) in enumerate(questions):
            st.markdown(f"**প্ৰশ্ন {i+1} [{category}]:** {q['question']}")
            user_answers[i] = st.radio("উত্তৰ বাছক:", q["options"], key=f"q_{i}", index=None)
            st.write("---")
        
        submitted = st.form_submit_button("পৰীক্ষা জমা দিয়ক (Submit)")

        if submitted:
            st.session_state.submitted = True
            st.session_state.score = sum([1 for i, (_, q) in enumerate(questions) if user_answers[i] == q["answer"]])
            st.session_state.total = len(questions)
            st.session_state.final_answers = user_answers

    # Show Results
    if st.session_state.get("submitted"):
        st.success(f"🎉 পৰীক্ষা সমাপ্ত! আপোনাৰ সৰ্বমুঠ স্ক'ৰ: {st.session_state.total} ৰ ভিতৰত **{st.session_state.score}**")
        st.markdown("### 📊 ফলাফল আৰু শুদ্ধ উত্তৰসমূহ:")
        
        for i, (category, q) in enumerate(questions):
            user_ans = st.session_state.final_answers[i]
            correct_ans = q["answer"]
            
            if user_ans == correct_ans:
                st.write(f"✅ **প্ৰশ্ন {i+1}:** শুদ্ধ! ({correct_ans})")
            else:
                st.write(f"❌ **প্ৰশ্ন {i+1}:** ভুল। \n- আপোনাৰ উত্তৰ: {user_ans} \n- **শুদ্ধ উত্তৰ: {correct_ans}**")
