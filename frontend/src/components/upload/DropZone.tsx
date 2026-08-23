import { useId, useRef } from 'react'
import { ACCEPTED_EXTENSIONS, FRIENDLY_TYPES } from '../../utils/validation'
import { UploadCloudIcon } from '../shared/icons'

interface DropZoneProps {
  isDragging: boolean
  error: string | null
  dragHandlers: {
    onDragEnter: (event: React.DragEvent) => void
    onDragOver: (event: React.DragEvent) => void
    onDragLeave: (event: React.DragEvent) => void
    onDrop: (event: React.DragEvent) => void
  }
  onInputChange: (event: React.ChangeEvent<HTMLInputElement>) => void
}

export function DropZone({ isDragging, error, dragHandlers, onInputChange }: DropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const inputId = useId()

  return (
    <div className="w-full">
      <div
        {...dragHandlers}
        className={`relative rounded-2xl border-2 border-dashed px-6 py-12 text-center transition-colors sm:px-12 sm:py-16 ${
          isDragging
            ? 'border-slate-900 bg-slate-100/80'
            : 'border-slate-300 bg-white hover:border-slate-400'
        }`}
      >
        {/* Upload Icon */}
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 text-slate-800">
          <UploadCloudIcon className="h-7 w-7" />
        </div>

        <h2 className="mt-4 text-base font-semibold text-slate-900 sm:text-lg">
          Document Summary Assistant
        </h2>
        <p className="mt-1.5 text-sm text-slate-600">
          Drag &amp; drop your document here
        </p>

        <div className="my-4 flex items-center justify-center gap-3">
          <span className="h-px w-12 bg-slate-200" />
          <span className="text-xs uppercase tracking-wider text-slate-400">or</span>
          <span className="h-px w-12 bg-slate-200" />
        </div>

        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-slate-800 active:scale-[0.99] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
        >
          Choose File
        </button>

        <label htmlFor={inputId} className="sr-only">
          Choose a document to upload
        </label>
        <input
          ref={inputRef}
          id={inputId}
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(',')}
          onChange={onInputChange}
          className="sr-only"
        />

        <div className="mt-6 border-t border-slate-100 pt-4">
          <p className="text-xs font-medium text-slate-500">{FRIENDLY_TYPES}</p>
        </div>
      </div>

      {error && (
        <div
          role="alert"
          className="mt-4 flex items-start gap-2.5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800"
        >
          <span className="mt-0.5 text-red-500 font-bold">!</span>
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}
