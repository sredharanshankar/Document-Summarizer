import { useCallback, useState } from 'react'
import { compareDocuments } from '../services/documentService'
import { ApiError, NetworkError } from '../types/api'
import type { CompareResponse } from '../types/document'

export type ComparisonState =
  | { status: 'idle' }
  | { status: 'comparing' }
  | { status: 'completed'; result: CompareResponse }
  | { status: 'failed'; message: string }

export function useDocumentComparison() {
  const [state, setState] = useState<ComparisonState>({ status: 'idle' })

  const compare = useCallback(async (jobIds: string[]) => {
    setState({ status: 'comparing' })
    try {
      const result = await compareDocuments(jobIds)
      setState({ status: 'completed', result })
    } catch (err) {
      if (err instanceof ApiError || err instanceof NetworkError) {
        setState({ status: 'failed', message: err.message })
      } else {
        setState({ status: 'failed', message: 'Could not compare these documents. Please try again.' })
      }
    }
  }, [])

  const reset = useCallback(() => setState({ status: 'idle' }), [])

  return { state, compare, reset }
}
