import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [sessionId, setSessionId] = useState(null);

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! Welcome to Northstar Homes. How can I help you today?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [leadState, setLeadState] = useState({
    customer_name: null,
    language_used: null,
    budget_mentioned: null,
    configuration_interest: null,
    purpose: null,
    timeline: null,
    current_location: null,
    interest_level: null,
    objections_raised: [],
    site_visit_status: "not_offered",
    site_visit_datetime: null,
    follow_up_required: false,
    follow_up_preference: null,
    opt_out_requested: false,
    escalation_needed: false,
    site_visit_requested: false,
    requested_site_visit_slot: null,
  });

  const [error, setError] = useState("");

  const sendMessage = async () => {
    if (!input.trim() || loading || analytics) return;

    const userMessage = input.trim();

    setInput("");
    setError("");

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: userMessage,
      },
    ]);

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message.");
      }

      const data = await response.json();

      setSessionId(data.session_id);

      if (data.lead_state) {
        setLeadState(data.lead_state);
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.response,
        },
      ]);
    } catch (err) {
      setError(
        "Something went wrong while contacting the assistant."
      );
    } finally {
      setLoading(false);
    }
  };

  const endConversation = async () => {
    if (!sessionId || loading || analytics) return;

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/end-conversation?session_id=${encodeURIComponent(
          sessionId
        )}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to end conversation.");
      }

      const data = await response.json();

      setAnalytics(data.analytics);
    } catch (err) {
      setError(
        "Unable to generate conversation analytics."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const formatValue = (value, fallback = "Not provided") => {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return fallback;
    }

    return value;
  };

  const getInterestClass = () => {
    if (leadState.interest_level === "high") return "high";
    if (leadState.interest_level === "medium") return "medium";
    if (leadState.interest_level === "low") return "low";

    return "neutral";
  };

  const getBookingClass = () => {
    if (leadState.site_visit_status === "booked") {
      return "booked";
    }

    if (
      leadState.site_visit_status ===
      "attempted_failed"
    ) {
      return "failed";
    }

    return "neutral";
  };

  const qualificationFields = [
    leadState.customer_name,
    leadState.budget_mentioned,
    leadState.configuration_interest,
    leadState.purpose,
    leadState.timeline,
    leadState.current_location,
  ];

  const completedFields = qualificationFields.filter(
    (field) =>
      field !== null &&
      field !== undefined &&
      field !== ""
  ).length;

  const qualificationPercentage = Math.round(
    (completedFields / qualificationFields.length) * 100
  );

  return (
    <div className="app">

      <div className="dashboard">

        {/* =====================================================
            HEADER
        ===================================================== */}

        <header className="header">

          <div className="brand">

            <div className="brand-mark">
              N
            </div>

            <div>
              <h1>Northstar Homes</h1>
              <p>AI Sales & Site Visit Assistant</p>
            </div>

          </div>

          <div className="status">
            <span className="status-dot"></span>
            Online
          </div>

        </header>


        {/* =====================================================
            MAIN DASHBOARD
        ===================================================== */}

        <div className="dashboard-body">

          {/* =================================================
              CHAT SECTION
          ================================================= */}

          <section className="chat-panel">

            <div className="panel-title">
              <div>
                <h2>Conversation</h2>
                <p>
                  AI-powered customer qualification
                </p>
              </div>

              {sessionId && (
                <div className="session-badge">
                  Active session
                </div>
              )}
            </div>


            <main className="chat-area">

              {messages.map((message, index) => (

                <div
                  key={index}
                  className={`message-row ${message.role}`}
                >

                  <div
                    className={`message ${message.role}`}
                  >

                    {message.role === "assistant" && (
                      <div className="message-label">
                        Northstar AI
                      </div>
                    )}

                    {message.content}

                  </div>

                </div>

              ))}


              {loading && (

                <div className="message-row assistant">

                  <div className="message assistant typing">

                    <div className="message-label">
                      Northstar AI
                    </div>

                    <div className="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>

                  </div>

                </div>

              )}

            </main>


            {error && (
              <div className="error">
                {error}
              </div>
            )}


            {/* INPUT */}

            <div className="input-area">

              <textarea
                value={input}
                onChange={(event) =>
                  setInput(event.target.value)
                }
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                rows="1"
                disabled={loading || analytics}
              />

              <button
                onClick={sendMessage}
                disabled={
                  !input.trim() ||
                  loading ||
                  analytics
                }
              >
                Send
              </button>

            </div>


            <button
              className="end-button"
              onClick={endConversation}
              disabled={
                !sessionId ||
                loading ||
                analytics
              }
            >
              End Conversation
            </button>

          </section>


          {/* =================================================
              LEAD PANEL
          ================================================= */}

          <aside className="lead-panel">

            <div className="lead-panel-header">

              <div>
                <h2>Lead Profile</h2>
                <p>Live qualification data</p>
              </div>

              <div className="ai-badge">
                AI
              </div>

            </div>


            {/* Customer */}

            <div className="lead-section">

              <div className="section-label">
                CUSTOMER
              </div>

              <div className="customer-name">

                <div className="avatar">
                  {leadState.customer_name
                    ? leadState.customer_name
                        .charAt(0)
                        .toUpperCase()
                    : "?"}
                </div>

                <div>
                  <strong>
                    {formatValue(
                      leadState.customer_name
                    )}
                  </strong>

                  <span>
                    {formatValue(
                      leadState.language_used,
                      "Language not detected"
                    )}
                  </span>
                </div>

              </div>

            </div>


            {/* Requirements */}

            <div className="lead-section">

              <div className="section-label">
                REQUIREMENTS
              </div>

              <div className="lead-item">
                <span>Configuration</span>
                <strong>
                  {formatValue(
                    leadState.configuration_interest
                  )}
                </strong>
              </div>

              <div className="lead-item">
                <span>Budget</span>
                <strong>
                  {formatValue(
                    leadState.budget_mentioned
                  )}
                </strong>
              </div>

              <div className="lead-item">
                <span>Purpose</span>
                <strong>
                  {formatValue(
                    leadState.purpose
                  )}
                </strong>
              </div>

              <div className="lead-item">
                <span>Timeline</span>
                <strong>
                  {formatValue(
                    leadState.timeline
                  )}
                </strong>
              </div>

            </div>


            {/* Interest */}

            <div className="lead-section">

              <div className="section-label">
                LEAD INTEREST
              </div>

              <div className="interest-card">

                <span
                  className={`interest-dot ${getInterestClass()}`}
                ></span>

                <strong>
                  {formatValue(
                    leadState.interest_level,
                    "Not determined"
                  )}
                </strong>

              </div>

            </div>


            {/* Qualification */}

            <div className="lead-section">

              <div className="qualification-header">

                <div className="section-label">
                  QUALIFICATION
                </div>

                <strong>
                  {qualificationPercentage}%
                </strong>

              </div>

              <div className="progress-bar">

                <div
                  className="progress-fill"
                  style={{
                    width: `${qualificationPercentage}%`,
                  }}
                ></div>

              </div>

              <p className="progress-text">
                {completedFields} of{" "}
                {qualificationFields.length} key
                details captured
              </p>

            </div>


            {/* Site Visit */}

            <div className="lead-section">

              <div className="section-label">
                SITE VISIT
              </div>

              <div
                className={`booking-card ${getBookingClass()}`}
              >

                {leadState.site_visit_status ===
                "booked" ? (

                  <>
                    <div className="booking-icon">
                      ✓
                    </div>

                    <div>
                      <strong>
                        Visit Booked
                      </strong>

                      <span>
                        {formatValue(
                          leadState.site_visit_datetime
                        )}
                      </span>
                    </div>
                  </>

                ) : leadState.site_visit_status ===
                  "attempted_failed" ? (

                  <>
                    <div className="booking-icon">
                      !
                    </div>

                    <div>
                      <strong>
                        Slot Unavailable
                      </strong>

                      <span>
                        Another time is required
                      </span>
                    </div>
                  </>

                ) : (

                  <>
                    <div className="booking-icon neutral-icon">
                      —
                    </div>

                    <div>
                      <strong>
                        Not booked
                      </strong>

                      <span>
                        No site visit scheduled
                      </span>
                    </div>
                  </>

                )}

              </div>

            </div>


            {/* Follow-up */}

            <div className="lead-section">

              <div className="section-label">
                ACTIONS
              </div>

              <div className="action-row">

                <span>Follow-up</span>

                <span
                  className={
                    leadState.follow_up_required
                      ? "action-required"
                      : "action-normal"
                  }
                >
                  {leadState.follow_up_required
                    ? "Required"
                    : "Not required"}
                </span>

              </div>

              <div className="action-row">

                <span>Escalation</span>

                <span
                  className={
                    leadState.escalation_needed
                      ? "action-required"
                      : "action-normal"
                  }
                >
                  {leadState.escalation_needed
                    ? "Required"
                    : "Not required"}
                </span>

              </div>

            </div>

          </aside>

        </div>


        {/* =====================================================
            ANALYTICS
        ===================================================== */}

        {analytics && (

          <section className="analytics-panel">

            <div className="analytics-header">

              <div>
                <h2>Conversation Analytics</h2>
                <p>
                  Post-conversation lead insights
                </p>
              </div>

              <div className="completed-badge">
                ✓ Conversation completed
              </div>

            </div>


            <div className="analytics-cards">

              <div className="analytics-card">
                <span>Interest</span>
                <strong>
                  {formatValue(
                    analytics.interest_level,
                    "Not determined"
                  )}
                </strong>
              </div>

              <div className="analytics-card">
                <span>Qualification</span>
                <strong>
                  {analytics.qualification_completeness ??
                    0}
                  %
                </strong>
              </div>

              <div className="analytics-card">
                <span>Site Visit</span>
                <strong>
                  {analytics.site_visit_status}
                </strong>
              </div>

              <div className="analytics-card">
                <span>Conversation Turns</span>
                <strong>
                  {analytics.conversation_turns}
                </strong>
              </div>

            </div>


            <div className="analytics-bottom">

              <div className="analytics-summary">

                <div className="section-label">
                  CONVERSATION SUMMARY
                </div>

                <p>
                  {analytics.conversation_summary}
                </p>

              </div>


              <div className="next-action">

                <div className="section-label">
                  RECOMMENDED NEXT ACTION
                </div>

                <p>
                  {analytics.recommended_next_action}
                </p>

              </div>

            </div>

          </section>

        )}

      </div>

    </div>
  );
}

export default App;