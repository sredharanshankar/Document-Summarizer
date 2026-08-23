import type { JobStage } from '../../types/document'

const STAGES: { key: JobStage; label: string; desc: string }[] = [
  { key: 'queued', label: 'Upload Received', desc: 'Queued for processing' },
  { key: 'validating', label: 'Validating Document', desc: 'Checking file integrity and formatting' },
  { key: 'extracting', label: 'Extracting Content', desc: 'Parsing text and document structure' },
  { key: 'ocr', label: 'Optical Recognition (OCR)', desc: 'Reading rasterized pages and scans' },
  { key: 'cleaning', label: 'Normalizing Text', desc: 'Removing artifacts and standardizing syntax' },
  { key: 'summarizing', label: 'Synthesizing Intelligence', desc: 'Generating key takeaways and summaries' },
  { key: 'done', label: 'Analysis Complete', desc: 'Finalizing document insights' },
]

interface ProcessingStatusProps {
  stage: JobStage
}

export function ProcessingStatus({ stage }: ProcessingStatusProps) {
  const currentIndex = STAGES.findIndex((s) => s.key === stage)
  const safeIndex = currentIndex >= 0 ? currentIndex : 0
  const progressPercent = Math.min(100, Math.round(((safeIndex + 1) / STAGES.length) * 100))
  const currentStageInfo = STAGES[safeIndex] || STAGES[0]

  return (
    <div
      className="rounded-xl border border-slate-200 bg-white p-6 sm:p-8"
      role="status"
      aria-live="polite"
    >
      {/* Header & Percentage */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-2 w-2 rounded-full bg-teal-600 animate-flat-pulse" />
            <h2 className="text-base font-semibold text-slate-900">Analyzing your document</h2>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            {currentStageInfo.desc}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-mono font-medium text-slate-700">
            Stage {safeIndex + 1}/{STAGES.length}
          </span>
          <span className="text-xs font-semibold text-slate-700">{progressPercent}%</span>
        </div>
      </div>

      {/* 2D Flat Progress Bar */}
      <div className="mt-5 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full bg-slate-900 transition-all duration-500 ease-out"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Stepped Pipeline Timeline */}
      <div className="mt-6 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
        {STAGES.map((s, index) => {
          const isDone = index < safeIndex
          const isCurrent = index === safeIndex

          return (
            <div
              key={s.key}
              className={`flex items-start gap-3 rounded-lg border p-3 transition-colors ${
                isCurrent
                  ? 'border-slate-900 bg-slate-50/80'
                  : isDone
                    ? 'border-slate-200 bg-white'
                    : 'border-slate-100 bg-slate-50/40 opacity-50'
              }`}
            >
              {/* Step indicator glyph */}
              <div className="mt-0.5 flex-shrink-0">
                {isDone ? (
                  <div className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-600 text-white">
                    <svg className="h-3 w-3" viewBox="0 0 16 16" fill="none">
                      <path
                        d="M3.5 8.5L6.5 11.5L12.5 4.5"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                ) : isCurrent ? (
                  <div className="flex h-5 w-5 items-center justify-center rounded-full border-2 border-slate-900 bg-white text-slate-900">
                    <span className="h-2 w-2 rounded-full bg-slate-900 animate-flat-pulse" />
                  </div>
                ) : (
                  <div className="flex h-5 w-5 items-center justify-center rounded-full border border-slate-300 text-[10px] font-medium text-slate-400">
                    {index + 1}
                  </div>
                )}
              </div>

              {/* Step content */}
              <div className="min-w-0 flex-1">
                <p
                  className={`text-xs font-semibold ${
                    isCurrent
                      ? 'text-slate-900'
                      : isDone
                        ? 'text-slate-700'
                        : 'text-slate-400'
                  }`}
                >
                  {s.label}
                </p>
                <p className="mt-0.5 truncate text-[11px] text-slate-500">{s.desc}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Flat Skeleton Preview Box */}
      <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50/60 p-4">
        <div className="flex items-center justify-between pb-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            Synthesizing Workspace Preview
          </span>
          <span className="text-[11px] font-mono text-slate-400">Live synthesis...</span>
        </div>
        <div className="space-y-2 pt-2">
          <div className="h-3 w-3/4 rounded bg-slate-200 animate-flat-pulse" />
          <div className="h-3 w-full rounded bg-slate-200 animate-flat-pulse" />
          <div className="h-3 w-5/6 rounded bg-slate-200 animate-flat-pulse" />
        </div>
      </div>
    </div>
  )
}
