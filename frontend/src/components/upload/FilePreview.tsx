import { formatFileSize } from '../../utils/formatters'
import type { SummaryLength } from '../../types/document'
import { DocumentIcon } from '../shared/icons'

interface FilePreviewProps {
  file: File
  summaryLength: SummaryLength
  onSummaryLengthChange: (length: SummaryLength) => void
  onRemove: () => void
  onAnalyze: () => void
}

const SUMMARY_LENGTH_OPTIONS: { value: SummaryLength; label: string; desc: string }[] = [
  { value: 'short', label: 'Short', desc: 'Core key takeaways' },
  { value: 'medium', label: 'Medium', desc: 'Balanced executive overview' },
  { value: 'long', label: 'Long', desc: 'Comprehensive deep synthesis' },
]

export function FilePreview({
  file,
  summaryLength,
  onSummaryLengthChange,
  onRemove,
  onAnalyze,
}: FilePreviewProps) {
  const extension = file.name.split('.').pop()?.toUpperCase() || 'FILE'

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
      {/* File Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3.5 min-w-0">
          <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-slate-50 text-slate-800">
            <DocumentIcon className="h-6 w-6" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="truncate text-base font-semibold text-slate-900">{file.name}</span>
              <span className="rounded border border-slate-200 bg-slate-100 px-2 py-0.5 text-[10px] font-mono font-medium text-slate-600">
                {extension}
              </span>
            </div>
            <p className="mt-0.5 text-xs text-slate-500">{formatFileSize(file.size)}</p>
          </div>
        </div>

        <button
          type="button"
          onClick={onRemove}
          className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
        >
          Remove
        </button>
      </div>

      {/* Summary Length Selection */}
      <fieldset className="mt-6 border-t border-slate-100 pt-6">
        <legend className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Select Summary Depth
        </legend>
        <div className="mt-3 grid grid-cols-1 gap-2.5 sm:grid-cols-3">
          {SUMMARY_LENGTH_OPTIONS.map((option) => {
            const isSelected = summaryLength === option.value
            return (
              <label
                key={option.value}
                className={`relative flex cursor-pointer flex-col rounded-xl border p-3.5 transition-all ${
                  isSelected
                    ? 'border-slate-900 bg-slate-900 text-white'
                    : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <input
                  type="radio"
                  name="summary-length"
                  value={option.value}
                  checked={isSelected}
                  onChange={() => onSummaryLengthChange(option.value)}
                  className="sr-only"
                />
                <span className="text-xs font-semibold">{option.label}</span>
                <span
                  className={`mt-1 text-[11px] leading-tight ${
                    isSelected ? 'text-slate-300' : 'text-slate-500'
                  }`}
                >
                  {option.desc}
                </span>
              </label>
            )
          })}
        </div>
      </fieldset>

      {/* Action Buttons */}
      <div className="mt-8 flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-end">
        <button
          type="button"
          onClick={onAnalyze}
          className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-sm transition-all hover:bg-slate-800 active:scale-[0.99] sm:w-auto focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
        >
          <span>Analyze Document</span>
          <svg className="h-4 w-4" viewBox="0 0 16 16" fill="none">
            <path
              d="M3.5 8h9m-4-4l4 4-4 4"
              stroke="currentColor"
              strokeWidth="1.75"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  )
}
