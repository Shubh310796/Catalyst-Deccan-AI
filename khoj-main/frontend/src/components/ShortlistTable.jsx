import { useState } from 'react'
import { User, MapPin, Briefcase, ChevronRight, MessageSquare, ShieldCheck, TrendingUp } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export default function ShortlistTable({ shortlist }) {
  const [selectedId, setSelectedId] = useState(null)

  return (
    <div className="grid grid-cols-1 gap-4">
      {shortlist.map((candidate, index) => (
        <div key={candidate.id} className="group">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => setSelectedId(selectedId === candidate.id ? null : candidate.id)}
            className={cn(
              "relative bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 cursor-pointer transition-all hover:bg-zinc-900/60 hover:border-zinc-700 overflow-hidden",
              selectedId === candidate.id && "ring-2 ring-primary/50 border-primary/50 bg-zinc-900/80"
            )}
          >
            {/* Rank Badge */}
            <div className="absolute top-0 right-0 px-4 py-1 bg-zinc-800 text-zinc-500 text-[10px] font-bold rounded-bl-xl tracking-widest uppercase">
              RANK #{index + 1}
            </div>

            <div className="flex flex-col md:flex-row md:items-center gap-6">
              {/* Profile Avatar */}
              <div className="flex-shrink-0">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-zinc-800 to-zinc-900 flex items-center justify-center border border-zinc-700 shadow-inner group-hover:scale-105 transition-transform">
                  <User className="w-8 h-8 text-zinc-500" />
                </div>
              </div>

              {/* Basic Info */}
              <div className="flex-grow space-y-1">
                <h4 className="text-xl font-bold text-white group-hover:text-primary transition-colors flex items-center gap-2">
                  {candidate.name}
                  {candidate.interest_score > 70 && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold uppercase">
                      <TrendingUp className="w-3 h-3" />
                      High Interest
                    </span>
                  )}
                </h4>
                <div className="flex flex-wrap items-center gap-4 text-sm text-zinc-500">
                  <span className="flex items-center gap-1">
                    <Briefcase className="w-3 h-3" />
                    {candidate.current_role}
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {candidate.location}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 text-xs">
                    {candidate.experience_years} yrs exp
                  </span>
                </div>
              </div>

              {/* Scores */}
              <div className="flex items-center gap-6">
                <div className="text-center">
                  <div className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider mb-1">Match Score</div>
                  <div className={cn(
                    "text-2xl font-black",
                    candidate.match_score >= 80 ? "text-emerald-500" : candidate.match_score >= 60 ? "text-amber-500" : "text-zinc-500"
                  )}>
                    {candidate.match_score}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider mb-1">Interest Score</div>
                  <div className={cn(
                    "text-2xl font-black",
                    candidate.interest_score >= 70 ? "text-emerald-500" : candidate.interest_score > 0 ? "text-amber-500" : "text-zinc-800"
                  )}>
                    {candidate.interest_score || '—'}%
                  </div>
                </div>
                <ChevronRight className={cn(
                  "w-5 h-5 text-zinc-700 transition-transform",
                  selectedId === candidate.id && "rotate-90 text-primary"
                )} />
              </div>
            </div>

            {/* Expanded Content */}
            <AnimatePresence>
              {selectedId === candidate.id && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden mt-6 pt-6 border-t border-zinc-800 space-y-6"
                >
                  {/* Explanation Section */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-xs font-bold text-zinc-400 uppercase tracking-widest">
                        <ShieldCheck className="w-4 h-4 text-emerald-500" />
                        Matching Explanation
                      </div>
                      <p className="text-sm text-zinc-400 leading-relaxed bg-zinc-950/50 p-4 rounded-xl border border-zinc-800/50">
                        {candidate.match_explanation}
                      </p>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-xs font-bold text-zinc-400 uppercase tracking-widest">
                        <MessageSquare className="w-4 h-4 text-primary" />
                        Engagement Summary
                      </div>
                      <p className="text-sm text-zinc-400 leading-relaxed bg-zinc-950/50 p-4 rounded-xl border border-zinc-800/50">
                        {candidate.interest_summary || "Outreach simulation was only conducted for top 5 candidates to optimize performance."}
                      </p>
                    </div>
                  </div>

                  {/* Skills Chips */}
                  <div className="space-y-3">
                    <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Candidate Skills</div>
                    <div className="flex flex-wrap gap-2">
                      {candidate.skills.map(skill => (
                        <span key={skill} className="px-3 py-1 rounded-full bg-zinc-800 text-zinc-300 text-xs font-medium border border-zinc-700/50">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Conversation Simulation */}
                  {candidate.conversation && candidate.conversation.length > 0 && (
                    <div className="space-y-4 pt-4">
                      <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Simulated Conversation</div>
                      <div className="space-y-3 max-h-60 overflow-y-auto p-4 bg-zinc-950 rounded-2xl border border-zinc-800 custom-scrollbar">
                        {candidate.conversation.map((msg, i) => (
                          <div key={i} className={cn(
                            "flex flex-col gap-1",
                            msg.speaker === 'Recruiter' ? "items-start" : "items-end"
                          )}>
                            <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-tighter">
                              {msg.speaker}
                            </span>
                            <div className={cn(
                              "max-w-[80%] px-4 py-2 rounded-2xl text-sm",
                              msg.speaker === 'Recruiter' 
                                ? "bg-zinc-900 text-zinc-300 rounded-tl-none border border-zinc-800" 
                                : "bg-primary/20 text-primary-foreground/90 rounded-tr-none border border-primary/20"
                            )}>
                              {msg.text}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      ))}
    </div>
  )
}
