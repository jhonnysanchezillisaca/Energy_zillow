import { Routes, Route } from 'react-router-dom'
import SearchPage from './pages/SearchPage'
import BuildingPage from './pages/BuildingPage'

function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <Routes>
        <Route path="/" element={<SearchPage />} />
        <Route path="/building/:bbl" element={<BuildingPage />} />
      </Routes>
    </div>
  )
}

export default App
