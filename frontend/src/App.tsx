import { Routes, Route, Navigate } from 'react-router-dom'
import { Analytics } from '@vercel/analytics/react'
import Signup from './pages/Signup'
import Verify from './pages/Verify'
import Preferences from './pages/Preferences'

export default function App() {
  return (
    <>
      <Analytics />
      <Routes>
        <Route path="/" element={<Signup />} />
        <Route path="/verify" element={<Verify />} />
        <Route path="/preferences" element={<Preferences />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}
