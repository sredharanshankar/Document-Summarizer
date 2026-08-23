import { formatFileSize } from './formatters'

// Must stay in sync with backend/app/config/settings.py defaults - the
// backend is the authoritative check; this only gives instant feedback.
export const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

// Mapped per-extension (not a flat accepted-MIME-types list): a flat list
// would let a file with one accepted extension but another accepted
// type's MIME (e.g. a ".pdf" reporting "text/plain") slip through, since
// "some accepted MIME type" isn't the same check as "the right MIME type
// for this extension".
const EXTENSION_MIME_TYPES: Record<string, string[]> = {
  '.pdf': ['application/pdf'],
  '.jpg': ['image/jpeg'],
  '.jpeg': ['image/jpeg'],
  '.png': ['image/png'],
  '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  '.txt': ['text/plain'],
}
export const ACCEPTED_EXTENSIONS = Object.keys(EXTENSION_MIME_TYPES)

export const FRIENDLY_TYPES = 'PDF, DOCX, TXT, JPG, JPEG, or PNG'

export interface FileValidationResult {
  valid: boolean
  errorMessage?: string
}

export function validateSelectedFile(file: File): FileValidationResult {
  const extension = `.${file.name.split('.').pop()?.toLowerCase() ?? ''}`

  if (!ACCEPTED_EXTENSIONS.includes(extension)) {
    return {
      valid: false,
      errorMessage: `Please upload a ${FRIENDLY_TYPES} file.`,
    }
  }

  if (file.type && !EXTENSION_MIME_TYPES[extension].includes(file.type)) {
    return {
      valid: false,
      errorMessage: `Please upload a ${FRIENDLY_TYPES} file.`,
    }
  }

  if (file.size === 0) {
    return {
      valid: false,
      errorMessage: 'This file is empty. Please choose a different document.',
    }
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    return {
      valid: false,
      errorMessage: `This file is larger than the ${formatFileSize(MAX_FILE_SIZE_BYTES)} limit.`,
    }
  }

  return { valid: true }
}
