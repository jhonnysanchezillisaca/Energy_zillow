import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import type { FutureConsumptionScenario } from '../types'

interface Props {
  scenarios: FutureConsumptionScenario[]
}

export default function FutureConsumptionChart({ scenarios }: Props) {
  if (!scenarios || scenarios.length === 0) return null

  // Pivot to grouped bar format
  const grouped: Record<string, Record<string, number>> = {}
  for (const s of scenarios) {
    if (!grouped[s.year]) grouped[s.year] = {}
    grouped[s.year][s.scenario] = s.value * 100
  }

  const data = Object.keys(grouped).sort().map(year => ({
    year,
    Low: grouped[year]['Low'] ?? 0,
    Med: grouped[year]['Med'] ?? 0,
    High: grouped[year]['High'] ?? 0,
  }))

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <h3 className="text-lg font-semibold mb-4">
        Consumption Budget Expectations (Fuel Price Fluctuations)
      </h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis tickFormatter={(v) => `${v.toFixed(0)}%`} />
            <Tooltip formatter={(value: number) => [`${value.toFixed(1)}%`, '']} />
            <Legend />
            <Bar dataKey="Low" fill="#3b82f6" />
            <Bar dataKey="Med" fill="#f59e0b" />
            <Bar dataKey="High" fill="#ef4444" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
