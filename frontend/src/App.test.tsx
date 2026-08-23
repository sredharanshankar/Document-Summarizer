import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'

function jsonResponse(body: unknown, status = 200): Response {
  // A minimal fetch Response stand-in - avoids depending on whether the
  // real Response/fetch globals are polyfilled in the jsdom test env,
  // and only implements what api.ts's apiFetch actually reads.
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response
}

function pdfFile(name = 'report.pdf'): File {
  return new File([new Uint8Array([1, 2, 3, 4])], name, { type: 'application/pdf' })
}

function completedJobResponse(jobId: string, filename: string, summary: string): Response {
  return jsonResponse({
    job_id: jobId,
    status: 'completed',
    stage: 'done',
    filename,
    created_at: new Date().toISOString(),
    error: null,
    result: {
      metadata: {
        filename,
        file_type: 'pdf',
        page_count: 1,
        word_count: 100,
        used_ocr: false,
        processing_duration_ms: 50,
      },
      summary,
      summary_length: 'medium',
      key_points: [],
      main_ideas: [],
      improvement_suggestions: [],
      ai_provider: 'fallback',
    },
  })
}

function selectFile(file: File) {
  // Deliberately not userEvent.upload(): it filters against the input's
  // `accept` attribute, which would silently swallow the very
  // wrong-file-type cases these tests need to exercise. jsdom also has no
  // DataTransfer implementation, so `.files` is defined directly - the
  // standard workaround for testing file inputs under jsdom.
  const input = document.querySelector('input[type=file]') as HTMLInputElement
  Object.defineProperty(input, 'files', { value: [file], configurable: true })
  fireEvent.change(input)
}

