import type { AnalyzeResult } from '../types/document'

export function buildResultMarkdown(result: AnalyzeResult): string {
  const { metadata } = result
  const lines = [
    `# Document Analysis: ${metadata.filename}`,
    '',
    `- Pages: ${metadata.page_count ?? 'N/A'}`,
    `- Word count: ${metadata.word_count}`,
    `- OCR used: ${metadata.used_ocr ? 'Yes' : 'No'}`,
    '',
    `## Summary (${result.summary_length})`,
    '',
    result.summary,
    '',
    '## Key Points',
    '',
    ...result.key_points.map((point) => `- ${point}`),
    '',
    '## Main Ideas',
    '',
    ...result.main_ideas.map((idea, i) => `${i + 1}. ${idea}`),
    '',
    '## Improvement Suggestions',
    '',
    ...(result.improvement_suggestions.length > 0
      ? result.improvement_suggestions.map((s) => `- ${s}`)
      : ['No significant issues found.']),
    '',
  ]
  return lines.join('\n')
}

export function buildResultText(result: AnalyzeResult): string {
  const { metadata } = result
  const lines = [
    `DOCUMENT ANALYSIS: ${metadata.filename}`,
    `Pages: ${metadata.page_count ?? 'N/A'} | Words: ${metadata.word_count} | OCR used: ${metadata.used_ocr ? 'Yes' : 'No'}`,
    '',
    `SUMMARY (${result.summary_length.toUpperCase()})`,
    result.summary,
    '',
    'KEY POINTS',
    ...result.key_points.map((point) => `- ${point}`),
    '',
    'MAIN IDEAS',
    ...result.main_ideas.map((idea, i) => `${i + 1}. ${idea}`),
    '',
    'IMPROVEMENT SUGGESTIONS',
    ...(result.improvement_suggestions.length > 0
      ? result.improvement_suggestions.map((s) => `- ${s}`)
      : ['No significant issues found.']),
    '',
  ]
  return lines.join('\n')
}

export function downloadTextFile(filename: string, content: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}
