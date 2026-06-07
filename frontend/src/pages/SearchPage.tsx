import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { searchBuilding } from '../api'
import type { SearchResult } from '../types'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<SearchResult | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const data = await searchBuilding(query)
      setResult(data)
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('No building found for that address.')
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const goToBuilding = (bbl: number) => {
    navigate(`/building/${bbl}`)
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4">
      <div className="w-full max-w-xl">
        <h1 className="text-3xl font-bold mb-2 text-center">Energy Dashboard</h1>
        <p className="text-gray-600 mb-8 text-center">
          Search NYC buildings to explore emissions, penalties, and efficiency recommendations.
        </p>

        <form onSubmit={handleSearch} className="flex gap-2 mb-6">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter address, e.g. 1 Wall Street"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        {error && (
          <div className="p-4 mb-4 text-red-700 bg-red-50 border border-red-200 rounded-lg">
            {error}
          </div>
        )}

        {result && (
          <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-5">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-semibold">{result.property_name || 'Unnamed Building'}</h2>
                <p className="text-gray-600">{result.address}</p>
                <p className="text-sm text-gray-400 mt-1">BBL: {result.bbl}</p>
              </div>
              <div className="text-right">
                <span className="inline-block px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                  Match: {Math.round(result.match_score)}%
                </span>
              </div>
            </div>
            <button
              onClick={() => goToBuilding(result.bbl)}
              className="mt-4 w-full px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800"
            >
              View Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
