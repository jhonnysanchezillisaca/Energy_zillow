import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import type { BuildingInfo } from '../types'

interface Props {
  info: BuildingInfo
}

export default function EmissionsVsLimitChart({ info }: Props) {
  if (!info.calculated_emissions || !info.emissions_limit) return null

  const data = [
    { name: 'Actual Emissions', value: info.calculated_emissions },
    { name: 'Limit', value: info.emissions_limit },
  ]

  const colors = ['#ef4444', '#10b981']

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <h3 className="text-lg font-semibold mb-4">Emissions vs Limit</h3>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 20, left: 40, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" width={120} />
            <Tooltip formatter={(value: number) => [`${value.toFixed(1)} tCO₂e`, '']} />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={colors[index]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
