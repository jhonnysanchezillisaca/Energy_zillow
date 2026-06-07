import { useState } from 'react'
import { getRecommendations } from '../api'
import type { RecommendationResponse } from '../types'

interface Props {
  bbl: number
}

export default function Recommendations({ bbl }: Props) {
  const [result, setResult] = useState<RecommendationResponse | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleGenerate = async () => {
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const data = await getRecommendations(bbl)
      setResult(data)
    } catch (err: any) {
      if (err.response?.status === 500) {
        setError('Recommendations service is temporarily unavailable.')
      } else if (err.response?.status === 404) {
        setError('Building not found for recommendations.')
      } else {
        setError('Failed to generate recommendations.')
      }
    } finally {
      setLoading(false)
    }
  }

  // Parse numbered list from the recommendation text
  const parseRecommendations = (text: string): string[] => {
    // Split by newlines and filter lines that start with a number
    return text
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => /^\d+[.)]/.test(line))
  }

  const tips = result ? parseRecommendations(result.recommendations) : []

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <h3 className="text-lg font-semibold mb-4">Improve Building Efficiency</h3>

      {!result && (
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Generating...' : 'Generate 5 Efficiency Tips'}
        </button>
      )}

      {error && (
        <div className="mt-4 p-3 text-red-700 bg-red-50 border border-red-200 rounded-lg text-sm">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-700">Recommendations</h4>
            <button
              onClick={() => setResult(null)}
              className="text-sm text-blue-600 hover:underline"
            >
              Regenerate
            </button>
          </div>
          {tips.length > 0 ? (
            <ol className="space-y-3">
              {tips.map((tip, idx) => (
                <li
                  key={idx}
                  className="p-3 bg-gray-50 border border-gray-100 rounded-lg text-sm leading-relaxed"
                >
                  {tip}
                </li>
              ))}
            </ol>
          ) : (
            <pre className="p-3 bg-gray-50 border border-gray-100 rounded-lg text-sm whitespace-pre-wrap">
              {result.recommendations}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}
