import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getBuildingDetail } from '../api'
import type { BuildingDetail } from '../types'

import BuildingHeader from '../components/BuildingHeader'
import MetricsCards from '../components/MetricsCards'
import PenaltyForecastChart from '../components/PenaltyForecastChart'
import EmissionsVsLimitChart from '../components/EmissionsVsLimitChart'
import SummaryTable from '../components/SummaryTable'
import EmissionsBreakdownChart from '../components/EmissionsBreakdownChart'
import FutureConsumptionChart from '../components/FutureConsumptionChart'
import Recommendations from '../components/Recommendations'

export default function BuildingPage() {
  const { bbl } = useParams<{ bbl: string }>()
  const navigate = useNavigate()
  const [data, setData] = useState<BuildingDetail | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!bbl) return
    const bblNum = parseInt(bbl, 10)
    if (isNaN(bblNum)) {
      setError('Invalid BBL')
      setLoading(false)
      return
    }

    setLoading(true)
    setError('')
    getBuildingDetail(bblNum)
      .then((detail) => {
        setData(detail)
      })
      .catch((err) => {
        if (err.response?.status === 404) {
          setError('Building not found.')
        } else {
          setError('Failed to load building data.')
        }
      })
      .finally(() => setLoading(false))
  }, [bbl])

  if (loading) {
    return (
      <div className="p-6">
        <p className="text-gray-500">Loading building data...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="p-4 mb-4 text-red-700 bg-red-50 border border-red-200 rounded-lg">
          {error}
        </div>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800"
        >
          Back to Search
        </button>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="p-6">
        <p className="text-gray-500">No data available.</p>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <button
        onClick={() => navigate('/')}
        className="mb-4 px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
      >
        Back to Search
      </button>

      <BuildingHeader info={data.info} />
      <MetricsCards info={data.info} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <PenaltyForecastChart penalties={data.penalties} info={data.info} />
          <EmissionsVsLimitChart info={data.info} />
        </div>
        <div>
          <SummaryTable info={data.info} />
          <EmissionsBreakdownChart fuels={data.fuels} />
        </div>
      </div>

      <FutureConsumptionChart scenarios={data.future_consumption} />
      <Recommendations bbl={data.info.bbl} />
    </div>
  )
}
