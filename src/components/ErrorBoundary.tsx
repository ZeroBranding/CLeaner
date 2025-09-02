import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // Log to Electron main process if available
    if (window.electronAPI?.log) {
      window.electronAPI.log('error', 'React Error Boundary', {
        error: error.toString(),
        stack: error.stack,
        componentStack: errorInfo.componentStack,
      });
    }

    // Update state with error details
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return <>{this.props.fallback}</>;
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-dark-bg-primary flex items-center justify-center p-4">
          <div className="max-w-2xl w-full">
            <div className="glass-card p-8 text-center">
              {/* Error Icon */}
              <div className="flex justify-center mb-6">
                <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-10 h-10 text-red-500" />
                </div>
              </div>

              {/* Error Title */}
              <h1 className="text-3xl font-bold text-white mb-4">
                Ups! Etwas ist schiefgelaufen
              </h1>

              {/* Error Message */}
              <p className="text-gray-400 mb-6">
                Ein unerwarteter Fehler ist aufgetreten. Das tut uns leid!
                Versuchen Sie, die Seite neu zu laden oder kehren Sie zur Startseite zurück.
              </p>

              {/* Error Details (Development only) */}
              {import.meta.env.DEV && this.state.error && (
                <div className="bg-dark-bg-secondary rounded-lg p-4 mb-6 text-left">
                  <h3 className="text-sm font-semibold text-gray-400 mb-2">
                    Fehlerdetails (nur in Entwicklung sichtbar):
                  </h3>
                  <pre className="text-xs text-red-400 overflow-auto max-h-40">
                    {this.state.error.toString()}
                    {this.state.error.stack && (
                      <>
                        {'\n\n'}
                        Stack Trace:
                        {'\n'}
                        {this.state.error.stack}
                      </>
                    )}
                  </pre>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={this.handleReset}
                  className="px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg 
                           font-semibold transition-colors duration-200 flex items-center justify-center gap-2"
                >
                  <RefreshCw className="w-5 h-5" />
                  Erneut versuchen
                </button>

                <button
                  onClick={this.handleReload}
                  className="px-6 py-3 bg-dark-bg-tertiary hover:bg-dark-bg-quaternary text-white 
                           rounded-lg font-semibold transition-colors duration-200 flex items-center justify-center gap-2"
                >
                  <RefreshCw className="w-5 h-5" />
                  Seite neu laden
                </button>

                <button
                  onClick={this.handleGoHome}
                  className="px-6 py-3 bg-dark-bg-tertiary hover:bg-dark-bg-quaternary text-white 
                           rounded-lg font-semibold transition-colors duration-200 flex items-center justify-center gap-2"
                >
                  <Home className="w-5 h-5" />
                  Zur Startseite
                </button>
              </div>

              {/* Support Information */}
              <div className="mt-8 pt-6 border-t border-gray-800">
                <p className="text-sm text-gray-500">
                  Wenn das Problem weiterhin besteht, kontaktieren Sie bitte den Support oder
                  erstellen Sie ein Issue auf{' '}
                  <a
                    href="https://github.com/ZeroBranding/CLeaner/issues"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-400 hover:text-primary-300 underline"
                  >
                    GitHub
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;