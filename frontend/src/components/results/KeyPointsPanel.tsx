import { CopyButton } from '../shared/CopyButton'

interface KeyPointsPanelProps {
  keyPoints: string[]
}

export function KeyPointsPanel({ keyPoints }: KeyPointsPanelProps) {
  if (keyPoints.length === 0) return null

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
      <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-4">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-teal-600" />
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-900">Key Points</h3>
        </div>
        <CopyButton text={keyPoints.map((point) => `- ${point}`).join('\n')} label="Copy" />
      </div>

      <ul className="mt-5 space-y-3">
        {keyPoints.map((point, index) => (
          <li key={index} className="flex items-start gap-3 text-sm text-slate-700 leading-relaxed">
            <span
              aria-hidden="true"
              className="mt-1 flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full border border-teal-200 bg-teal-50 text-[10px] font-bold text-teal-700"
            >
              ✓
            </span>
            <span>{point}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
