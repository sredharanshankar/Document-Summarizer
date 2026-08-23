import { useCallback, useState } from 'react'
import { regenerateSummary } from '../services/documentService'
import { ApiError, NetworkError } from '../types/api'
import type { SummaryLength } from '../types/document'

export function useSummaryRegeneration(
  jobId: string,
  initialSummary: string,
  initialLength: SummaryLength,
) {
  const [summary, setSummary] = useState(initialSummary)
  const [summaryLength, setSummaryLength] = useState(initialLength)
  const [isRegenerating, setIsRegenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const changeLength = useCallback(
    async (length: SummaryLength) => {
      if (length === summaryLength || isRegenerating) return
      setIsRegenerating(true)
      setError(null)
      try {
        const response = await regenerateSummary(jobId, length)
        setSummary(response.summary)
        setSummaryLength(response.summary_length)
      } catch (err) {
        if (err instanceof ApiError || err instanceof NetworkError) {
          setError(err.message)
        } else {
          setError('Could not regenerate the summary. Please try again.')
        }
      } finally {
        setIsRegenerating(false)
      }
    },
    [jobId, summaryLength, isRegenerating],
  )

  return { summary, summaryLength, isRegenerating, error, changeLength }
}
