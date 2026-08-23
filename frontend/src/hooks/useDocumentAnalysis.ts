import { useCallback, useRef, useState } from 'react'
import { analyzeDocument, getJobStatus } from '../services/documentService'
import { ApiError, NetworkError } from '../types/api'
import type { AnalyzeResult, JobStage, SummaryLength } from '../types/document'

const POLL_INTERVAL_MS = 1200

export type AnalysisState =
  | { status: 'idle' }
  | { status: 'uploading' }
  | { status: 'processing'; jobId: string; stage: JobStage }
  | { status: 'completed'; jobId: string; result: AnalyzeResult }
  | { status: 'failed'; message: string }

export function useDocumentAnalysis() {
  const [state, setState] = useState<AnalysisState>({ status: 'idle' })
  const pollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const stopPolling = useCallback(() => {
    if (pollTimeoutRef.current) {
      clearTimeout(pollTimeoutRef.current)
      pollTimeoutRef.current = null
    }
  }, [])

  const poll = useCallback((jobId: string) => {
    const tick = async () => {
      try {
        const job = await getJobStatus(jobId)
        if (job.status === 'completed' && job.result) {
          setState({ status: 'completed', jobId, result: job.result })
          return
        }
        if (job.status === 'failed') {
          setState({
            status: 'failed',
            message: job.error?.message ?? 'Processing failed. Please try again.',
          })
          return
        }
        setState({ status: 'processing', jobId, stage: job.stage })
        pollTimeoutRef.current = setTimeout(tick, POLL_INTERVAL_MS)
      } catch (err) {
        setState({ status: 'failed', message: describeError(err) })
      }
    }
    void tick()
  }, [])

  const start = useCallback(
    async (file: File, summaryLength: SummaryLength) => {
      stopPolling()
      setState({ status: 'uploading' })
      try {
        const accepted = await analyzeDocument(file, summaryLength)
        setState({ status: 'processing', jobId: accepted.job_id, stage: 'queued' })
        poll(accepted.job_id)
      } catch (err) {
        setState({ status: 'failed', message: describeError(err) })
      }
    },
    [poll, stopPolling],
  )

  const reset = useCallback(() => {
    stopPolling()
    setState({ status: 'idle' })
  }, [stopPolling])

  return { state, start, reset }
}

function describeError(err: unknown): string {
  if (err instanceof ApiError) return err.message
  if (err instanceof NetworkError) return err.message
  return 'Something went wrong. Please try again.'
}
