import { useState, type FormEvent } from 'react'
import { useCompareQuestion } from '../../hooks/useCompareQuestion'
import { ChatIcon } from '../shared/icons'

interface AskCompareQuestionPanelProps {
  jobIds: string[]
}

export function AskCompareQuestionPanel({ jobIds }: AskCompareQuestionPanelProps) {
  const [question, setQuestion] = useState('')
  const { history, isAsking, error, ask } = useCompareQuestion(jobIds)

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    if (!question.trim() || isAsking) return
    void ask(question)
    setQuestion('')
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
      <div className="flex items-center gap-2 border-b border-slate-100 pb-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-800">
          <ChatIcon className="h-4 w-4" />
        </div>
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-900">
            Ask Across Documents
          </h3>
          <p className="text-xs text-slate-500">
            Ask any question comparing these documents — responses are grounded across all selected files.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="mt-5 flex flex-col gap-2.5 sm:flex-row">
        <label htmlFor="compare-question" className="sr-only">
          Your question about these compared documents
        </label>
        <input
          id="compare-question"
          type="text"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="e.g. How do the key terms or figures differ between these documents?"
          disabled={isAsking}
          className="flex-1 rounded-xl border border-slate-300 bg-slate-50/50 px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-900 focus:bg-white disabled:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
        />
        <button
          type="submit"
          disabled={isAsking || !question.trim()}
          className="inline-flex items-center justify-center rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.99] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
        >
          {isAsking ? 'Asking...' : 'Ask'}
        </button>
      </form>

      {error && (
        <div role="alert" className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3.5 text-xs text-red-700">
          {error}
        </div>
      )}

      {history.length === 0 && !error && (
        <p className="mt-5 text-center text-xs text-slate-400">No questions asked yet.</p>
      )}

      {history.length > 0 && (
        <ul className="mt-6 space-y-4" aria-live="polite">
          {history
            .slice()
            .reverse()
            .map((item) => (
              <li
                key={item.id}
                className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 transition-colors"
              >
                <div className="flex items-start gap-2 text-sm font-semibold text-slate-900">
                  <span className="rounded bg-slate-200 px-1.5 py-0.5 text-[10px] font-mono text-slate-700">
                    Q
                  </span>
                  <span>Q: {item.question}</span>
                </div>
                <div className="mt-2.5 border-t border-slate-200/60 pt-2.5 text-sm leading-relaxed text-slate-700">
                  <p>{item.answer}</p>
                </div>
              </li>
            ))}
        </ul>
      )}
    </div>
  )
}
