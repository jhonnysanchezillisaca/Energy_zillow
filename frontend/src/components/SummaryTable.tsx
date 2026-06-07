import type { BuildingInfo } from '../types'

interface Props {
  info: BuildingInfo
}

function formatNumber(value: number | null): string {
  if (value === null || value === undefined) return 'N/A'
  return value.toLocaleString()
}

function formatMoney(value: number | null): string {
  if (value === null || value === undefined) return 'N/A'
  return `$${Math.round(value).toLocaleString()}`
}

export default function SummaryTable({ info }: Props) {
  const rows = [
    { label: 'Surface (ft²)', value: formatNumber(info.largest_property_use_type_gross_floor_area_ft2) },
    { label: 'DOB Emissions (tCO₂e)', value: formatNumber(info.dob_emissions) },
    { label: 'Calculated Emissions (tCO₂e)', value: formatNumber(info.calculated_emissions) },
    { label: 'Limit (tCO₂e)', value: formatNumber(info.emissions_limit) },
    { label: 'Excess (tCO₂e)', value: formatNumber(info.excess_emissions) },
    { label: 'Penalty', value: formatMoney(info.penalty) },
  ]

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <h3 className="text-lg font-semibold mb-4">Summary</h3>
      <table className="w-full text-sm">
        <tbody>
          {rows.map((row) => (
            <tr key={row.label} className="border-b last:border-0 border-gray-100">
              <td className="py-2 text-gray-600">{row.label}</td>
              <td className="py-2 text-right font-medium">{row.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
