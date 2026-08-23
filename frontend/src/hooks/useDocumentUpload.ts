import { useCallback, useState } from 'react'
import { validateSelectedFile } from '../utils/validation'

export function useDocumentUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  const selectFile = useCallback((file: File) => {
    const result = validateSelectedFile(file)
    if (!result.valid) {
      setError(result.errorMessage ?? 'This file cannot be uploaded.')
      setSelectedFile(null)
      return
    }
    setError(null)
    setSelectedFile(file)
  }, [])

  const removeFile = useCallback(() => {
    setSelectedFile(null)
    setError(null)
  }, [])

  const onDragEnter = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    setIsDragging(true)
  }, [])

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
  }, [])

  const onDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    setIsDragging(false)
  }, [])

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()
      setIsDragging(false)
      const file = event.dataTransfer.files?.[0]
      if (file) selectFile(file)
    },
    [selectFile],
  )

  const onInputChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0]
      if (file) selectFile(file)
      event.target.value = ''
    },
    [selectFile],
  )

  return {
    selectedFile,
    error,
    isDragging,
    selectFile,
    removeFile,
    dragHandlers: { onDragEnter, onDragOver, onDragLeave, onDrop },
    onInputChange,
  }
}
