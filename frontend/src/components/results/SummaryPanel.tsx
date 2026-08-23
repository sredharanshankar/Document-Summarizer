import { CopyButton } from '../shared/CopyButton'
import type { SummaryLength } from '../../types/document'

interface SummaryPanelProps {
  summary: string
  summaryLength: SummaryLength
  isRegenerating: boolean
  error: string | null
  onLengthChange: (length: SummaryLength) => void
}

const LENGTH_OPTIONS: { value: SummaryLength; label: string }[] = [
  { value: 'short', label: 'Short' },
  { value: 'medium', label: 'Medium' },
  { value: 'long', label: 'Long' },
]

export function SummaryPanel({
  summary,
  summaryLength,
  isRegenerating,
  error,
  onLengthChange,
}: SummaryPanelProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-slate-900" />
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-900">
            Executive Summary
          </h3>
        </div>

        <div className="flex items-center gap-2">
          <div
            className="flex gap-1 rounded-xl border border-slate-200 bg-slate-50 p-1"
            role="radiogroup"
            aria-label="Summary length"
          >
            {LENGTH_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                role="radio"
                aria-checked={summaryLength === option.value}
                disabled={isRegenerating}
                onClick={() => onLengthChange(option.value)}
                className={`rounded-lg px-3 py-1 text-xs font-semibold transition-all disabled:cursor-not-allowed disabled:opacity-60 ${
                  summaryLength === option.value
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
          <CopyButton text={summary} label="Copy" />
        </div>
      </div>

      {error && (
        <div role="alert" className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3.5 text-xs text-red-700">
          {error}
        </div>
      )}

      <div className="relative mt-5">
        {isRegenerating && (
          <div className="absolute inset-0 flex items-center justify-center rounded-xl bg-white/70 backdrop-blur-xs">
            <span className="rounded-lg border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-700 shadow-xs animate-flat-pulse">
              Synthesizing new depth...
            </span>
          </div>
        )}
        <p
          className={`whitespace-pre-line text-sm leading-relaxed text-slate-700 sm:text-base sm:leading-loose ${
            isRegenerating ? 'opacity-40' : ''
          }`}
          aria-live="polite"
        >
          {summary}
        </p>
      </div>
    </div>
  )
}
