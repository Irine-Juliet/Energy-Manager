import { createContext, useState, useContext, useEffect, ReactNode } from 'react'
import api from '../utils/api'
import { User, LoginCredentials, SignupData } from '../types'

interface AuthContextType {
  user: User | null
  login: (username: string, password: string) => Promise<void>
  signup: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('token')
    if (token) {
      // Validate token and get user info
      // TODO: Implement user validation
      setLoading(false)
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (username: string, password: string) => {
    // TODO: Implement login API call
    const response = await api.post('/auth/login/', { username, password })
    localStorage.setItem('token', response.data.token)
    setUser(response.data.user)
  }

  const signup = async (username: string, email: string, password: string) => {
    // TODO: Implement signup API call
    const response = await api.post('/auth/signup/', { username, email, password })
    localStorage.setItem('token', response.data.token)
    setUser(response.data.user)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
