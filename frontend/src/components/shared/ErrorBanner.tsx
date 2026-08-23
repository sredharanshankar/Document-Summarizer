interface ErrorBannerProps {
  message: string
  onRetry: () => void
}

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div role="alert" className="rounded-2xl border border-red-200 bg-red-50/70 p-6 sm:p-8 text-center shadow-sm">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-red-200 bg-white text-red-600 font-bold text-lg">
        !
      </div>
      <h2 className="mt-4 text-base font-semibold text-red-900">We couldn't process this document</h2>
      <p className="mt-1.5 text-sm text-red-700 max-w-md mx-auto">{message}</p>
      <div className="mt-6">
        <button
          type="button"
          onClick={onRetry}
          className="inline-flex items-center gap-2 rounded-xl bg-red-700 px-5 py-2.5 text-xs font-semibold text-white shadow-sm transition-all hover:bg-red-800 active:scale-[0.99] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-700"
        >
          Try another document
        </button>
      </div>
    </div>
  )
}
