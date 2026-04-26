import { useState } from 'react'
import axios from 'axios'
import JDInput from './components/JDInput'
import ShortlistTable from './components/ShortlistTable'
import { Search, Loader2, Sparkles } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const API_BASE = 'http://localhost:8000'

function App() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleProcessJD = async (jdText) => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.post(`${API_BASE}/api/run`, { jd_text: jdText })
      setResults(response.data)
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Failed to process JD. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 selection:bg-primary selection:text-primary-foreground font-sans">
      {/* Background Glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-primary/20 blur-[120px] rounded-full" />
        <div className="absolute top-[20%] -right-[10%] w-[30%] h-[30%] bg-accent/10 blur-[100px] rounded-full" />
      </div>

      <main className="relative container mx-auto px-4 py-12 max-w-6xl">
        {/* Header */}
        <header className="text-center mb-16 space-y-4">
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-xs font-medium text-zinc-400 mb-2"
          >
            <Sparkles className="w-3 h-3 text-primary" />
            <span>AI-Powered Talent Scouting</span>
          </motion.div>
          <motion.h1 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-5xl md:text-6xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-500"
          >
            Talent Scout AI
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-zinc-400 text-lg max-w-2xl mx-auto"
          >
            Automate your hiring pipeline. Paste a job description and let our agent find, match, and engage the best candidates.
          </motion.p>
        </header>

        <div className="space-y-12">
          {/* Input Section */}
          <section className="bg-zinc-900/50 border border-zinc-800 rounded-3xl p-8 backdrop-blur-sm shadow-2xl">
            <JDInput onProcess={handleProcessJD} loading={loading} />
          </section>

          {/* Results Section */}
          <AnimatePresence mode="wait">
            {loading && (
              <motion.div 
                key="loading"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="flex flex-col items-center justify-center py-20 space-y-6"
              >
                <div className="relative">
                  <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full animate-pulse" />
                  <Loader2 className="w-12 h-12 text-primary animate-spin relative" />
                </div>
                <div className="text-center space-y-2">
                  <h3 className="text-xl font-medium text-white">Analyzing JD & Matching Candidates</h3>
                  <p className="text-zinc-500 text-sm animate-pulse">Running simulated outreach for top matches...</p>
                </div>
              </motion.div>
            )}

            {error && (
              <motion.div 
                key="error"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-center"
              >
                {error}
              </motion.div>
            )}

            {results && !loading && (
              <motion.section 
                key="results"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-white">Ranked Shortlist</h2>
                    <p className="text-zinc-500 text-sm">Found {results.shortlist.length} potential matches for {results.parsed_jd.role_title}</p>
                  </div>
                  <div className="flex gap-2">
                    <div className="px-3 py-1 rounded-lg bg-zinc-900 border border-zinc-800 text-xs">
                      <span className="text-zinc-500">Role:</span> <span className="text-zinc-300 font-medium">{results.parsed_jd.role_type}</span>
                    </div>
                    <div className="px-3 py-1 rounded-lg bg-zinc-900 border border-zinc-800 text-xs">
                      <span className="text-zinc-500">Exp:</span> <span className="text-zinc-300 font-medium">{results.parsed_jd.experience_years_required}+ yrs</span>
                    </div>
                  </div>
                </div>
                
                <ShortlistTable shortlist={results.shortlist} />
              </motion.section>
            )}
          </AnimatePresence>
        </div>
      </main>

      <footer className="py-12 border-t border-zinc-900 text-center text-zinc-600 text-sm">
        <p>&copy; 2026 Talent Scout AI. Built for Catalyst Hackathon.</p>
      </footer>
    </div>
  )
}

export default App
