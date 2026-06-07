import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import type { PenaltyForecast, BuildingInfo } from '../types'

interface Props {
  penalties: PenaltyForecast | null
  info: BuildingInfo
}

function formatMoney(value: number): string {
  return `$${Math.round(value).toLocaleString()}`
}

export default function PenaltyForecastChart({ penalties, info }: Props) {
  if (!penalties) return null

  const data = [
    { year: '2024', penalty: info.penalty ?? 0 },
    { year: '2030', penalty: penalties.penalty_2030 ?? 0 },
    { year: '2035', penalty: penalties.penalty_2035 ?? 0 },
    { year: '2040', penalty: penalties.penalty_2040 ?? 0 },
  ]

  const maxPenalty = Math.max(...data.map(d => d.penalty))
  if (maxPenalty === 0) return null

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <h3 className="text-lg font-semibold mb-4">Penalty Forecast</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
            <Tooltip formatter={(value: number) => [formatMoney(value), 'Penalty']} />
            <Line
              type="monotone"
              dataKey="penalty"
              stroke="#2563eb"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
