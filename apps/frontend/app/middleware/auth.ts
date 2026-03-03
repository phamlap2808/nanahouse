/**
 * Auth middleware: redirects unauthenticated users to /login.
 * Only runs on client-side to avoid SSR flash (no localStorage on server).
 */
export default defineNuxtRouteMiddleware((_to) => {
  // Skip auth check on server — localStorage is unavailable during SSR
  if (import.meta.server) return

  const { isAuthenticated, initAuth } = useAuth()
  initAuth()

  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})
