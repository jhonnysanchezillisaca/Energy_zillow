import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import type { FuelBreakdown } from '../types'

interface Props {
  fuels: FuelBreakdown | null
}

const COLORS = ['#3b82f6', '#f59e0b', '#ef4444', '#10b981']

export default function EmissionsBreakdownChart({ fuels }: Props) {
  if (!fuels) return null

  const data = [
    { name: 'Electricity', value: fuels.electricity ?? 0 },
    { name: 'Natural Gas', value: fuels.natural_gas ?? 0 },
    { name: 'Fuel Oil', value: fuels.fuel_oil ?? 0 },
    { name: 'Others', value: fuels.others ?? 0 },
  ].filter(d => d.value > 0)

  if (data.length === 0) return null

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <h3 className="text-lg font-semibold mb-4">Emissions Breakdown</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius="60%"
              outerRadius="80%"
              paddingAngle={3}
              dataKey="value"
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            >
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value: number) => [`${value.toFixed(1)} tCO₂e`, '']} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
