import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { api, setToken } from '../lib/api'

export default function Verify() {
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const location = useLocation()
  const phone = (location.state as any)?.phone || ''

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { access_token } = await api.verifyOtp(phone, code)
      setToken(access_token)
      navigate('/preferences')
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
          <div className="text-4xl mb-3">📱</div>
          <h1 className="text-2xl font-bold">Check your texts</h1>
          <p className="text-gray-400 mt-2 text-sm">
            We sent a 4-digit code to <span className="text-white">{phone}</span>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={4}
            placeholder="1234"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
            required
            className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white text-center text-2xl tracking-widest placeholder-gray-600 focus:outline-none focus:border-green-500 transition"
          />

          {error && <p className="text-red-400 text-sm text-center">{error}</p>}

          <button
            type="submit"
            disabled={loading || code.length < 4}
            className="w-full bg-green-500 hover:bg-green-400 disabled:bg-green-800 disabled:cursor-not-allowed text-black font-semibold rounded-xl py-3 text-base transition"
          >
            {loading ? 'Verifying...' : 'Verify →'}
          </button>

          <button
            type="button"
            onClick={() => navigate('/')}
            className="w-full text-gray-500 text-sm hover:text-gray-300 transition"
          >
            ← Change number
          </button>
        </form>
      </div>
    </div>
  )
}
