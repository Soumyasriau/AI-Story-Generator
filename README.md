# StoryLearn AI

StoryLearn AI is a Streamlit app that generates story-style, student-friendly explanations for any topic, fetches relevant educational images, and produces a downloadable PDF.

## Features
- Story-style, technically accurate explanations via OpenAI
- Step-by-step concept flow and highlighted key points
- Automatic download of 3–5 educational images (Bing Image Downloader)
- PDF export with images (ReportLab)
- Modern UI styling and responsive layout

## Setup

1. Create and activate a Python virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r storylearn_ai\requirements.txt
```

2. Set your OpenAI API key as an environment variable:

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

3. Run the app:

```powershell
streamlit run storylearn_ai\app.py
```

## Files
- `storylearn_ai/app.py`: Streamlit frontend
- `storylearn_ai/ai_engine.py`: AI generation wrapper
- `storylearn_ai/image_fetcher.py`: Image downloader
- `storylearn_ai/pdf_generator.py`: PDF builder using ReportLab
- `storylearn_ai/assets/style.css`: CSS for modern UI

## Notes & Error Handling
- The app expects `OPENAI_API_KEY` set in the environment.
- Image downloads rely on `bing-image-downloader`. If network or service fails, the app will continue and still produce text and PDF (possibly without images).
- The AI is asked to return JSON. If parsing fails, the raw story will still display.

## Next steps / Improvements
- Support additional model providers (Gemini/Llama)
- Add caching for topic results
- Add more polished animations and accessibility improvements
