import { formatDuration } from '../../utils/formatters'
import type { DocumentMetadata } from '../../types/document'
import { DocumentIcon } from '../shared/icons'

interface DocumentMetadataCardProps {
  metadata: DocumentMetadata
  aiProvider: string
}

export function DocumentMetadataCard({ metadata, aiProvider }: DocumentMetadataCardProps) {
  const parts = [
    metadata.file_type.toUpperCase(),
    metadata.page_count !== null ? `${metadata.page_count} page${metadata.page_count === 1 ? '' : 's'}` : null,
    `${metadata.word_count.toLocaleString()} words`,
    metadata.used_ocr ? 'OCR enabled' : null,
  ].filter(Boolean)

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3.5 min-w-0">
          <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-slate-50 text-slate-800">
            <DocumentIcon className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <h2 className="truncate text-base font-semibold text-slate-900 sm:text-lg">
              {metadata.filename}
            </h2>
            <div className="mt-1 flex flex-wrap items-center gap-1.5 text-xs text-slate-500">
              {parts.map((p, i) => (
                <span key={i} className="inline-flex items-center gap-1.5">
                  {i > 0 && <span className="text-slate-300">•</span>}
                  <span>{p}</span>
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-mono font-medium text-slate-600">
            ⏱ {formatDuration(metadata.processing_duration_ms)}
          </span>
          <span
            className="rounded-lg border border-teal-200 bg-teal-50 px-2.5 py-1 text-xs font-medium text-teal-800"
            title={
              aiProvider === 'fallback'
                ? 'Extractive summarization engine'
                : `Powered by ${aiProvider}`
            }
          >
            {aiProvider === 'fallback' ? 'Local Extractive Model' : `Engine: ${aiProvider}`}
          </span>
        </div>
      </div>
    </div>
  )
}
