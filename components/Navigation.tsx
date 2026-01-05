'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useSession, signOut } from 'next-auth/react'

export default function Navigation() {
  const pathname = usePathname()
  const router = useRouter()
  const { data: session, status } = useSession()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const isActive = (path: string) => mounted && pathname === path

  const handleSignOut = async () => {
    await signOut({ redirect: false })
    router.push('/')
    router.refresh()
  }

  return (
    <nav className="flex gap-4 items-center">
      <Link
        href="/"
        className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
          isActive('/')
            ? 'bg-blue-600 text-white'
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
        }`}
      >
        Home
      </Link>
      {status === 'authenticated' && (
        <>
          <Link
            href="/submit"
            className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              isActive('/submit')
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            Submit Shop
          </Link>
          <Link
            href="/profile"
            className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              isActive('/profile')
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            Profile
          </Link>
          {(session?.user as any)?.role === 'admin' && (
            <Link
              href="/admin"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/admin')
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              Admin
            </Link>
          )}
        </>
      )}
      <div className="ml-auto flex items-center gap-3">
        {status === 'loading' ? (
          <div className="h-8 w-20 bg-gray-200 rounded animate-pulse"></div>
        ) : status === 'authenticated' ? (
          <>
            <span className="text-sm text-gray-600">
              {session?.user?.name || session?.user?.email}
            </span>
            <button
              onClick={handleSignOut}
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
            >
              Sign Out
            </button>
          </>
        ) : (
          <Link
            href="/auth/signin"
            className="px-3 py-2 rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            Sign In
          </Link>
        )}
      </div>
    </nav>
  )
}

