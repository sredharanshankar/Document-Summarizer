// Small, hand-rolled inline icon set - deliberately not an icon library
// dependency for a handful of glyphs. Every icon is a plain flat outline
// (no gradients, no 3D), stroke-based so it inherits `currentColor`.

type IconProps = { className?: string }

export function DocumentIcon({ className = 'h-6 w-6' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M7 3.5h7l4 4V19a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 6 19V5A1.5 1.5 0 0 1 7 3.5Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path d="M14 3.5V7a1 1 0 0 0 1 1h3.5" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
      <path d="M9 12.5h6M9 15.5h6M9 9.5h2" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  )
}

export function UploadCloudIcon({ className = 'h-8 w-8' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M7.5 17.5a4 4 0 0 1-.6-7.96 5 5 0 0 1 9.66-1.62A4.5 4.5 0 0 1 16.5 17.5h-9Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path d="M12 14.5V9m0 0-2.2 2.2M12 9l2.2 2.2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function SparkleIcon({ className = 'h-5 w-5' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M11 4.5c.3 2.4 1 3.9 2.1 5s2.6 1.8 5 2.1c-2.4.3-3.9 1-5 2.1s-1.8 2.6-2.1 5c-.3-2.4-1-3.9-2.1-5s-2.6-1.8-5-2.1c2.4-.3 3.9-1 5-2.1s1.8-2.6 2.1-5Z"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinejoin="round"
      />
      <path d="M18.5 3.5c.15 1 .43 1.68.9 2.15s1.15.75 2.15.9c-1 .15-1.68.43-2.15.9s-.75 1.15-.9 2.15c-.15-1-.43-1.68-.9-2.15s-1.15-.75-2.15-.9c1-.15 1.68-.43 2.15-.9s.75-1.15.9-2.15Z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" />
    </svg>
  )
}

export function CheckCircleIcon({ className = 'h-5 w-5' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <circle cx="12" cy="12" r="8.25" stroke="currentColor" strokeWidth="1.6" />
      <path d="M8.5 12.2 10.8 14.5 15.5 9.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function CircleDotIcon({ className = 'h-5 w-5' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <circle cx="12" cy="12" r="8.25" stroke="currentColor" strokeWidth="1.6" />
      <circle cx="12" cy="12" r="3" fill="currentColor" />
    </svg>
  )
}

export function CircleIcon({ className = 'h-5 w-5' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <circle cx="12" cy="12" r="8.25" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  )
}

export function ArrowRightIcon({ className = 'h-5 w-5' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M4.5 12h15M13.5 6l6 6-6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function ScaleIcon({ className = 'h-5 w-5' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M12 3.5v17M8 6.5h8M5 6.5l-2.5 5.5a2.8 2.8 0 0 0 5.4 0L5 6.5ZM19 6.5l-2.5 5.5a2.8 2.8 0 0 0 5.4 0L19 6.5Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function ChatIcon({ className = 'h-5 w-5' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v7a2.5 2.5 0 0 1-2.5 2.5H9l-4 3.5v-3.5H6.5A2.5 2.5 0 0 1 4 13.5v-7Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function AlertIcon({ className = 'h-5 w-5' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M12 4 21 19.5H3L12 4Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
      <path d="M12 10v4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <circle cx="12" cy="16.7" r="0.9" fill="currentColor" />
    </svg>
  )
}
