export function VytalLogo({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="vytal-logo-gradient" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#2dd4bf" />
          <stop offset="1" stopColor="#60a5fa" />
        </linearGradient>
      </defs>
      <rect width="32" height="32" rx="9" fill="#0c1222" stroke="rgba(148,178,222,0.25)" />
      <path d="M7 10l9 14 9-14" fill="none" stroke="url(#vytal-logo-gradient)" strokeWidth="3.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