describe('App', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('shows the drop zone on first load', () => {
    render(<App />)
    expect(screen.getByText(/drag & drop your document here/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /choose file/i })).toBeInTheDocument()
  })

  it('rejects an invalid file type without calling the network', async () => {
    render(<App />)
    const badFile = new File(['hello'], 'notes.exe', { type: 'application/octet-stream' })

    await selectFile(badFile)

    expect(await screen.findByRole('alert')).toHaveTextContent(/PDF, DOCX, TXT, JPG, JPEG, or PNG/i)
    expect(fetch).not.toHaveBeenCalled()
  })

  it('shows the file preview after selecting a valid file', async () => {
    render(<App />)

    await selectFile(pdfFile())

    expect(await screen.findByText('report.pdf')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze document/i })).toBeInTheDocument()
  })

  it('shows a real processing state while the job is running, then renders results', async () => {
    const fetchMock = vi.mocked(fetch)
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ job_id: 'job-1', status: 'processing' }, 202))
      .mockResolvedValueOnce(
        jsonResponse({
          job_id: 'job-1',
          status: 'processing',
          stage: 'summarizing',
          filename: 'report.pdf',
          created_at: new Date().toISOString(),
          result: null,
          error: null,
        }),
      )
      .mockResolvedValue(
        jsonResponse({
          job_id: 'job-1',
          status: 'completed',
          stage: 'done',
          filename: 'report.pdf',
          created_at: new Date().toISOString(),
          error: null,
          result: {
            metadata: {
              filename: 'report.pdf',
              file_type: 'pdf',
              page_count: 2,
              word_count: 500,
              used_ocr: false,
              processing_duration_ms: 120,
            },
            summary: 'This is the generated summary.',
            summary_length: 'medium',
            key_points: ['First key point', 'Second key point'],
            main_ideas: ['The main idea'],
            improvement_suggestions: [],
            ai_provider: 'fallback',
          },
        }),
      )

    render(<App />)
    await selectFile(pdfFile())
    await userEvent.click(screen.getByRole('button', { name: /analyze document/i }))

    // Real progress reflected from the backend's reported stage, not a fake timer.
    expect(await screen.findByText(/analyzing your document/i)).toBeInTheDocument()

    await waitFor(
      () => expect(screen.getByText('This is the generated summary.')).toBeInTheDocument(),
      { timeout: 5000 },
    )

    expect(screen.getByText('First key point')).toBeInTheDocument()
    expect(screen.getByText('The main idea')).toBeInTheDocument()
    expect(screen.getByText(/no significant issues/i)).toBeInTheDocument()
  })

  it('lets the user ask a question about the completed document', async () => {
    const fetchMock = vi.mocked(fetch)
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ job_id: 'job-2', status: 'processing' }, 202))
      .mockResolvedValueOnce(
        jsonResponse({
          job_id: 'job-2',
          status: 'completed',
          stage: 'done',
          filename: 'report.pdf',
          created_at: new Date().toISOString(),
          error: null,
          result: {
            metadata: {
              filename: 'report.pdf',
              file_type: 'pdf',
              page_count: 2,
              word_count: 500,
              used_ocr: false,
              processing_duration_ms: 120,
            },
            summary: 'This is the generated summary.',
            summary_length: 'medium',
            key_points: ['First key point'],
            main_ideas: ['The main idea'],
            improvement_suggestions: [],
            ai_provider: 'fallback',
          },
        }),
      )
      .mockResolvedValueOnce(
        jsonResponse({ answer: 'The document says X.', ai_provider: 'fallback' }),
      )

    render(<App />)
    await selectFile(pdfFile())
    await userEvent.click(screen.getByRole('button', { name: /analyze document/i }))

    await waitFor(() =>
      expect(screen.getByText('This is the generated summary.')).toBeInTheDocument(),
    )

    const questionInput = screen.getByLabelText(/your question about this document/i)
    await userEvent.type(questionInput, 'What does it say?')
    await userEvent.click(screen.getByRole('button', { name: /^ask$/i }))

    expect(await screen.findByText('The document says X.')).toBeInTheDocument()
    expect(screen.getByText('Q: What does it say?')).toBeInTheDocument()
    // Submitting clears the input for the next question.
    expect(questionInput).toHaveValue('')

    const lastCall = fetchMock.mock.calls.at(-1)
    expect(lastCall?.[0]).toBe('/api/documents/ask')
    expect(JSON.parse((lastCall?.[1] as RequestInit).body as string)).toEqual({
      job_id: 'job-2',
      question: 'What does it say?',
    })
  })

  it('lets the user compare two documents analyzed this session', async () => {
    const fetchMock = vi.mocked(fetch)
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ job_id: 'job-a', status: 'processing' }, 202))
      .mockResolvedValueOnce(completedJobResponse('job-a', 'report-a.pdf', 'Summary A.'))
      .mockResolvedValueOnce(jsonResponse({ job_id: 'job-b', status: 'processing' }, 202))
      .mockResolvedValueOnce(completedJobResponse('job-b', 'report-b.pdf', 'Summary B.'))
      .mockResolvedValueOnce(
        jsonResponse({
          documents: ['report-a.pdf', 'report-b.pdf'],
          comparison_summary: 'They differ on scope.',
          similarities: ['Both mention budgets.'],
          differences: ['"report-a.pdf" covers Q1.', '"report-b.pdf" covers Q2.'],
          ai_provider: 'fallback',
        }),
      )

    render(<App />)

    // Analyze the first document.
    await selectFile(pdfFile('report-a.pdf'))
    await userEvent.click(screen.getByRole('button', { name: /analyze document/i }))
    await waitFor(() => expect(screen.getByText('Summary A.')).toBeInTheDocument())

    // Reset and analyze a second document.
    await userEvent.click(screen.getByRole('button', { name: /analyze another document/i }))
    await selectFile(pdfFile('report-b.pdf'))
    await userEvent.click(screen.getByRole('button', { name: /analyze document/i }))
    await waitFor(() => expect(screen.getByText('Summary B.')).toBeInTheDocument())

    // The compare entry point only appears once 2+ documents are available.
    await userEvent.click(screen.getByRole('button', { name: /compare documents \(2\)/i }))

    await userEvent.click(screen.getByRole('checkbox', { name: /report-a\.pdf/i }))
    await userEvent.click(screen.getByRole('checkbox', { name: /report-b\.pdf/i }))
    await userEvent.click(screen.getByRole('button', { name: /^compare \(2\)$/i }))

    expect(await screen.findByText('They differ on scope.')).toBeInTheDocument()
    expect(screen.getByText('Both mention budgets.')).toBeInTheDocument()
    expect(screen.getByText('"report-a.pdf" covers Q1.')).toBeInTheDocument()

    // Test multi-document Q&A on the compare screen
    fetchMock.mockResolvedValueOnce(
      jsonResponse({ answer: 'Document A has higher Q1 spend.', ai_provider: 'fallback' }),
    )

    const compareQuestionInput = screen.getByLabelText(/your question about these compared documents/i)
    await userEvent.type(compareQuestionInput, 'Which has higher spend?')
    await userEvent.click(screen.getByRole('button', { name: /^ask$/i }))

    expect(await screen.findByText('Document A has higher Q1 spend.')).toBeInTheDocument()
    expect(screen.getByText('Q: Which has higher spend?')).toBeInTheDocument()
    expect(compareQuestionInput).toHaveValue('')

    const compareAskCall = fetchMock.mock.calls.at(-1)
    expect(compareAskCall?.[0]).toBe('/api/documents/compare/ask')
    expect(JSON.parse((compareAskCall?.[1] as RequestInit).body as string)).toEqual({
      job_ids: ['job-a', 'job-b'],
      question: 'Which has higher spend?',
    })
  })

  it('shows a clean error banner when the backend rejects the upload', async () => {
    const fetchMock = vi.mocked(fetch)
    fetchMock.mockResolvedValueOnce(
      jsonResponse({ error: 'corrupted_file', message: 'This file could not be read.' }, 400),
    )

    render(<App />)
    await selectFile(pdfFile())
    await userEvent.click(screen.getByRole('button', { name: /analyze document/i }))

    expect(await screen.findByText('This file could not be read.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /try another document/i })).toBeInTheDocument()
  })
})
