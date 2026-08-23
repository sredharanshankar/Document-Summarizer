import type { SessionDocument } from '../../types/document'
import { DocumentIcon } from '../shared/icons'

export const MIN_COMPARE_DOCUMENTS = 2
export const MAX_COMPARE_DOCUMENTS = 5

interface DocumentPickerProps {
  documents: SessionDocument[]
  selectedJobIds: string[]
  onToggle: (jobId: string) => void
  onCompare: () => void
  isComparing: boolean
  error: string | null
}

export function DocumentPicker({
  documents,
  selectedJobIds,
  onToggle,
  onCompare,
  isComparing,
  error,
}: DocumentPickerProps) {
  const atMax = selectedJobIds.length >= MAX_COMPARE_DOCUMENTS
  const canCompare =
    selectedJobIds.length >= MIN_COMPARE_DOCUMENTS &&
    selectedJobIds.length <= MAX_COMPARE_DOCUMENTS &&
    !isComparing

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
      <div className="flex items-center gap-2 border-b border-slate-100 pb-4">
        <span className="h-2 w-2 rounded-full bg-slate-900" />
        <div>
          <h2 className="text-base font-semibold text-slate-900">Compare Documents</h2>
          <p className="mt-0.5 text-xs text-slate-500">
            Select {MIN_COMPARE_DOCUMENTS}-{MAX_COMPARE_DOCUMENTS} documents analyzed this session to compare.
          </p>
        </div>
      </div>

      <fieldset className="mt-5">
        <legend className="sr-only">Documents to compare</legend>
        <ul className="space-y-2.5">
          {documents.map((doc) => {
            const checked = selectedJobIds.includes(doc.jobId)
            return (
              <li key={doc.jobId}>
                <label
                  className={`flex cursor-pointer items-center justify-between gap-3 rounded-xl border p-3.5 transition-all ${
                    checked
                      ? 'border-slate-900 bg-slate-50'
                      : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/50'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => onToggle(doc.jobId)}
                      disabled={!checked && atMax}
                      className="h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900"
                    />
                    <div className="flex items-center gap-2 min-w-0">
                      <DocumentIcon className="h-4 w-4 text-slate-500 flex-shrink-0" />
                      <span className="truncate text-sm font-medium text-slate-900">{doc.filename}</span>
                    </div>
                  </div>
                  {checked && (
                    <span className="rounded bg-slate-900 px-2 py-0.5 text-[10px] font-semibold text-white">
                      Selected
                    </span>
                  )}
                </label>
              </li>
            )
          })}
        </ul>
      </fieldset>

      {error && (
        <div role="alert" className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700">
          {error}
        </div>
      )}

      <div className="mt-6 flex items-center justify-between">
        <span className="text-xs text-slate-500">
          {selectedJobIds.length} of {documents.length} selected
        </span>
        <button
          type="button"
          onClick={onCompare}
          disabled={!canCompare}
          className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.99] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
        >
          {isComparing
            ? 'Comparing...'
            : `Compare${selectedJobIds.length > 0 ? ` (${selectedJobIds.length})` : ''}`}
        </button>
      </div>
    </div>
  )
}
