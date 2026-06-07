export interface SearchResult {
  bbl: number
  property_name: string | null
  address: string | null
  match_score: number
}

export interface BuildingInfo {
  bbl: number
  calendar_year: number
  property_name: string | null
  address: string | null
  address_1: string | null
  status: boolean
  status_text: string
  status_color: string
  ranking: number | null
  energy_star_score: number | null
  largest_property_use_type_gross_floor_area_ft2: number | null
  calculated_emissions: number | null
  emissions_limit: number | null
  excess_emissions: number | null
  difference: number | null
  relative_to_limit: number | null
  dob_emissions: number | null
  penalty: number | null
}

export interface PenaltyForecast {
  calendar_year: number
  bbl: number
  penalty_2030: number | null
  penalty_2035: number | null
  penalty_2040: number | null
}

export interface FuelBreakdown {
  calendar_year: number
  bbl: number
  fuel_oil: number | null
  electricity: number | null
  natural_gas: number | null
  others: number | null
}

export interface FutureConsumptionScenario {
  year: string
  scenario: string
  value: number
}

export interface RecommendationResponse {
  bbl: number
  recommendations: string
}

export interface BuildingDetail {
  info: BuildingInfo
  penalties: PenaltyForecast | null
  fuels: FuelBreakdown | null
  future_consumption: FutureConsumptionScenario[]
}
