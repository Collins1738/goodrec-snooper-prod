import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, clearToken } from '../lib/api'

type Venue = { key: string; name: string }

export default function Preferences() {
  const navigate = useNavigate()
  const [venues, setVenues] = useState<Venue[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  function handleLogout() {
    clearToken()
    navigate('/')
  }

  useEffect(() => {
    async function load() {
      try {
        const [venueList, prefs] = await Promise.all([
          api.getVenues(),
          api.getPreferences(),
        ])
        setVenues(venueList)
        setSelected(new Set(prefs.venue_keys))
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  function toggle(key: string) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
    setSaved(false)
  }

  async function handleSave() {
    setSaving(true)
    setError('')
    try {
      await api.updatePreferences(Array.from(selected))
      setSaved(true)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-400">
        Loading...
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center px-4 py-12">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="text-4xl mb-3">🔔</div>
          <h1 className="text-2xl font-bold">Your alerts</h1>
          <p className="text-gray-400 mt-2 text-sm">
            Pick which venues to watch. We'll text you when a free host slot opens.
          </p>
        </div>

        <div className="space-y-3 mb-8">
          {venues.map((venue) => (
            <button
              key={venue.key}
              onClick={() => toggle(venue.key)}
              className={`w-full flex items-center justify-between px-4 py-4 rounded-xl border transition ${
                selected.has(venue.key)
                  ? 'border-green-500 bg-green-500/10 text-white'
                  : 'border-gray-700 bg-gray-800 text-gray-300'
              }`}
            >
              <span className="text-base font-medium">{venue.name}</span>
              <span className={`text-xl ${selected.has(venue.key) ? 'opacity-100' : 'opacity-0'}`}>
                ✓
              </span>
            </button>
          ))}
        </div>

        {error && <p className="text-red-400 text-sm text-center mb-4">{error}</p>}

        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full bg-green-500 hover:bg-green-400 disabled:bg-green-800 disabled:cursor-not-allowed text-black font-semibold rounded-xl py-3 text-base transition"
        >
          {saving ? 'Saving...' : saved ? '✓ Saved' : 'Save preferences'}
        </button>

        <button
          onClick={handleLogout}
          className="w-full mt-4 text-gray-500 hover:text-gray-300 text-sm py-2 transition"
        >
          Log out
        </button>
      </div>
    </div>
  )
}
