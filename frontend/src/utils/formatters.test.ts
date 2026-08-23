import { describe, expect, it } from 'vitest'
import { formatDuration, formatFileSize } from './formatters'

describe('formatFileSize', () => {
  it('formats bytes', () => {
    expect(formatFileSize(500)).toBe('500 B')
  })

  it('formats kilobytes', () => {
    expect(formatFileSize(2048)).toBe('2.0 KB')
  })

  it('formats megabytes', () => {
    expect(formatFileSize(5 * 1024 * 1024)).toBe('5.0 MB')
  })
})

describe('formatDuration', () => {
  it('formats sub-second durations in milliseconds', () => {
    expect(formatDuration(250)).toBe('250 ms')
  })

  it('formats durations of a second or more in seconds', () => {
    expect(formatDuration(1500)).toBe('1.5s')
  })
})
