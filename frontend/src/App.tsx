import { Routes, Route, Navigate } from 'react-router-dom'
import Signup from './pages/Signup'
import Verify from './pages/Verify'
import Preferences from './pages/Preferences'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Signup />} />
      <Route path="/verify" element={<Verify />} />
      <Route path="/preferences" element={<Preferences />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
