import { useEffect, useState } from 'react'
import { api } from '../lib/api'

// ── Types ─────────────────────────────────────────────────────────────────────

type Stats = {
  total_users: number
  verified_users: number
  total_subscriptions: number
  total_notified_events: number
}

type AdminUser = {
  id: string
  phone: string
  verified: boolean
  created_at: string
  venue_keys: string[]
}

type Game = {
  event_id: string
  venue_key: string
  venue_name: string
  date: string
  start_time: string
  deeplink: string
  subscribed_users: string[]
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function maskPhone(phone: string): string {
  if (phone.length <= 4) return phone
  return '••••••• ' + phone.slice(-4)
}

function formatGameTime(startTime: string): string {
  if (!startTime) return 'TBD'
  try {
    const dt = new Date(startTime)
    return dt.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
  } catch {
    return startTime
  }
}

function formatJoined(isoDate: string): string {
  if (!isoDate) return ''
  try {
    return new Date(isoDate).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  } catch {
    return isoDate
  }
}

const VENUE_LABELS: Record<string, string> = {
  socceroof_crown_heights: 'Crown Heights',
  socceroof_wall_street: 'Wall St',
}

function venueLabel(key: string): string {
  return VENUE_LABELS[key] ?? key
}

// ── Stat Card ─────────────────────────────────────────────────────────────────

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="flex-1 bg-gray-800 rounded-xl px-3 py-3 text-center min-w-0">
      <div className="text-xl font-bold text-white">{value}</div>
      <div className="text-xs text-gray-400 mt-0.5 leading-tight">{label}</div>
    </div>
  )
}

// ── Users Tab ─────────────────────────────────────────────────────────────────

function UsersTab({ users }: { users: AdminUser[] }) {
  if (users.length === 0) {
    return (
      <div className="text-center text-gray-500 py-12">
        <div className="text-3xl mb-2">👤</div>
        <p className="text-sm">No users yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {users.map((user) => (
        <div key={user.id} className="bg-gray-800 rounded-xl px-4 py-4">
          <div className="flex items-center justify-between mb-2">
            <span className="font-mono text-white text-sm font-medium">
              {maskPhone(user.phone)}
            </span>
            {user.verified ? (
              <span className="flex items-center gap-1 text-green-400 text-xs font-medium bg-green-400/10 px-2 py-0.5 rounded-full">
                ✓ verified
              </span>
            ) : (
              <span className="flex items-center gap-1 text-gray-500 text-xs font-medium bg-gray-700 px-2 py-0.5 rounded-full">
                unverified
              </span>
            )}
          </div>
          <div className="text-xs text-gray-500 mb-3">
            Joined {formatJoined(user.created_at)}
          </div>
          {user.venue_keys.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {user.venue_keys.map((key) => (
                <span
                  key={key}
                  className="text-xs bg-green-500/10 text-green-400 border border-green-500/20 px-2.5 py-1 rounded-full"
                >
                  {venueLabel(key)}
                </span>
              ))}
            </div>
          ) : (
            <span className="text-xs text-gray-600 italic">No venues subscribed</span>
          )}
        </div>
      ))}
    </div>
  )
}

// ── Games Tab ─────────────────────────────────────────────────────────────────

