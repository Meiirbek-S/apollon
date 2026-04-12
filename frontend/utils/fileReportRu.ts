export function verdictToRu(verdict: 'SAFE' | 'SUSPICIOUS' | 'MALWARE-LIKE'): string {
  if (verdict === 'SAFE') return 'БЕЗОПАСНО'
  if (verdict === 'SUSPICIOUS') return 'ПОДОЗРИТЕЛЬНО'
  return 'ОПАСНО'
}

export function humanizeIndicatorRu(indicator: string): string {
  const value = indicator.toLowerCase()

  if (value.includes('createprocess') || value.includes('winexec') || value.includes('shellexecute')) {
    return 'Файл использует функции запуска других процессов.'
  }
  if (value.includes('loadlibrary') || value.includes('getprocaddress')) {
    return 'Файл динамически загружает системные библиотеки.'
  }
  if (value.includes('virtualalloc') || value.includes('writememory') || value.includes('createremotethread')) {
    return 'Обнаружены признаки внедрения кода в память.'
  }
  if (value.includes('powershell') || value.includes('cmd.exe')) {
    return 'Файл может запускать скриптовые или консольные команды.'
  }
  if (value.includes('packed') || value.includes('entropy')) {
    return 'Обнаружена высокая энтропия или признаки упаковки/обфускации файла.'
  }
  if (value.includes('rwx')) {
    return 'Обнаружена секция с правами чтения/записи/исполнения (RWX).'
  }
  if (value.includes('suspicious import')) {
    return 'Обнаружены подозрительные функции в импортах.'
  }
  if (value.includes('network') || value.includes('socket') || value.includes('http')) {
    return 'Файл содержит признаки сетевой активности.'
  }

  return indicator
}
