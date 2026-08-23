import { useState } from 'react'

interface CopyButtonProps {
  text: string
  label?: string
}

export function CopyButton({ text, label = 'Copy' }: CopyButtonProps) {
  const [copied, setCopied] = useState(false)

  const handleClick = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      // Clipboard API can be unavailable (e.g. insecure context) - fail silently
    }
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 transition-colors hover:border-slate-300 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
      aria-label={copied ? `${label} - copied to clipboard` : label}
    >
      {copied ? (
        <>
          <span className="text-emerald-600">✓</span>
          <span className="text-emerald-700">Copied!</span>
        </>
      ) : (
        <>
          <span className="text-slate-400">📋</span>
          <span>{label}</span>
        </>
      )}
    </button>
  )
}
