interface SuggestionsPanelProps {
  suggestions: string[]
}

export function SuggestionsPanel({ suggestions }: SuggestionsPanelProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
      <div className="flex items-center gap-2 border-b border-slate-100 pb-4">
        <span className="h-2 w-2 rounded-full bg-amber-500" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-900">
          Improvement Suggestions
        </h3>
      </div>

      {suggestions.length === 0 ? (
        <div className="mt-5 flex items-center gap-2.5 rounded-xl border border-emerald-200 bg-emerald-50/50 p-4 text-xs font-medium text-emerald-800">
          <span>✓</span>
          <p>No significant issues were found in this document.</p>
        </div>
      ) : (
        <ol className="mt-5 space-y-3.5">
          {suggestions.map((suggestion, index) => (
            <li key={index} className="flex items-start gap-3.5 text-sm text-slate-700 leading-relaxed">
              <span
                aria-hidden="true"
                className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-md border border-amber-200 bg-amber-50 text-xs font-mono font-semibold text-amber-800"
              >
                {index + 1}
              </span>
              <span>{suggestion}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
