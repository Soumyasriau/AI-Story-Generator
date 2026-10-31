import { useState } from 'react'
import './App.css'

const API_URL = 'https://ai-story-generator-10t8.onrender.com/api/generate-story'
// For local testing, change the line above to:
// const API_URL = 'http://localhost:8000/api/generate-story'

function App() {
  const [topic, setTopic] = useState('')
  const [story, setStory] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const generateStory = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic first.')
      return
    }

    setLoading(true)
    setError('')
    setStory(null)

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Story generation failed')
      }

      setStory(data.result)
    } catch (err) {
      setError(err.message || 'Unable to connect to AI server.')
    } finally {
      setLoading(false)
    }
  }

  // Only show pictures the backend has already checked and sent as image data.
  const safeImages = (story?.images || []).filter(
    (src) => typeof src === 'string' && src.startsWith('data:image/')
  )

  return (
    <div className="app">
      <nav className="navbar">
        <a className="brand" href="#">
          <span className="brand-icon">{"\u2728"}</span>
          StoryLearn <span>AI</span>
        </a>
        <a href="#about" className="nav-link">About</a>
      </nav>

      <main>
        <section className="hero">
          <div className="eyebrow">{"\u2728"} YOUR PERSONAL AI LEARNING COMPANION</div>

          <h1>
            Learn anything.
            <br />
            <span>Through stories.</span>
          </h1>

          <p className="hero-text">
            Turn complex topics into simple, engaging stories.
            Understand concepts, explore ideas and learn smarter with AI.
          </p>

          <div className="generator">
            <label htmlFor="topic">What would you like to learn today?</label>
            <div className="input-row">
              <input
                id="topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && generateStory()}
                placeholder="e.g. Artificial Intelligence, Photosynthesis..."
              />
              <button onClick={generateStory} disabled={loading}>
                {loading ? 'Generating...' : 'Generate Story'}
              </button>
            </div>
            <p className="hint">{"\u2728"} Enter any topic and let AI explain it through a story.</p>
          </div>

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              Creating your learning story...
            </div>
          )}

          {error && <div className="error">{error}</div>}
        </section>

        {story && (
          <section className="results">
            <div className="result-heading">
              <span className="result-tag">YOUR AI-GENERATED LESSON</span>
              <h2>{story.title || topic}</h2>
            </div>

            <article className="result-card">
              <h3>{"\u{1F4D6} Your Story"}</h3>
              <p className="story-text">{story.story}</p>
            </article>

            {safeImages.length > 0 && (
              <article className="result-card">
                <h3>{"\u{1F5BC}\uFE0F Pictures"}</h3>
                <div className="gallery">
                  {safeImages.map((src, index) => (
                    <img key={index} src={src} alt={`${topic} picture ${index + 1}`} />
                  ))}
                </div>
              </article>
            )}

            {story.steps?.length > 0 && (
              <article className="result-card">
                <h3>{"\u{1F9E9} Step-by-step Concept Flow"}</h3>
                <div className="steps">
                  {story.steps.map((step, index) => (
                    <div className="step" key={index}>
                      <span>{index + 1}</span>
                      <p>
                        {story.step_icons?.[index] ? story.step_icons[index] + ' ' : ''}
                        {step}
                      </p>
                    </div>
                  ))}
                </div>
              </article>
            )}

            {story.key_points?.length > 0 && (
              <article className="result-card">
                <h3>Key Points</h3>
                {story.key_points.map((point, index) => (
                  <p className="key-point" key={index}>{"\u2022"} {point}</p>
                ))}
              </article>
            )}

            {story.summary && (
              <article className="result-card summary">
                <h3>Summary</h3>
                <p>{story.summary}</p>
              </article>
            )}

            <button className="new-button" onClick={() => {
              setStory(null)
              setTopic('')
            }}>
              Generate Another Story
            </button>
          </section>
        )}

        <section className="features" id="about">
          <div className="feature">
            <span>{"\u{1F4D6}"}</span>
            <h3>Simple Explanations</h3>
            <p>Understand difficult concepts in easy language.</p>
          </div>
          <div className="feature">
            <span>{"\u{1F3AF}"}</span>
            <h3>Step-by-step Learning</h3>
            <p>Break down topics into manageable steps.</p>
          </div>
          <div className="feature">
            <span>{"\u2728"}</span>
            <h3>AI Powered</h3>
            <p>Discover a smarter way to learn any subject.</p>
          </div>
        </section>
      </main>

      <footer>
        <p>{"\u00A9"} StoryLearn AI</p>
      </footer>
    </div>
  )
}

export default App