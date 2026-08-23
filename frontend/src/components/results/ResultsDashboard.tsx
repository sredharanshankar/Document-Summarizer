import { DocumentMetadataCard } from './DocumentMetadataCard'
import { SummaryPanel } from './SummaryPanel'
import { KeyPointsPanel } from './KeyPointsPanel'
import { MainIdeasPanel } from './MainIdeasPanel'
import { SuggestionsPanel } from './SuggestionsPanel'
import { AskQuestionPanel } from './AskQuestionPanel'
import { useSummaryRegeneration } from '../../hooks/useSummaryRegeneration'
import { buildResultMarkdown, buildResultText, downloadTextFile } from '../../utils/exportResult'
import type { AnalyzeResult } from '../../types/document'

interface ResultsDashboardProps {
  jobId: string
  result: AnalyzeResult
  onReset: () => void
}

export function ResultsDashboard({ jobId, result, onReset }: ResultsDashboardProps) {
  const regeneration = useSummaryRegeneration(jobId, result.summary, result.summary_length)

  const currentResult: AnalyzeResult = {
    ...result,
    summary: regeneration.summary,
    summary_length: regeneration.summaryLength,
  }

  const baseName = result.metadata.filename.replace(/\.[^.]+$/, '') || 'document-analysis'

  return (
    <div className="space-y-6">
      <DocumentMetadataCard metadata={result.metadata} aiProvider={result.ai_provider} />

      <SummaryPanel
        summary={regeneration.summary}
        summaryLength={regeneration.summaryLength}
        isRegenerating={regeneration.isRegenerating}
        error={regeneration.error}
        onLengthChange={regeneration.changeLength}
      />

      <KeyPointsPanel keyPoints={result.key_points} />
      <MainIdeasPanel mainIdeas={result.main_ideas} />
      <SuggestionsPanel suggestions={result.improvement_suggestions} />

      {/* Action Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => downloadTextFile(`${baseName}.md`, buildResultMarkdown(currentResult), 'text/markdown')}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-semibold text-slate-700 transition-colors hover:border-slate-300 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
          >
            <span>↓</span>
            <span>Download .md</span>
          </button>
          <button
            type="button"
            onClick={() => downloadTextFile(`${baseName}.txt`, buildResultText(currentResult), 'text/plain')}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-semibold text-slate-700 transition-colors hover:border-slate-300 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
          >
            <span>↓</span>
            <span>Download .txt</span>
          </button>
        </div>

        <button
          type="button"
          onClick={onReset}
          className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-slate-800 active:scale-[0.99] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
        >
          <span>+</span>
          <span>Analyze another document</span>
        </button>
      </div>

      <AskQuestionPanel jobId={jobId} />
    </div>
  )
}
