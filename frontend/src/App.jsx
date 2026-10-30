
import { useState } from 'react'
import './App.css'

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
      const response = await fetch('https://ai-story-generator-10t8.onrender.com/api/generate-story', {
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

  return (
    <div className="app">
      <nav className="navbar">
        <a className="brand" href="#">
          <span className="brand-icon">âœ¦</span>
          StoryLearn <span>AI</span>
        </a>
        <a href="#about" className="nav-link">About</a>
      </nav>

      <main>
        <section className="hero">
          <div className="eyebrow">âœ¦ YOUR PERSONAL AI LEARNING COMPANION</div>

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
                {loading ? 'Generating...' : 'Generate Story â†’'}
              </button>
            </div>
            <p className="hint">âœ¨ Enter any topic and let AI explain it through a story.</p>
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
              <h2>{topic}</h2>
            </div>

            <article className="result-card">
              <h3>ðŸ“– Your Story</h3>
              <p className="story-text">{story.story}</p>
            </article>

            {story.steps?.length > 0 && (
              <article className="result-card">
                <h3>ðŸ§  Step-by-step Concept Flow</h3>
                <div className="steps">
                  {story.steps.map((step, index) => (
                    <div className="step" key={index}>
                      <span>{index + 1}</span>
                      <p>{step}</p>
                    </div>
                  ))}
                </div>
              </article>
            )}

            {story.key_points?.length > 0 && (
              <article className="result-card">
                <h3>â­ Key Takeaways</h3>
                {story.key_points.map((point, index) => (
                  <p className="key-point" key={index}>âœ“ {point}</p>
                ))}
              </article>
            )}

            {story.summary && (
              <article className="result-card summary">
                <h3>ðŸ“ Quick Summary</h3>
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
            <span>ðŸ“š</span>
            <h3>Simple Explanations</h3>
            <p>Understand difficult concepts in easy language.</p>
          </div>
          <div className="feature">
            <span>ðŸ’¡</span>
            <h3>Step-by-step Learning</h3>
            <p>Break down topics into manageable steps.</p>
          </div>
          <div className="feature">
            <span>âœ¨</span>
            <h3>AI Powered</h3>
            <p>Discover a smarter way to learn any subject.</p>
          </div>
        </section>
      </main>

      <footer>
        <p>âœ¦ StoryLearn AI â€” Making learning an adventure.</p>
      </footer>
    </div>
  )
}

export default App


