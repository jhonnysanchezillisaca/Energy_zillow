import type { BuildingInfo } from '../types'

interface Props {
  info: BuildingInfo
}

function formatMoney(value: number | null): string {
  if (value === null || value === undefined) return 'N/A'
  return `$${Math.round(value).toLocaleString()}`
}

function formatPercent(value: number | null): string {
  if (value === null || value === undefined) return 'N/A'
  return `${(value * 100).toFixed(2)}%`
}

export default function MetricsCards({ info }: Props) {
  const relative = info.relative_to_limit ?? 0
  const isOverLimit = relative > 0

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <p className="text-sm text-gray-500 mb-1">Emissions Over Limit</p>
        <p className={`text-2xl font-bold ${isOverLimit ? 'text-red-600' : 'text-green-600'}`}>
          {formatPercent(relative)}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          {isOverLimit ? 'Exceeded' : 'Below limit'}
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <p className="text-sm text-gray-500 mb-1">Annual Penalty</p>
        <p className="text-2xl font-bold text-gray-900">
          {formatMoney(info.penalty)}
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <p className="text-sm text-gray-500 mb-1">ENERGY STAR Score</p>
        <p className="text-2xl font-bold text-gray-900">
          {info.energy_star_score ?? 'N/A'}
        </p>
      </div>
    </div>
  )
}
