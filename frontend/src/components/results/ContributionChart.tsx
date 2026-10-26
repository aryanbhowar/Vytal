import { Bar, BarChart, Cell, ReferenceLine, ResponsiveContainer, XAxis, YAxis } from 'recharts'
import type { ContributingFactor } from '../../types/assessment'
import { shortFactorLabel } from '../../utils/formatting'


/**
 * Diverging bar chart of the person's real log-odds contributions from the API.
 * The table beside it carries the same information as text for screen readers.
 */
export function ContributionChart({ factors, title }: { factors: ContributingFactor[]; title: string }) {
  const data = factors.map((f) => ({ name: shortFactorLabel(f.feature), value: f.log_odds_contribution }))
  const extent = Math.max(0.25, ...data.map((d) => Math.abs(d.value))) * 1.1
  return (
    <div className="contribution-chart" aria-hidden="true" title={title}>
      <ResponsiveContainer width="100%" height={Math.max(150, data.length * 40)}>
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 4 }}>
          <XAxis type="number" domain={[-extent, extent]} hide />
          <YAxis type="category" dataKey="name" width={118} tickLine={false} axisLine={false} tick={{ fill: '#b6c2d9', fontSize: 13 }} />
          <ReferenceLine x={0} stroke="rgba(148,178,222,0.35)" />
          <Bar dataKey="value" radius={4} barSize={16} isAnimationActive={false}>
            {data.map((d) => (
              <Cell key={d.name} fill={d.value > 0 ? '#fda4af' : '#5eead4'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
