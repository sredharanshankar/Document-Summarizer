import { describe, expect, it } from 'vitest'
import { MAX_FILE_SIZE_BYTES, validateSelectedFile } from './validation'

function makeFile(name: string, type: string, size: number): File {
  const file = new File([new Uint8Array(size)], name, { type })
  return file
}

describe('validateSelectedFile', () => {
  it('accepts a valid PDF', () => {
    const file = makeFile('report.pdf', 'application/pdf', 1024)
    expect(validateSelectedFile(file)).toEqual({ valid: true })
  })

  it('accepts a valid PNG', () => {
    const file = makeFile('scan.png', 'image/png', 1024)
    expect(validateSelectedFile(file)).toEqual({ valid: true })
  })

  it('accepts a valid DOCX', () => {
    const file = makeFile(
      'report.docx',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      1024,
    )
    expect(validateSelectedFile(file)).toEqual({ valid: true })
  })

  it('accepts a valid TXT', () => {
    const file = makeFile('notes.txt', 'text/plain', 1024)
    expect(validateSelectedFile(file)).toEqual({ valid: true })
  })

  it('rejects an unsupported extension', () => {
    const file = makeFile('notes.exe', 'application/octet-stream', 1024)
    const result = validateSelectedFile(file)
    expect(result.valid).toBe(false)
    expect(result.errorMessage).toMatch(/PDF, DOCX, TXT, JPG, JPEG, or PNG/)
  })

  it('rejects a MIME type that does not match an allowed extension', () => {
    const file = makeFile('fake.pdf', 'text/plain', 1024)
    const result = validateSelectedFile(file)
    expect(result.valid).toBe(false)
  })

  it('rejects an empty file', () => {
    const file = makeFile('empty.pdf', 'application/pdf', 0)
    const result = validateSelectedFile(file)
    expect(result.valid).toBe(false)
    expect(result.errorMessage).toMatch(/empty/i)
  })

  it('rejects a file over the size limit', () => {
    const file = makeFile('huge.pdf', 'application/pdf', MAX_FILE_SIZE_BYTES + 1)
    const result = validateSelectedFile(file)
    expect(result.valid).toBe(false)
    expect(result.errorMessage).toMatch(/limit/i)
  })

  it('accepts a file exactly at the size limit', () => {
    const file = makeFile('max.pdf', 'application/pdf', MAX_FILE_SIZE_BYTES)
    expect(validateSelectedFile(file).valid).toBe(true)
  })
})
