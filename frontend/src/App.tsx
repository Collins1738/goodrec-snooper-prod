import { Routes, Route, Navigate } from 'react-router-dom'
import { Analytics } from '@vercel/analytics/react'
import Signup from './pages/Signup'
import Verify from './pages/Verify'
import Preferences from './pages/Preferences'
import Admin from './pages/Admin'
import PrivacyPolicy from './pages/PrivacyPolicy'
import TermsOfService from './pages/TermsOfService'

export default function App() {
  return (
    <>
      <Analytics />
      <Routes>
        <Route path="/" element={<Signup />} />
        <Route path="/verify" element={<Verify />} />
        <Route path="/preferences" element={<Preferences />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/privacy" element={<PrivacyPolicy />} />
        <Route path="/terms" element={<TermsOfService />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}