function GameCard({ game }: { game: Game }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="bg-gray-800 rounded-xl px-4 py-4">
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1 min-w-0">
          <div className="text-white font-medium text-sm">{game.venue_name}</div>
          <div className="text-gray-400 text-xs mt-0.5">{formatGameTime(game.start_time)}</div>
        </div>
        <span
          className={`shrink-0 text-xs font-semibold px-2.5 py-1 rounded-full ${
            game.subscribed_users.length > 0
              ? 'bg-green-500/10 text-green-400 border border-green-500/20'
              : 'bg-gray-700 text-gray-500'
          }`}
        >
          {game.subscribed_users.length}{' '}
          {game.subscribed_users.length === 1 ? 'subscriber' : 'subscribers'}
        </span>
      </div>

      <div className="flex items-center gap-3 mt-3">
        <a
          href={game.deeplink}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-green-400 underline underline-offset-2"
        >
          View on Goodrec ↗
        </a>
        {game.subscribed_users.length > 0 && (
          <button
            onClick={() => setExpanded((v) => !v)}
            className="text-xs text-gray-400 hover:text-gray-200 transition"
          >
            {expanded ? '▲ Hide' : '▼ Show'} users
          </button>
        )}
      </div>

      {expanded && game.subscribed_users.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-700 space-y-1.5">
          {game.subscribed_users.map((phone) => (
            <div key={phone} className="font-mono text-xs text-gray-300">
              {maskPhone(phone)}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function GamesTab({ games }: { games: Game[] }) {
  if (games.length === 0) {
    return (
      <div className="text-center text-gray-500 py-12">
        <div className="text-3xl mb-2">⚽</div>
        <p className="text-sm">No upcoming games found</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {games.map((game) => (
        <GameCard key={game.event_id} game={game} />
      ))}
    </div>
  )
}

// ── Tokens Tab ────────────────────────────────────────────────────────────────

type TokenStatus = {
  access_token_preview: string
  expires_at: number | null
  expired: boolean
}

function TokensTab() {
  const [status, setStatus] = useState<TokenStatus | null>(null)
  const [loadingStatus, setLoadingStatus] = useState(true)
  const [accessToken, setAccessToken] = useState('')
  const [refreshToken, setRefreshToken] = useState('')
  const [seeding, setSeeding] = useState(false)
  const [seedMsg, setSeedMsg] = useState<{ ok: boolean; text: string } | null>(null)

  async function fetchStatus() {
    setLoadingStatus(true)
    try {
      const data = await api.getTokenStatus()
      setStatus(data)
    } catch {
      setStatus(null)
    } finally {
      setLoadingStatus(false)
    }
  }

  useEffect(() => { fetchStatus() }, [])

  async function handleSeed(e: React.FormEvent) {
    e.preventDefault()
    if (!accessToken.trim() || !refreshToken.trim()) return
    setSeeding(true)
    setSeedMsg(null)
    try {
      await api.seedTokens(accessToken.trim(), refreshToken.trim())
      setSeedMsg({ ok: true, text: 'Tokens saved successfully.' })
      setAccessToken('')
      setRefreshToken('')
      await fetchStatus()
    } catch (err: any) {
      setSeedMsg({ ok: false, text: err.message || 'Failed to save tokens.' })
    } finally {
      setSeeding(false)
    }
  }

  function formatExpiry(epoch: number | null): string {
    if (epoch === null) return 'Unknown'
    return new Date(epoch * 1000).toLocaleString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: 'numeric', minute: '2-digit', hour12: true,
    })
  }

  return (
    <div className="space-y-5">
      {/* Current status */}
      <div className="bg-gray-800 rounded-xl px-4 py-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-300">Current Token Status</h2>
          <button
            onClick={fetchStatus}
            disabled={loadingStatus}
            className="text-xs text-gray-400 hover:text-white transition disabled:opacity-40"
          >
            {loadingStatus ? 'Loading…' : 'Refresh'}
          </button>
        </div>
        {status ? (
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Access token</span>
              <span className="font-mono text-xs text-gray-300">{status.access_token_preview}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Expires</span>
              <span className="text-xs text-gray-300">{formatExpiry(status.expires_at)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Status</span>
              {status.expired ? (
                <span className="text-xs font-semibold text-red-400 bg-red-400/10 px-2 py-0.5 rounded-full">Expired</span>
              ) : (
                <span className="text-xs font-semibold text-green-400 bg-green-400/10 px-2 py-0.5 rounded-full">Valid</span>
              )}
            </div>
          </div>
        ) : (
          <p className="text-xs text-gray-500">{loadingStatus ? 'Checking…' : 'Could not load token status.'}</p>
        )}
      </div>

      {/* Seed form */}
      <div className="bg-gray-800 rounded-xl px-4 py-4">
        <h2 className="text-sm font-semibold text-gray-300 mb-3">Seed Fresh Tokens</h2>
        <p className="text-xs text-gray-500 mb-4">
          Use when the refresh token has expired. Capture fresh tokens via Proxyman from the Goodrec app and paste below.
        </p>
        <form onSubmit={handleSeed} className="space-y-3">
          <div>
            <label className="block text-xs text-gray-400 mb-1">Access Token</label>
            <textarea
              value={accessToken}
              onChange={(e) => setAccessToken(e.target.value)}
              rows={3}
              placeholder="eyJ..."
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-xs font-mono text-white placeholder-gray-600 focus:outline-none focus:border-green-500 resize-none"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Refresh Token</label>
            <textarea
              value={refreshToken}
              onChange={(e) => setRefreshToken(e.target.value)}
              rows={3}
              placeholder="eyJ..."
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-xs font-mono text-white placeholder-gray-600 focus:outline-none focus:border-green-500 resize-none"
            />
          </div>
          {seedMsg && (
            <div className={`text-xs px-3 py-2 rounded-lg ${seedMsg.ok ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
              {seedMsg.text}
            </div>
          )}
          <button
            type="submit"
            disabled={seeding || !accessToken.trim() || !refreshToken.trim()}
            className="w-full py-2.5 rounded-xl bg-green-500 text-black text-sm font-semibold disabled:opacity-40 hover:bg-green-400 transition"
          >
            {seeding ? 'Saving…' : 'Save Tokens'}
          </button>
        </form>
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function Admin() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [users, setUsers] = useState<AdminUser[]>([])
  const [games, setGames] = useState<Game[]>([])
  const [tab, setTab] = useState<'users' | 'games' | 'tokens'>('users')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const [statsData, usersData, gamesData] = await Promise.all([
        api.getAdminStats() as Promise<Stats>,
        api.getAdminUsers() as Promise<{ users: AdminUser[]; total: number }>,
        api.getAdminGames() as Promise<{ games: Game[] }>,
      ])
      setStats(statsData)
      setUsers(usersData.users)
      setGames(gamesData.games)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center px-4 py-8">
      <div className="w-full max-w-lg">

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold">Goodrec Admin</h1>
            <p className="text-xs text-gray-500 mt-0.5">Dashboard</p>
          </div>
          <button
            onClick={load}
            disabled={loading}
            className="p-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 disabled:opacity-40 transition text-gray-300 hover:text-white"
            title="Refresh"
          >
            <svg
              className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl px-4 py-3 mb-5">
            {error}
          </div>
        )}

        {/* Stats Row */}
        {stats && (
          <div className="flex gap-2 mb-6">
            <StatCard label="Users" value={stats.total_users} />
            <StatCard label="Verified" value={stats.verified_users} />
            <StatCard label="Subscriptions" value={stats.total_subscriptions} />
            <StatCard label="Games" value={games.length} />
          </div>
        )}

        {/* Tabs */}
        <div className="flex bg-gray-800 rounded-xl p-1 mb-5">
          <button
            onClick={() => setTab('users')}
            className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition ${
              tab === 'users'
                ? 'bg-green-500 text-black'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Users
          </button>
          <button
            onClick={() => setTab('games')}
            className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition ${
              tab === 'games'
                ? 'bg-green-500 text-black'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Games
          </button>
          <button
            onClick={() => setTab('tokens')}
            className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition ${
              tab === 'tokens'
                ? 'bg-green-500 text-black'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Tokens
          </button>
        </div>

        {/* Tab Content */}
        {tab === 'tokens' ? (
          <TokensTab />
        ) : loading ? (
          <div className="text-center text-gray-500 py-12">
            <div className="text-sm">Loading...</div>
          </div>
        ) : tab === 'users' ? (
          <UsersTab users={users} />
        ) : (
          <GamesTab games={games} />
        )}

      </div>
    </div>
  )
}
