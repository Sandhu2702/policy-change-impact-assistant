import { useEffect, useState } from "react";
import { askPolicyQuestion, getPolicyChanges } from "./api";
import "./App.css";

const POLICIES = [
  "Annual Leave Policy",
  "Work From Home Policy",
  "Travel Reimbursement Policy",
  "Confidential Data Sharing Policy",
];

function App() {
  const [policyName, setPolicyName] = useState(POLICIES[0]);
  const [question, setQuestion] = useState("");
  const [changes, setChanges] = useState([]);
  const [answer, setAnswer] = useState(null);
  const [loadingChanges, setLoadingChanges] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadChanges() {
      setLoadingChanges(true);
      setError("");
      setAnswer(null);

      try {
        const data = await getPolicyChanges(policyName);
        if (!cancelled) {
          setChanges(data.changes ?? []);
        }
      } catch (err) {
        if (!cancelled) {
          setChanges([]);
          setError(err.message || "Could not load policy changes.");
        }
      } finally {
        if (!cancelled) setLoadingChanges(false);
      }
    }

    loadChanges();

    return () => {
      cancelled = true;
    };
  }, [policyName]);

  async function handleAskQuestion(event) {
    event.preventDefault();

    if (!question.trim() || asking) return;

    setAsking(true);
    setAnswer(null);
    setError("");

    try {
      const data = await askPolicyQuestion(policyName, question.trim());
      setAnswer(data);
    } catch (err) {
      setError(err.message || "Could not get an answer.");
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">P</div>
          <span>PolicyImpact</span>
        </div>
        <span className="status">● Backend-powered assistant</span>
      </header>

      <main className="dashboard">
        <section className="hero">
          <p className="eyebrow">POLICY INTELLIGENCE</p>
          <h1>Understand what changed.</h1>
          <p className="subtitle">
            Compare policy versions, explore important changes, and get
            answers backed by policy evidence.
          </p>
        </section>

        <section className="panel">
          <div className="section-heading">
            <div>
              <h2>Explore a policy</h2>
              <p>Select a policy to see its recorded changes.</p>
            </div>
            <span className="step-label">01 / POLICY</span>
          </div>

          <label htmlFor="policy">Policy name</label>
          <select
            id="policy"
            value={policyName}
            onChange={(event) => setPolicyName(event.target.value)}
          >
            {POLICIES.map((policy) => (
              <option key={policy} value={policy}>
                {policy}
              </option>
            ))}
          </select>

          {loadingChanges ? (
            <p className="result-message">Loading policy changes...</p>
          ) : changes.length > 0 ? (
            <div className="changes-list">
              {changes.map((change) => (
                <article className="change-card" key={change.id}>
                  <div className="change-heading">
                    <span className={`change-type ${change.change_type.toLowerCase()}`}>
                      {change.change_type}
                    </span>
                    <span className="change-versions">
                      {change.old_version} → {change.new_version}
                    </span>
                  </div>
                  <h3>{change.section}</h3>
                  {change.old_text && (
                    <div className="policy-text">
                      <span>Previous</span>
                      <p>{change.old_text}</p>
                    </div>
                  )}
                  {change.new_text && (
                    <div className="policy-text updated">
                      <span>Updated</span>
                      <p>{change.new_text}</p>
                    </div>
                  )}
                </article>
              ))}
            </div>
          ) : (
            !error && (
              <p className="result-message">
                No recorded changes found for this policy.
              </p>
            )
          )}
        </section>

        <section className="panel">
          <div className="section-heading">
            <div>
              <h2>Ask your policy</h2>
              <p>Get answers grounded in recorded policy changes.</p>
            </div>
            <span className="step-label">02 / ASK</span>
          </div>

          <form onSubmit={handleAskQuestion}>
            <label htmlFor="question">Your question</label>
            <textarea
              id="question"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="e.g. How many annual leave days can employees carry over?"
              rows={4}
            />

            <button
              className="ask-button"
              type="submit"
              disabled={!question.trim() || asking}
            >
              {asking ? "Getting answer..." : "Ask a question"}
              <span>→</span>
            </button>
          </form>

          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}

          {answer && (
            <div className="answer-card" aria-live="polite">
              <h3>Answer</h3>
              <p className="answer-text">{answer.answer}</p>

              {answer.citations?.length > 0 && (
                <div className="citations">
                  <h4>Policy evidence</h4>
                  {answer.citations.map((citation, index) => (
                    <div
                      className="citation-item"
                      key={`${citation.section}-${index}`}
                    >
                      <strong>{citation.section}</strong>
                      <span>
                        {citation.old_version} → {citation.new_version}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </section>

        <footer>
          Policy Change Impact Assistant <span>•</span> Evidence-led answers
        </footer>
      </main>
    </div>
  );
}

export default App;