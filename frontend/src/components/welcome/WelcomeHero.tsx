import { SparkleIcon, DocumentIcon, ChatIcon, ScaleIcon, ArrowRightIcon } from '../shared/icons'

interface WelcomeHeroProps {
  onGetStarted: () => void
}

const HIGHLIGHTS = [
  {
    icon: SparkleIcon,
    title: 'Adaptive Summaries',
    description: 'Instant multi-length synthesis tailored to your focus: concise briefs, balanced overviews, or comprehensive deep-dives.',
    tag: 'Multi-length',
  },
  {
    icon: DocumentIcon,
    title: 'Key Point Extraction',
    description: 'Pinpoints pivotal decisions, quantitative data, and core arguments without losing critical context.',
    tag: 'Structured',
  },
  {
    icon: ChatIcon,
    title: 'Grounded Q&A',
    description: 'Ask natural language questions directly against your document with zero hallucination guarantee.',
    tag: 'Interactive',
  },
  {
    icon: ScaleIcon,
    title: 'Multi-Document Comparison',
    description: 'Compare agreements, versions, or research papers side-by-side to highlight agreements and discrepancies.',
    tag: 'Comparative',
  },
]

const FORMATS = [
  { label: 'PDF Documents', ext: '.PDF', icon: '📄' },
  { label: 'Word Files', ext: '.DOCX', icon: '📝' },
  { label: 'Plain Text', ext: '.TXT', icon: '📃' },
  { label: 'Scanned Images', ext: '.PNG / .JPG (OCR)', icon: '🔍' },
]

export function WelcomeHero({ onGetStarted }: WelcomeHeroProps) {
  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:py-12">
      {/* Hero Badge */}
      <div className="flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-teal-200 bg-teal-50/80 px-3.5 py-1 text-xs font-semibold tracking-wide text-teal-800">
          <span className="h-1.5 w-1.5 rounded-full bg-teal-600" />
          <span>Professional Document Intelligence</span>
        </div>

        {/* Hero Title */}
        <h1 className="mt-5 max-w-2xl font-serif text-3xl font-bold tracking-tight text-slate-900 sm:text-5xl sm:leading-tight">
          Read faster. Understand deeper. Decide with clarity.
        </h1>

        {/* Hero Subtitle */}
        <p className="mt-4 max-w-xl text-base text-slate-600 sm:text-lg sm:leading-relaxed">
          Transform lengthy reports, contracts, academic papers, and scanned archives into structured executive summaries and grounded insights.
        </p>

        {/* CTA Button */}
        <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row">
          <button
            type="button"
            onClick={onGetStarted}
            className="group inline-flex items-center justify-center gap-2.5 rounded-xl bg-slate-900 px-6 py-3.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-slate-800 active:scale-[0.99] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
          >
            <span>Start Summarizing</span>
            <ArrowRightIcon className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5" />
          </button>
          <span className="text-xs text-slate-500">No account required • Fast local analysis</span>
        </div>
      </div>

      {/* Feature Grid */}
      <div className="mt-14 grid grid-cols-1 gap-4 sm:grid-cols-2">
        {HIGHLIGHTS.map((item, index) => {
          const Icon = item.icon
          return (
            <div
              key={index}
              className="group flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 transition-colors hover:border-slate-300 hover:bg-slate-50/50"
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-800">
                    <Icon className="h-4.5 w-4.5" />
                  </div>
                  <span className="rounded border border-slate-200 bg-slate-50 px-2 py-0.5 text-[11px] font-medium text-slate-600">
                    {item.tag}
                  </span>
                </div>
                <h3 className="mt-3.5 text-sm font-semibold text-slate-900">{item.title}</h3>
                <p className="mt-1.5 text-xs leading-relaxed text-slate-600">{item.description}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Supported Formats Banner */}
      <div className="mt-10 rounded-xl border border-slate-200 bg-white p-5">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="text-center sm:text-left">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Supported Document Formats</p>
            <p className="text-xs text-slate-600 mt-0.5">Automated text extraction &amp; optical character recognition</p>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-2">
            {FORMATS.map((fmt, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700"
              >
                <span className="text-sm">{fmt.icon}</span>
                <span>{fmt.ext}</span>
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
