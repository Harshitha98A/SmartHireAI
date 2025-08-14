# 📄⚡ SmartHireAI — The Resume Ranker That Doesn’t Complain

One-line: Your AI-powered resume screener that reads every word so you don’t have to.
SmartHireAI uses Google Gemini + Streamlit to rank resumes against your job description — fast, fair, and without the coffee jitters. ☕

## 💼 Why SmartHireAI Exists (aka The Recruiter Pain)

Recruiters, you know the drill:

You’ve seen “detail-oriented” so many times it’s starting to lose detail.

You meant to shortlist based on the JD… but three LinkedIn notifications later, you’re lost in page 5 of a CV.

You try to be thorough, but the stack is taller than your laptop screen. 📚

SmartHireAI fixes that.

Paste a JD 📝

Upload a pile of resumes 📂

Get a ranked, scored, and neatly commented shortlist — before your coffee cools.

## ✨ What SmartHireAI Does for You

🧠 Reads & Ranks → AI-powered evaluation with JD Match % for each resume.

💬 Quick Context Comments → Under 500 characters — the “why” behind the score.

📄 Batch Processing → Upload all the resumes at once — no one-by-one suffering.

⏱ Timeout & Retry Logic → AI won’t ghost you mid-search.

💾 Excel Export → Download a ready-to-share, ranked shortlist.

## 🛠 Tech Stack (Brains + Muscle)

Frontend/UI: Streamlit

AI Engine: Google Gemini API

Resume Parsing: PyPDF2

Data Wrangling: Pandas

Output: Excel via openpyxl

## ⚙️ How It Works

Paste your Job Description.

(Optional) Add recruiter notes like: “Must love APIs”.

Upload multiple PDF resumes.

SmartHireAI:

Scores each resume with JD Match %.

Writes a snappy Contextual Comment.

Ranks the list from top fit to “maybe next time.”

Download results as Excel.

## 💻 Run Locally
pip install -r requirements.txt
echo "GOOGLE_API_KEY=your_api_key_here" > .env
streamlit run smarthireai.py

### 📂 Project Layout
smarthireai/
├── smarthireai.py          # Main app
├── requirements.txt        # Dependencies
├── .env                    # API key
└── README.md               # You’re reading this

### 🎯 Demo Tips

Upload a mix of resumes — watch the rankings shuffle.

Add a funny requirement in “Additional Notes” and see how it affects scores. (Yes, SmartHireAI takes notes literally.)

Export to Excel and hand it to a hiring manager with: “Here’s your top 5 — you’re welcome.”

## 🫶 Why Recruiters Love It

Because screening shouldn’t feel like a part-time job.
SmartHireAI gets you from resume mountain to shortlist gold in minutes.
