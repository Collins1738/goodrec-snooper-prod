import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

export default function Signup() {
  const [phone, setPhone] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.sendOtp(phone)
      navigate('/verify', { state: { phone } })
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="text-4xl mb-3">🏟️</div>
          <h1 className="text-2xl font-bold">Goodrec Snooper</h1>
          <p className="text-gray-400 mt-2 text-sm">
            Get SMS alerts when free host slots open up.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Phone number</label>
            <input
              type="tel"
              placeholder="+1 212 555 1234"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white text-base placeholder-gray-500 focus:outline-none focus:border-green-500 transition"
            />
            <p className="text-xs text-gray-500 mt-1">Include country code (e.g. +1)</p>
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-500 hover:bg-green-400 disabled:bg-green-800 disabled:cursor-not-allowed text-black font-semibold rounded-xl py-3 text-base transition"
          >
            {loading ? 'Sending...' : 'Get Started →'}
          </button>
        </form>
      </div>
    </div>
  )
}
