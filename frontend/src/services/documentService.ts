import { apiFetch } from './api'
import type {
  AnalyzeAcceptedResponse,
  AskQuestionResponse,
  CompareResponse,
  JobStatusResponse,
  SummarizeResponse,
  SummaryLength,
} from '../types/document'

export async function analyzeDocument(
  file: File,
  summaryLength: SummaryLength,
): Promise<AnalyzeAcceptedResponse> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('summary_length', summaryLength)

  return apiFetch<AnalyzeAcceptedResponse>('/api/documents/analyze', {
    method: 'POST',
    body: formData,
  })
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  return apiFetch<JobStatusResponse>(`/api/documents/status/${jobId}`)
}

export async function regenerateSummary(
  jobId: string,
  summaryLength: SummaryLength,
): Promise<SummarizeResponse> {
  return apiFetch<SummarizeResponse>('/api/documents/summarize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_id: jobId, summary_length: summaryLength }),
  })
}

export async function askQuestion(jobId: string, question: string): Promise<AskQuestionResponse> {
  return apiFetch<AskQuestionResponse>('/api/documents/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_id: jobId, question }),
  })
}

export async function compareDocuments(jobIds: string[]): Promise<CompareResponse> {
  return apiFetch<CompareResponse>('/api/documents/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_ids: jobIds }),
  })
}

export async function askCompareQuestion(
  jobIds: string[],
  question: string,
): Promise<AskQuestionResponse> {
  return apiFetch<AskQuestionResponse>('/api/documents/compare/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_ids: jobIds, question }),
  })
}

