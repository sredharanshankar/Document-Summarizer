import { useCallback, useState } from 'react'
import { askCompareQuestion } from '../services/documentService'
import { ApiError, NetworkError } from '../types/api'

export interface AskedQuestion {
  id: string
  question: string
  answer: string
  aiProvider: string
}

function makeId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

export function useCompareQuestion(jobIds: string[]) {
  const [history, setHistory] = useState<AskedQuestion[]>([])
  const [isAsking, setIsAsking] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const ask = useCallback(
    async (question: string) => {
      const trimmed = question.trim()
      if (!trimmed || isAsking || jobIds.length === 0) return

      setIsAsking(true)
      setError(null)
      try {
        const response = await askCompareQuestion(jobIds, trimmed)
        setHistory((prev) => [
          ...prev,
          {
            id: makeId(),
            question: trimmed,
            answer: response.answer,
            aiProvider: response.ai_provider,
          },
        ])
      } catch (err) {
        if (err instanceof ApiError || err instanceof NetworkError) {
          setError(err.message)
        } else {
          setError('Could not get an answer. Please try again.')
        }
      } finally {
        setIsAsking(false)
      }
    },
    [jobIds, isAsking],
  )

  return { history, isAsking, error, ask }
}
