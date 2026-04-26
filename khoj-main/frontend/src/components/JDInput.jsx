import { useState } from 'react'
import { FileText, Send } from 'lucide-react'

export default function JDInput({ onProcess, loading }) {
  const [text, setText] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (text.trim()) {
      onProcess(text)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <FileText className="w-5 h-5 text-primary" />
        <h3 className="text-lg font-medium text-white">Paste Job Description</h3>
      </div>
      
      <div className="relative group">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste the full job description text here... (e.g., Senior React Developer with 5+ years experience...)"
          className="w-full h-48 bg-zinc-950 border border-zinc-800 rounded-2xl p-4 text-zinc-300 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all resize-none placeholder:text-zinc-700"
          disabled={loading}
        />
        <div className="absolute inset-0 rounded-2xl bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-xl font-semibold hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary/20"
        >
          {loading ? 'Processing...' : 'Find Candidates'}
          <Send className="w-4 h-4" />
        </button>
      </div>
    </form>
  )
}
