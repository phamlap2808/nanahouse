/**
 * Authentication composable for managing user state and API calls.
 */

interface User {
  id: number
  email: string
  full_name: string
  role: string
  avatar_url: string | null
  is_active: boolean
  created_at: string
}

interface LoginPayload {
  email: string
  password: string
}

interface RegisterPayload {
  email: string
  password: string
  full_name: string
}

interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

const TOKEN_KEY = 'nanahouse_token'
const USER_KEY = 'nanahouse_user'

export const useAuth = () => {
  const user = useState<User | null>('auth_user', () => null)
  const token = useState<string | null>('auth_token', () => null)
  const loading = useState<boolean>('auth_loading', () => false)
  const error = useState<string | null>('auth_error', () => null)

  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const initAuth = () => {
    if (import.meta.server) return
    const savedToken = localStorage.getItem(TOKEN_KEY)
    const savedUser = localStorage.getItem(USER_KEY)
    if (savedToken && savedUser) {
      token.value = savedToken
      try {
        user.value = JSON.parse(savedUser)
      } catch {
        localStorage.removeItem(USER_KEY)
      }
    }
  }

  const _authHeaders = () => ({
    Authorization: `Bearer ${token.value}`,
  })

  const _saveUser = (u: User) => {
    user.value = u
    if (import.meta.client) {
      localStorage.setItem(USER_KEY, JSON.stringify(u))
    }
  }

  const login = async (payload: LoginPayload): Promise<boolean> => {
    loading.value = true
    error.value = null
    try {
      const data = await $fetch<TokenResponse>(`${apiBase}/api/v1/auth/login`, {
        method: 'POST',
        body: payload,
      })
      token.value = data.access_token
      _saveUser(data.user)
      if (import.meta.client) {
        localStorage.setItem(TOKEN_KEY, data.access_token)
      }
      return true
    } catch (err: any) {
      const message = err?.data?.detail || err?.message || 'Login failed'
      error.value = typeof message === 'string' ? message : 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  const register = async (payload: RegisterPayload): Promise<boolean> => {
    loading.value = true
    error.value = null
    try {
      await $fetch(`${apiBase}/api/v1/auth/register`, {
        method: 'POST',
        body: payload,
      })
      return true
    } catch (err: any) {
      const message = err?.data?.detail || err?.message || 'Registration failed'
      error.value = typeof message === 'string' ? message : 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  const fetchUser = async (): Promise<boolean> => {
    if (!token.value) return false
    try {
      const data = await $fetch<User>(`${apiBase}/api/v1/auth/me`, {
        headers: _authHeaders(),
      })
      _saveUser(data)
      return true
    } catch {
      logout()
      return false
    }
  }

  const updateProfile = async (fullName: string): Promise<boolean> => {
    loading.value = true
    error.value = null
    try {
      const data = await $fetch<User>(`${apiBase}/api/v1/auth/profile`, {
        method: 'PUT',
        headers: _authHeaders(),
        body: { full_name: fullName },
      })
      _saveUser(data)
      return true
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to update profile'
      return false
    } finally {
      loading.value = false
    }
  }

  const changePassword = async (currentPassword: string, newPassword: string): Promise<boolean> => {
    loading.value = true
    error.value = null
    try {
      await $fetch(`${apiBase}/api/v1/auth/password`, {
        method: 'PUT',
        headers: _authHeaders(),
        body: { current_password: currentPassword, new_password: newPassword },
      })
      return true
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to change password'
      return false
    } finally {
      loading.value = false
    }
  }

  const uploadAvatar = async (file: File): Promise<boolean> => {
    loading.value = true
    error.value = null
    try {
      const formData = new FormData()
      formData.append('file', file)
      const data = await $fetch<User>(`${apiBase}/api/v1/auth/avatar`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token.value}` },
        body: formData,
      })
      _saveUser(data)
      return true
    } catch (err: unknown) {
      const e = err as { data?: { detail?: string } }
      error.value = e?.data?.detail || 'Failed to upload avatar'
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    if (import.meta.client) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    }
  }

  return {
    user: readonly(user),
    token: readonly(token),
    loading: readonly(loading),
    error,
    isAuthenticated,
    isAdmin,
    initAuth,
    login,
    register,
    fetchUser,
    updateProfile,
    changePassword,
    uploadAvatar,
    logout,
  }
}
