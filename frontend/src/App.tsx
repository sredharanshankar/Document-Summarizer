import { useEffect, useState } from 'react'
import { WelcomeHero } from './components/welcome/WelcomeHero'
import { DropZone } from './components/upload/DropZone'
import { FilePreview } from './components/upload/FilePreview'
import { ProcessingStatus } from './components/shared/ProcessingStatus'
import { ErrorBanner } from './components/shared/ErrorBanner'
import { ResultsDashboard } from './components/results/ResultsDashboard'
import { ComparePanel } from './components/compare/ComparePanel'
import { DocumentIcon } from './components/shared/icons'
import { useDocumentUpload } from './hooks/useDocumentUpload'
import { useDocumentAnalysis } from './hooks/useDocumentAnalysis'
import type { SessionDocument, SummaryLength } from './types/document'

const MIN_DOCUMENTS_TO_COMPARE = 2

function App() {
  const upload = useDocumentUpload()
  const analysis = useDocumentAnalysis()
  const [summaryLength, setSummaryLength] = useState<SummaryLength>('medium')
  const [sessionDocuments, setSessionDocuments] = useState<SessionDocument[]>([])
  const [viewMode, setViewMode] = useState<'analyze' | 'compare'>('analyze')
  const [activeScreen, setActiveScreen] = useState<'welcome' | 'workspace'>('welcome')

  // Track every completed analysis this session (in memory only - lost on
  // reload, same as the rest of the app's state) so the user can compare
  // documents they've already analyzed without re-uploading them.
  useEffect(() => {
    if (analysis.state.status === 'completed') {
      const { jobId, result } = analysis.state
      setSessionDocuments((prev) =>
        prev.some((doc) => doc.jobId === jobId)
          ? prev
          : [...prev, { jobId, filename: result.metadata.filename }],
      )
    }
  }, [analysis.state])

  // Automatically slide to workspace if a document is selected, analyzing, or finished
  useEffect(() => {
    if (upload.selectedFile || analysis.state.status !== 'idle') {
      setActiveScreen('workspace')
    }
  }, [upload.selectedFile, analysis.state.status])

  const handleAnalyze = () => {
    if (upload.selectedFile) {
      void analysis.start(upload.selectedFile, summaryLength)
    }
  }

  const handleReset = () => {
    analysis.reset()
    upload.removeFile()
  }

  const isAtWelcome =
    activeScreen === 'welcome' &&
    viewMode === 'analyze' &&
    analysis.state.status === 'idle' &&
    !upload.selectedFile

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-teal-100 selection:text-teal-900">
      {/* 2D Modern Navigation Header */}
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur-xs">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3.5 sm:px-6">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => {
                setActiveScreen('welcome')
                setViewMode('analyze')
              }}
              className="group flex items-center gap-2.5 text-left focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 text-white shadow-xs">
                <DocumentIcon className="h-5 w-5" />
              </div>
              <div>
                <span className="block text-sm font-bold tracking-tight text-slate-900">
                  Document Summary Assistant
                </span>
                <span className="block text-[10px] font-medium text-slate-500">
                  2D Intelligence Workspace
                </span>
              </div>
            </button>
          </div>

          <div className="flex items-center gap-2">
            {/* Screen Switcher */}
            <nav className="flex items-center gap-1 rounded-xl border border-slate-200 bg-slate-50 p-1">
              <button
                type="button"
                onClick={() => {
                  setActiveScreen('welcome')
                  setViewMode('analyze')
                }}
                className={`rounded-lg px-3 py-1 text-xs font-semibold transition-all ${
                  isAtWelcome
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Welcome
              </button>
              <button
                type="button"
                onClick={() => {
                  setActiveScreen('workspace')
                  setViewMode('analyze')
                }}
                className={`rounded-lg px-3 py-1 text-xs font-semibold transition-all ${
                  !isAtWelcome && viewMode === 'analyze'
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Summarizer
              </button>
            </nav>

            {/* Compare Documents Mode */}
            {sessionDocuments.length >= MIN_DOCUMENTS_TO_COMPARE && (
              <button
                type="button"
                onClick={() => {
                  setActiveScreen('workspace')
                  setViewMode(viewMode === 'compare' ? 'analyze' : 'compare')
                }}
                className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 ${
                  viewMode === 'compare'
                    ? 'border-slate-900 bg-slate-900 text-white'
                    : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
                }`}
              >
                <span>
                  {viewMode === 'compare'
                    ? 'Back to analysis'
                    : `Compare documents (${sessionDocuments.length})`}
                </span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Area with 2D Sliding Track */}
      <div className="flex-1 slide-container">
        <div
          className="slide-track"
          style={{
            transform: isAtWelcome ? 'translateX(0%)' : 'translateX(-50%)',
          }}
        >
          {/* Panel 1: Welcome Landing Screen */}
          <section className="slide-panel" aria-label="Welcome Page">
            <WelcomeHero onGetStarted={() => setActiveScreen('workspace')} />
          </section>

          {/* Panel 2: Summarizer & Workspace Screen */}
          <section className="slide-panel" aria-label="Document Workspace">
            <main className="mx-auto max-w-3xl px-4 py-8 sm:py-10">
              {viewMode === 'compare' ? (
                <ComparePanel
                  documents={sessionDocuments}
                  onClose={() => setViewMode('analyze')}
                />
              ) : (
                <div className="space-y-6">
                  {analysis.state.status === 'idle' && !upload.selectedFile && (
                    <div>
                      <div className="mb-6 flex items-center justify-between">
                        <div>
                          <h2 className="text-xl font-bold tracking-tight text-slate-900">
                            Upload Document
                          </h2>
                          <p className="mt-0.5 text-xs text-slate-500">
                            Upload your file to generate structured insights and instant summaries.
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => setActiveScreen('welcome')}
                          className="text-xs font-medium text-slate-500 hover:text-slate-900 transition-colors"
                        >
                          ← Back to overview
                        </button>
                      </div>
                      <DropZone
                        isDragging={upload.isDragging}
                        error={upload.error}
                        dragHandlers={upload.dragHandlers}
                        onInputChange={upload.onInputChange}
                      />
                    </div>
                  )}

                  {analysis.state.status === 'idle' && upload.selectedFile && (
                    <FilePreview
                      file={upload.selectedFile}
                      summaryLength={summaryLength}
                      onSummaryLengthChange={setSummaryLength}
                      onRemove={upload.removeFile}
                      onAnalyze={handleAnalyze}
                    />
                  )}

                  {(analysis.state.status === 'uploading' ||
                    analysis.state.status === 'processing') && (
                    <ProcessingStatus
                      stage={
                        analysis.state.status === 'processing' ? analysis.state.stage : 'queued'
                      }
                    />
                  )}

                  {analysis.state.status === 'failed' && (
                    <ErrorBanner message={analysis.state.message} onRetry={handleReset} />
                  )}

                  {analysis.state.status === 'completed' && (
                    <ResultsDashboard
                      jobId={analysis.state.jobId}
                      result={analysis.state.result}
                      onReset={handleReset}
                    />
                  )}
                </div>
              )}
            </main>
          </section>
        </div>
      </div>

      {/* 2D Minimal Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
        <div className="mx-auto max-w-5xl px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Document Summary Assistant • Pure 2D Flat Interface</span>
          <div className="flex items-center gap-3 text-slate-400 text-[11px]">
            <span>Local OCR Engine</span>
            <span>•</span>
            <span>Extractive &amp; Generative AI Support</span>
            <span>•</span>
            <span>Responsive 2D</span>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
