/**
 * Formatiert Bytes in eine lesbare Größenangabe
 */
export function formatBytes(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Formatiert einen Prozentsatz
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Formatiert ein Datum in ein lesbares Format
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  
  if (isNaN(date.getTime())) {
    return 'Ungültiges Datum';
  }

  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  // Relative Zeit für kürzliche Zeitpunkte
  if (diffMins < 1) {
    return 'Gerade eben';
  } else if (diffMins < 60) {
    return `vor ${diffMins} Minute${diffMins === 1 ? '' : 'n'}`;
  } else if (diffHours < 24) {
    return `vor ${diffHours} Stunde${diffHours === 1 ? '' : 'n'}`;
  } else if (diffDays < 7) {
    return `vor ${diffDays} Tag${diffDays === 1 ? '' : 'en'}`;
  }

  // Absolutes Datum für ältere Zeitpunkte
  return date.toLocaleDateString('de-DE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Formatiert eine Zeitdauer in Sekunden
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  }
}

/**
 * Formatiert eine Anzahl mit Tausender-Trennzeichen
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('de-DE');
}

/**
 * Kürzt einen Dateipfad für die Anzeige
 */
export function truncatePath(path: string, maxLength: number = 50): string {
  if (path.length <= maxLength) return path;
  
  const parts = path.split(/[/\\]/);
  if (parts.length <= 2) return path;
  
  let result = parts[0] + '/.../' + parts[parts.length - 1];
  
  // Falls immer noch zu lang, kürze den Dateinamen
  if (result.length > maxLength) {
    const fileName = parts[parts.length - 1];
    const extension = fileName.includes('.') ? '.' + fileName.split('.').pop() : '';
    const baseName = fileName.replace(extension, '');
    const maxBaseName = maxLength - parts[0].length - 6 - extension.length; // 6 für "/.../"
    
    if (maxBaseName > 3) {
      result = parts[0] + '/.../' + baseName.substring(0, maxBaseName) + '...' + extension;
    }
  }
  
  return result;
}