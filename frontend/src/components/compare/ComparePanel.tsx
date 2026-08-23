import { useState } from 'react'
import { DocumentPicker } from './DocumentPicker'
import { ComparisonResults } from './ComparisonResults'
import { useDocumentComparison } from '../../hooks/useDocumentComparison'
import type { SessionDocument } from '../../types/document'

interface ComparePanelProps {
  documents: SessionDocument[]
  onClose: () => void
}

export function ComparePanel({ documents, onClose }: ComparePanelProps) {
  const [selectedJobIds, setSelectedJobIds] = useState<string[]>([])
  const comparison = useDocumentComparison()

  const toggle = (jobId: string) => {
    setSelectedJobIds((prev) =>
      prev.includes(jobId) ? prev.filter((id) => id !== jobId) : [...prev, jobId],
    )
  }

  const handleReset = () => {
    comparison.reset()
    setSelectedJobIds([])
  }

  if (comparison.state.status === 'completed') {
    return (
      <ComparisonResults
        result={comparison.state.result}
        jobIds={selectedJobIds}
        onReset={handleReset}
      />
    )
  }

  return (
    <div className="space-y-4">
      <DocumentPicker
        documents={documents}
        selectedJobIds={selectedJobIds}
        onToggle={toggle}
        onCompare={() => void comparison.compare(selectedJobIds)}
        isComparing={comparison.state.status === 'comparing'}
        error={comparison.state.status === 'failed' ? comparison.state.message : null}
      />
      <div className="text-center sm:text-left">
        <button
          type="button"
          onClick={onClose}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-slate-900 transition-colors"
        >
          <span>←</span>
          <span>Back to document analysis</span>
        </button>
      </div>
    </div>
  )
}
