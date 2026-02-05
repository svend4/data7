/**
 * Knowledge Transformation System UI
 *
 * Web interface for transforming scientific knowledge:
 * - Dissertations → Encyclopedias (decomposition + aggregation)
 * - Encyclopedias → Dissertations (decomposition + synthesis)
 */

import React, { useState } from 'react';
import { axiosClient } from '../lib/axios';

interface Fact {
  subject: string;
  predicate: string;
  object: string;
  certainty: number;
  context?: string;
}

interface DissertationProposal {
  title: string;
  description: string;
  novelty: number;
  impact: number;
  feasibility: number;
  gap_type: string;
  research_questions: string[];
  expected_contributions: string[];
}

type TransformMode = 'dissertation_to_wiki' | 'wiki_to_dissertation';

export const KnowledgeSystem: React.FC = () => {
  const [mode, setMode] = useState<TransformMode>('wiki_to_dissertation');
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [facts, setFacts] = useState<Fact[]>([]);
  const [proposals, setProposals] = useState<DissertationProposal[]>([]);
  const [error, setError] = useState('');

  const handleTransform = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text');
      return;
    }

    setLoading(true);
    setError('');
    setFacts([]);
    setProposals([]);

    try {
      if (mode === 'wiki_to_dissertation') {
        // Step 1: Decompose Wikipedia text into facts
        const decomposeRes = await axiosClient.post('/api/knowledge/decompose/wiki', {
          text: inputText,
          metadata: { source: 'user_input' }
        });

        const extractedFacts: Fact[] = decomposeRes.data.facts;
        setFacts(extractedFacts);

        // Step 2: Synthesize dissertation proposals
        if (extractedFacts.length > 0) {
          const synthesizeRes = await axiosClient.post('/api/knowledge/synthesize/dissertation', {
            facts: extractedFacts,
            domain: 'general',
            min_novelty: 0.5
          });

          setProposals(synthesizeRes.data.proposals);
        }
      } else {
        // Dissertation to Wiki mode (future implementation)
        setError('Dissertation → Wiki transformation coming soon!');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Transformation failed');
      console.error('Transformation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setInputText('');
    setFacts([]);
    setProposals([]);
    setError('');
  };

  const loadSampleWiki = () => {
    setInputText(`Machine Learning is a branch of artificial intelligence. Neural Networks are computational models inspired by biological neurons. Deep Learning uses neural networks with multiple layers. Convolutional Neural Networks are used for image recognition. Recurrent Neural Networks process sequential data. Transformers have revolutionized natural language processing. GPT models are based on transformer architecture. Machine Learning requires large datasets for training. Supervised Learning uses labeled data. Unsupervised Learning finds patterns in unlabeled data.`);
  };

  return (
    <div className="knowledge-system-page">
      <div className="page-header">
        <h1>🧠 Knowledge Transformation System</h1>
        <p className="subtitle">Transform scientific knowledge between formats</p>
      </div>

      <div className="content-wrapper">
        {/* Mode Selector */}
        <div className="mode-selector">
          <button
            className={`mode-btn ${mode === 'wiki_to_dissertation' ? 'active' : ''}`}
            onClick={() => setMode('wiki_to_dissertation')}
          >
            📚 Encyclopedia → 🎓 Dissertation Ideas
          </button>
          <button
            className={`mode-btn ${mode === 'dissertation_to_wiki' ? 'active' : ''}`}
            onClick={() => setMode('dissertation_to_wiki')}
            disabled
          >
            🎓 Dissertation → 📚 Encyclopedia (Coming Soon)
          </button>
        </div>

        {/* Input Section */}
        <div className="input-section">
          <div className="section-header">
            <h2>{mode === 'wiki_to_dissertation' ? '📖 Wikipedia Text' : '📝 Dissertation Text'}</h2>
            <button className="sample-btn" onClick={loadSampleWiki}>
              Load Sample
            </button>
          </div>

          <textarea
            className="text-input"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={
              mode === 'wiki_to_dissertation'
                ? 'Paste Wikipedia article text here...'
                : 'Paste dissertation text here...'
            }
            rows={10}
            disabled={loading}
          />

          <div className="action-buttons">
            <button className="transform-btn" onClick={handleTransform} disabled={loading || !inputText}>
              {loading ? (
                <>
                  <span className="spinner" />
                  Processing...
                </>
              ) : (
                <>
                  ⚡ Transform
                </>
              )}
            </button>
            <button className="clear-btn" onClick={handleClear} disabled={loading}>
              Clear
            </button>
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {(facts.length > 0 || proposals.length > 0) && (
          <div className="results-section">
            {/* Facts */}
            {facts.length > 0 && (
              <div className="facts-panel">
                <h2>🔬 Extracted Facts ({facts.length})</h2>
                <div className="facts-list">
                  {facts.slice(0, 20).map((fact, idx) => (
                    <div key={idx} className="fact-card">
                      <div className="fact-content">
                        <span className="subject">{fact.subject}</span>
                        <span className="predicate">{fact.predicate.replace(/_/g, ' ')}</span>
                        <span className="object">{fact.object}</span>
                      </div>
                      <div className="fact-meta">
                        <span className="certainty">
                          Certainty: {(fact.certainty * 100).toFixed(0)}%
                        </span>
                      </div>
                      {fact.context && (
                        <div className="fact-context">
                          "{fact.context.substring(0, 100)}..."
                        </div>
                      )}
                    </div>
                  ))}
                  {facts.length > 20 && (
                    <div className="more-indicator">
                      + {facts.length - 20} more facts...
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Dissertation Proposals */}
            {proposals.length > 0 && (
              <div className="proposals-panel">
                <h2>💡 Dissertation Proposals ({proposals.length})</h2>
                <div className="proposals-list">
                  {proposals.map((proposal, idx) => (
                    <div key={idx} className="proposal-card">
                      <div className="proposal-header">
                        <h3>{proposal.title}</h3>
                        <div className="proposal-badges">
                          <span className="badge novelty">
                            Novelty: {(proposal.novelty * 100).toFixed(0)}%
                          </span>
                          <span className="badge impact">
                            Impact: {(proposal.impact * 100).toFixed(0)}%
                          </span>
                          <span className="badge feasibility">
                            Feasibility: {(proposal.feasibility * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>

                      <p className="proposal-description">{proposal.description}</p>

                      {proposal.research_questions.length > 0 && (
                        <div className="proposal-section">
                          <h4>Research Questions:</h4>
                          <ul>
                            {proposal.research_questions.map((q, qIdx) => (
                              <li key={qIdx}>{q}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {proposal.expected_contributions.length > 0 && (
                        <div className="proposal-section">
                          <h4>Expected Contributions:</h4>
                          <ul>
                            {proposal.expected_contributions.map((c, cIdx) => (
                              <li key={cIdx}>{c}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      <div className="proposal-footer">
                        <span className="gap-type">Gap Type: {proposal.gap_type}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <style>{`
        .knowledge-system-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
          padding: 2rem;
          color: #fff;
        }

        .page-header {
          text-align: center;
          margin-bottom: 2rem;
          padding-bottom: 2rem;
          border-bottom: 2px solid #d4af37;
        }

        .page-header h1 {
          font-size: 2.5rem;
          color: #d4af37;
          margin-bottom: 0.5rem;
        }

        .subtitle {
          color: #999;
          font-size: 1.1rem;
        }

        .content-wrapper {
          max-width: 1400px;
          margin: 0 auto;
        }

        /* Mode Selector */
        .mode-selector {
          display: flex;
          gap: 1rem;
          margin-bottom: 2rem;
          justify-content: center;
        }

        .mode-btn {
          padding: 1rem 2rem;
          font-size: 1.1rem;
          background: #2a2a2a;
          border: 2px solid #444;
          color: #fff;
          cursor: pointer;
          border-radius: 8px;
          transition: all 0.3s ease;
        }

        .mode-btn:hover:not(:disabled) {
          border-color: #d4af37;
          background: #333;
        }

        .mode-btn.active {
          border-color: #d4af37;
          background: rgba(212, 175, 55, 0.1);
        }

        .mode-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* Input Section */
        .input-section {
          background: #2a2a2a;
          border: 2px solid #d4af37;
          border-radius: 8px;
          padding: 2rem;
          margin-bottom: 2rem;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .section-header h2 {
          color: #d4af37;
          font-size: 1.5rem;
          margin: 0;
        }

        .sample-btn {
          padding: 0.5rem 1rem;
          background: #444;
          border: 1px solid #666;
          color: #fff;
          border-radius: 4px;
          cursor: pointer;
          transition: background 0.3s ease;
        }

        .sample-btn:hover {
          background: #555;
        }

        .text-input {
          width: 100%;
          padding: 1rem;
          background: #1a1a1a;
          border: 1px solid #444;
          color: #fff;
          border-radius: 4px;
          font-size: 1rem;
          font-family: monospace;
          resize: vertical;
          margin-bottom: 1rem;
        }

        .text-input:focus {
          outline: none;
          border-color: #d4af37;
        }

        .text-input:disabled {
          opacity: 0.5;
        }

        /* Action Buttons */
        .action-buttons {
          display: flex;
          gap: 1rem;
        }

        .transform-btn {
          flex: 1;
          padding: 1rem;
          background: #d4af37;
          border: none;
          color: #1a1a1a;
          font-size: 1.1rem;
          font-weight: 600;
          border-radius: 4px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          transition: background 0.3s ease;
        }

        .transform-btn:hover:not(:disabled) {
          background: #f0c84a;
        }

        .transform-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .clear-btn {
          padding: 1rem 2rem;
          background: #444;
          border: 1px solid #666;
          color: #fff;
          font-size: 1rem;
          border-radius: 4px;
          cursor: pointer;
          transition: background 0.3s ease;
        }

        .clear-btn:hover:not(:disabled) {
          background: #555;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid #1a1a1a;
          border-top: 2px solid transparent;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .error-message {
          margin-top: 1rem;
          padding: 1rem;
          background: rgba(255, 0, 0, 0.1);
          border: 1px solid rgba(255, 0, 0, 0.3);
          border-radius: 4px;
          color: #ff6b6b;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        /* Results Section */
        .results-section {
          display: grid;
          gap: 2rem;
        }

        /* Facts Panel */
        .facts-panel {
          background: #2a2a2a;
          border: 2px solid #4a90e2;
          border-radius: 8px;
          padding: 2rem;
        }

        .facts-panel h2 {
          color: #4a90e2;
          margin-bottom: 1.5rem;
        }

        .facts-list {
          display: grid;
          gap: 1rem;
        }

        .fact-card {
          background: #1a1a1a;
          border: 1px solid #444;
          border-radius: 4px;
          padding: 1rem;
        }

        .fact-content {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .subject {
          color: #4a90e2;
          font-weight: 600;
        }

        .predicate {
          color: #999;
          font-style: italic;
          padding: 0.25rem 0.5rem;
          background: #2a2a2a;
          border-radius: 4px;
        }

        .object {
          color: #f0c84a;
        }

        .fact-meta {
          color: #666;
          font-size: 0.9rem;
        }

        .certainty {
          color: #28a745;
        }

        .fact-context {
          margin-top: 0.5rem;
          padding-top: 0.5rem;
          border-top: 1px solid #333;
          color: #999;
          font-size: 0.9rem;
          font-style: italic;
        }

        .more-indicator {
          text-align: center;
          padding: 1rem;
          color: #666;
          font-style: italic;
        }

        /* Proposals Panel */
        .proposals-panel {
          background: #2a2a2a;
          border: 2px solid #9b59b6;
          border-radius: 8px;
          padding: 2rem;
        }

        .proposals-panel h2 {
          color: #9b59b6;
          margin-bottom: 1.5rem;
        }

        .proposals-list {
          display: grid;
          gap: 1.5rem;
        }

        .proposal-card {
          background: #1a1a1a;
          border: 1px solid #9b59b6;
          border-radius: 8px;
          padding: 1.5rem;
        }

        .proposal-header {
          margin-bottom: 1rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #333;
        }

        .proposal-header h3 {
          color: #d4af37;
          margin-bottom: 0.5rem;
          font-size: 1.3rem;
        }

        .proposal-badges {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .badge {
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.85rem;
          font-weight: 600;
        }

        .badge.novelty {
          background: rgba(155, 89, 182, 0.2);
          color: #9b59b6;
          border: 1px solid #9b59b6;
        }

        .badge.impact {
          background: rgba(231, 76, 60, 0.2);
          color: #e74c3c;
          border: 1px solid #e74c3c;
        }

        .badge.feasibility {
          background: rgba(40, 167, 69, 0.2);
          color: #28a745;
          border: 1px solid #28a745;
        }

        .proposal-description {
          color: #ccc;
          line-height: 1.6;
          margin-bottom: 1rem;
        }

        .proposal-section {
          margin: 1rem 0;
        }

        .proposal-section h4 {
          color: #d4af37;
          font-size: 1rem;
          margin-bottom: 0.5rem;
        }

        .proposal-section ul {
          margin: 0;
          padding-left: 1.5rem;
          color: #999;
        }

        .proposal-section li {
          margin: 0.25rem 0;
          line-height: 1.5;
        }

        .proposal-footer {
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid #333;
          color: #666;
          font-size: 0.9rem;
        }

        .gap-type {
          text-transform: capitalize;
        }

        /* Responsive */
        @media (max-width: 768px) {
          .page-header h1 {
            font-size: 2rem;
          }

          .mode-selector {
            flex-direction: column;
          }

          .action-buttons {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};
