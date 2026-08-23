export type SummaryLength = 'short' | 'medium' | 'long'

export type JobStage =
  | 'queued'
  | 'validating'
  | 'extracting'
  | 'ocr'
  | 'cleaning'
  | 'summarizing'
  | 'done'

export type JobStatus = 'processing' | 'completed' | 'failed'

export interface DocumentMetadata {
  filename: string
  file_type: string
  page_count: number | null
  word_count: number
  used_ocr: boolean
  processing_duration_ms: number
}

export interface AnalyzeResult {
  metadata: DocumentMetadata
  summary: string
  summary_length: SummaryLength
  key_points: string[]
  main_ideas: string[]
  improvement_suggestions: string[]
  ai_provider: string
}

export interface ErrorPayload {
  error: string
  message: string
}

export interface AnalyzeAcceptedResponse {
  job_id: string
  status: JobStatus
}

export interface JobStatusResponse {
  job_id: string
  status: JobStatus
  stage: JobStage
  filename: string
  created_at: string
  result: AnalyzeResult | null
  error: ErrorPayload | null
}

export interface SummarizeResponse {
  summary: string
  summary_length: SummaryLength
}

export interface AskQuestionResponse {
  answer: string
  ai_provider: string
}

export interface CompareResponse {
  documents: string[]
  comparison_summary: string
  similarities: string[]
  differences: string[]
  ai_provider: string
}

export interface SessionDocument {
  jobId: string
  filename: string
}
