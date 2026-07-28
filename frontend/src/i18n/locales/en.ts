const en = {
  nav: {
    dashboard: 'Dashboard',
    upload: 'Upload',
    chat: 'AI Chat',
    reports: 'Reports',
    models: 'Models',
  },
  sidebar: {
    brand: 'CloudInsight',
    tagline: 'AI Platform',
    mainMenu: 'Main Menu',
    signOut: 'Sign Out',
  },
  header: {
    toggleTheme: 'Toggle theme',
    notifications: 'Notifications',
    noNotifications: 'No new notifications',
    guest: 'Guest',
  },
  footer: {
    copyright: '© {{year}} CloudInsight AI. All rights reserved.',
    status: 'All systems operational',
  },
  login: {
    title: 'CloudInsight AI',
    subtitle: 'Sign in to your account',
    button: 'Login',
  },
  dashboard: {
    loading: 'Loading…',
    error: 'Failed to load dashboard.',
  },
  chat: {
    title: 'AI Chat',
    placeholder: 'Ask anything…',
    send: 'Send',
    thinking: 'Thinking…',
    modelNotReady: 'Model not ready',
    modelNotReadyDesc: 'The AI model is not installed yet. Go to Models to install it.',
    goToModels: 'Go to Models',
    you: 'You',
    assistant: 'Assistant',
    errorSending: 'Failed to send message.',
  },
  models: {
    title: 'Models',
    subtitle: 'Manage locally installed AI models',
    installed: 'Installed',
    downloading: 'Downloading…',
    install: 'Install',
    delete: 'Delete',
    confirmDelete: 'Confirm delete?',
    deleting: 'Deleting…',
    loading: 'Loading models…',
    noModels: 'No models installed.',
    otherInstalled: 'Other installed models',
    refresh: 'Refresh',
  },
  reports: {
    title: 'Reports Page',
  },
  upload: {
    title: 'Upload Page',
  },
} as const

export default en
