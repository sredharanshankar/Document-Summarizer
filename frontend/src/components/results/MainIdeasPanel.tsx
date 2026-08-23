interface MainIdeasPanelProps {
  mainIdeas: string[]
}

export function MainIdeasPanel({ mainIdeas }: MainIdeasPanelProps) {
  if (mainIdeas.length === 0) return null

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
      <div className="flex items-center gap-2 border-b border-slate-100 pb-4">
        <span className="h-2 w-2 rounded-full bg-slate-700" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-900">Main Ideas</h3>
      </div>

      <ol className="mt-5 space-y-3.5">
        {mainIdeas.map((idea, index) => (
          <li key={index} className="flex items-start gap-3.5 text-sm text-slate-700 leading-relaxed">
            <span
              aria-hidden="true"
              className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-md border border-slate-200 bg-slate-50 text-xs font-mono font-semibold text-slate-700"
            >
              {index + 1}
            </span>
            <span>{idea}</span>
          </li>
        ))}
      </ol>
    </div>
  )
}
