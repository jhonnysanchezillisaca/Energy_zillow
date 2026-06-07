import type { BuildingInfo } from '../types'

interface Props {
  info: BuildingInfo
}

export default function BuildingHeader({ info }: Props) {
  const statusColor = info.status_color === 'green' ? 'bg-green-100 text-green-800' :
                      info.status_color === 'red' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'

  return (
    <div className="mb-6">
      <div className="flex flex-wrap items-center gap-3 mb-2">
        <h1 className="text-2xl font-bold">{info.property_name || 'Unnamed Building'}</h1>
        <span className={`px-2 py-1 text-xs font-semibold rounded ${statusColor}`}>
          {info.status_text}
        </span>
      </div>
      <p className="text-gray-600">{info.address || info.address_1 || 'Address not available'}</p>
      <div className="flex flex-wrap gap-4 mt-3 text-sm text-gray-500">
        <span>BBL: {info.bbl}</span>
        <span>Year: {info.calendar_year}</span>
        {info.ranking !== null && <span>Ranking: #{info.ranking}</span>}
        {info.energy_star_score !== null && (
          <span>ENERGY STAR Score: {info.energy_star_score}</span>
        )}
      </div>
    </div>
  )
}
