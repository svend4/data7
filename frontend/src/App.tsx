import { useState } from 'react'
import { AgentRegistry } from './components/AgentRegistry'
import { SwitchboardStats } from './components/SwitchboardStats'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">
          🎭 Meta-Orchestrator Switchboard
        </h1>
        <p className="app-subtitle">
          Art Deco 1920s Telephonic Exchange for Multi-Agent AI Systems
        </p>
      </header>

      <main className="app-main">
        <SwitchboardStats />
        <AgentRegistry />
      </main>

      <footer className="app-footer">
        <p>Phase 0: MVP Foundation | Version 0.1.0</p>
      </footer>
    </div>
  )
}

export default App
