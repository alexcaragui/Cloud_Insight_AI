const ro = {
  nav: {
    dashboard: 'Panou de control',
    upload: 'Încărcare',
    chat: 'Chat AI',
    reports: 'Rapoarte',
    models: 'Modele',
  },
  sidebar: {
    brand: 'CloudInsight',
    tagline: 'Platformă AI',
    mainMenu: 'Meniu principal',
    signOut: 'Deconectare',
  },
  header: {
    toggleTheme: 'Schimbă tema',
    notifications: 'Notificări',
    noNotifications: 'Nicio notificare nouă',
    guest: 'Vizitator',
  },
  footer: {
    copyright: '© {{year}} CloudInsight AI. Toate drepturile rezervate.',
    status: 'Toate sistemele funcționează',
  },
  login: {
    title: 'CloudInsight AI',
    subtitle: 'Conectează-te la contul tău',
    button: 'Conectare',
  },
  dashboard: {
    loading: 'Se încarcă…',
    error: 'Eroare la încărcarea panoului.',
  },
  chat: {
    title: 'Chat AI',
    placeholder: 'Întreabă orice…',
    send: 'Trimite',
    thinking: 'Se gândește…',
    modelNotReady: 'Modelul nu este pregătit',
    modelNotReadyDesc: 'Modelul AI nu este instalat. Mergi la Modele pentru a-l instala.',
    goToModels: 'Mergi la Modele',
    you: 'Tu',
    assistant: 'Asistent',
    errorSending: 'Eroare la trimiterea mesajului.',
  },
  models: {
    title: 'Modele',
    subtitle: 'Gestionează modelele AI instalate local',
    installed: 'Instalat',
    downloading: 'Se descarcă…',
    install: 'Instalează',
    delete: 'Șterge',
    confirmDelete: 'Confirmi ștergerea?',
    deleting: 'Se șterge…',
    loading: 'Se încarcă modelele…',
    noModels: 'Niciun model instalat.',
    otherInstalled: 'Alte modele instalate',
    refresh: 'Reîmprospătează',
  },
  reports: {
    title: 'Pagina Rapoarte',
  },
  upload: {
    title: 'Pagina Încărcare',
  },
} as const

export default ro
