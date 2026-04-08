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

  const selectedCount = selected.size

  return (
    <div className="h-screen flex flex-col items-center bg-gray-950">
      <div className="w-full max-w-sm flex flex-col h-full">

        {/* Fixed header */}
        <div className="pt-10 pb-4 px-4 text-center shrink-0">
          <div className="text-4xl mb-3">🔔</div>
          <h1 className="text-2xl font-bold text-white">Your alerts</h1>
          <p className="text-gray-400 mt-2 text-sm">
            Pick which venues to watch. We'll text you when a free host slot opens.
          </p>
        </div>

        {/* Selected count badge */}
        {venues.length > 0 && (
          <div className="px-4 pb-2 shrink-0">
            <p className="text-xs text-green-400 text-center">
              {selectedCount === 0
                ? 'None selected'
                : `${selectedCount} venue${selectedCount === 1 ? '' : 's'} selected`}
            </p>
          </div>
        )}

        {/* Scrollable venue list */}
        <div className="flex-1 overflow-y-auto px-4 py-1 space-y-2">
          {venues.map((venue) => (
            <button
              key={venue.key}
              onClick={() => toggle(venue.key)}
              className={`w-full flex items-center justify-between px-4 py-3 rounded-xl border transition ${
                selected.has(venue.key)
                  ? 'border-green-500 bg-green-500/10 text-white'
                  : 'border-gray-700 bg-gray-800 text-gray-300'
              }`}
            >
              <span className="text-base font-medium text-left">{venue.name}</span>
              <span
                className={`text-lg ml-2 shrink-0 transition-opacity ${
                  selected.has(venue.key) ? 'opacity-100 text-green-400' : 'opacity-0'
                }`}
              >
                ✓
              </span>
            </button>
          ))}
        </div>

        {/* Fixed footer — always visible */}
        <div className="shrink-0 px-4 pt-3 pb-8 border-t border-gray-800 bg-gray-950">
          {error && <p className="text-red-400 text-sm text-center mb-3">{error}</p>}

          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full bg-green-500 hover:bg-green-400 disabled:bg-green-800 disabled:cursor-not-allowed text-black font-semibold rounded-xl py-3 text-base transition"
          >
            {saving ? 'Saving...' : saved ? '✓ Saved' : 'Save preferences'}
          </button>

          <button
            onClick={handleLogout}
            className="w-full mt-3 text-gray-500 hover:text-gray-300 text-sm py-2 transition"
          >
            Log out
          </button>
        </div>
      </div>
    </div>
  )
}
