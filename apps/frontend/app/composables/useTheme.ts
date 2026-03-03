/**
 * Theme composable for managing dark/light mode toggle.
 * Persists theme preference to localStorage.
 */

type Theme = 'dark' | 'light'

const THEME_KEY = 'nanahouse_theme'

export const useTheme = () => {
  const theme = useState<Theme>('app_theme', () => 'dark')

  const isDark = computed(() => theme.value === 'dark')

  const initTheme = () => {
    if (import.meta.server) return

    const saved = localStorage.getItem(THEME_KEY) as Theme | null
    if (saved && (saved === 'dark' || saved === 'light')) {
      theme.value = saved
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      theme.value = prefersDark ? 'dark' : 'light'
    }

    applyTheme(theme.value)
  }

  const toggleTheme = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'

    if (import.meta.client) {
      localStorage.setItem(THEME_KEY, theme.value)
    }

    applyTheme(theme.value)
  }

  const applyTheme = (t: Theme) => {
    if (import.meta.server) return
    document.documentElement.setAttribute('data-theme', t)
  }

  return {
    theme: readonly(theme),
    isDark,
    initTheme,
    toggleTheme,
  }
}
