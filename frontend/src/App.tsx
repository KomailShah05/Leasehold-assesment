import { useEffect, useState } from 'react'
import { fetchHealth } from './api/client'

type Connection = 'checking' | 'connected' | 'unavailable'

/**
 * Placeholder shell for the triage journey. For now it only confirms that the
 * React app can reach the Django API; the journey itself is a later ticket.
 */
const App = () => {
  const [connection, setConnection] = useState<Connection>('checking')

  useEffect(() => {
    let cancelled = false
    fetchHealth().then((result) => {
      if (cancelled) return
      setConnection(result.ok ? 'connected' : 'unavailable')
    })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <main>
      <h1>Leasehold enquiry triage</h1>
      <p>
        This prototype will help you describe a leasehold problem and point you to guidance. It
        does not give legal advice.
      </p>
      <p role="status">
        {connection === 'checking' && 'Checking the connection to the service…'}
        {connection === 'connected' && 'Connected to the service.'}
        {connection === 'unavailable' && 'The service is not available right now.'}
      </p>
    </main>
  )
}

export default App
