# StoryLearn AI 🚀

**Learn anything. Through stories.**

StoryLearn AI is an AI-powered learning platform that transforms complex topics into simple, engaging stories. It uses Google Gemini to generate student-friendly explanations, step-by-step concept flows and key learning points.

🌐 **Live Demo:** https://storylearnai.pages.dev/

## ✨ Features

- **AI Story Generation:** Convert any topic into an easy-to-understand educational story.
- **Step-by-Step Learning:** Understand complex concepts through structured explanations.
- **Key Points:** Get the most important information highlighted.
- **AI-Powered Learning:** Uses Google Gemini for intelligent content generation.
- **Responsive Interface:** Clean and user-friendly React interface.
- **Instant Results:** Generate learning content by entering any topic.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| React.js | Frontend development |
| Vite | Frontend build tool |
| Python | Backend development |
| FastAPI | REST API |
| Google Gemini | AI story generation |
| Cloudflare Pages | Frontend deployment |
| Render | Backend hosting |
| GitHub | Version control |

## 🏗️ Project Architecture

```text
StoryLearn-AI/
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── index.html
│
├── backend/
│   └── main.py
│
├── ai_engine.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Soumyasriau/AI-Story-Generator.git
cd AI-Story-Generator
```

### 2. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Gemini API

Create a `.env` file in the project root directory:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
```

Get your API key from [Google AI Studio](https://aistudio.google.com/).

**Important:** Never upload your `.env` file or API key to GitHub.

### 4. Start the backend

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Backend API documentation:

http://localhost:8000/docs

### 5. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

## 🌍 Live Deployment

- **Frontend:** https://storylearnai.pages.dev/
- **Backend API:** https://ai-story-generator-10t8.onrender.com/
- **API Documentation:** https://ai-story-generator-10t8.onrender.com/docs

## 🔐 Environment Variables

| Variable | Description |
|---|---|
| GEMINI_API_KEY | Google Gemini API key |
| GEMINI_MODEL | Gemini model used for story generation |

## ⚠️ Error Handling

- Gemini API errors are handled by the backend.
- API quota limits may temporarily prevent story generation.
- A valid Gemini API key is required.
- The backend must be running for story generation to work.

## 🚀 Future Enhancements

- Download generated stories as PDF.
- Text-to-speech functionality.
- Multiple language support.
- Story length and difficulty selection.
- Save and revisit generated stories.

## 👩‍💻 Author

**Soumya**

GitHub: https://github.com/Soumyasriau

---

⭐ If you find StoryLearn AI interesting, consider giving this repository a star!
