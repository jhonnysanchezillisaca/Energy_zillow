import axios from 'axios'
import type { SearchResult, BuildingDetail, FutureConsumptionScenario, RecommendationResponse } from './types'

const API_BASE = import.meta.env.VITE_API_URL || ''

const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

export async function searchBuilding(address: string): Promise<SearchResult> {
  const res = await client.get('/api/v1/search', { params: { address } })
  return res.data
}

export async function getBuildingDetail(bbl: number): Promise<BuildingDetail> {
  const res = await client.get(`/api/v1/buildings/${bbl}`)
  return res.data
}

export async function getFutureConsumption(bbl: number): Promise<FutureConsumptionScenario[]> {
  const res = await client.get(`/api/v1/buildings/${bbl}/future`)
  return res.data
}

export async function getRecommendations(bbl: number): Promise<RecommendationResponse> {
  const res = await client.get(`/api/v1/buildings/${bbl}/recommendations`)
  return res.data
}
