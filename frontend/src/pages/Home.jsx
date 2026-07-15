import { Navigate } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'

import { hasSessionHint } from '../lib/api'



function Home() {

  const { isLoading } = useAuth()



  // Guests never need a /auth/me round-trip before landing on the dashboard.

  if (!hasSessionHint()) {

    return <Navigate to="/dashboard" replace />

  }



  if (isLoading) {

    return (

      <div

        className="flex min-h-screen items-center justify-center bg-white"

        role="status"

        aria-live="polite"

      >

        <p className="text-sm text-gray-600">Loading…</p>

      </div>

    )

  }



  return <Navigate to="/dashboard" replace />

}



export default Home


