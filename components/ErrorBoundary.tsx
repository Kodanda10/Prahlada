import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
}

interface ErrorBoundaryProps {
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = {
    hasError: false,
  };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: unknown, info: React.ErrorInfo) {
    console.error('UI Error Boundary caught exception', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="p-6 bg-red-500/10 border border-red-500/40 rounded-2xl text-red-200 text-sm font-hindi">
            कोई त्रुटि हुई है। हमारी टीम इसे ठीक कर रही है।
          </div>
        )
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
