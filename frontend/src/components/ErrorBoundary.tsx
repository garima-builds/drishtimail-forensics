import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="view-container">
          <div className="card">
            <div className="card-header">
              <h3>⚠️ {this.props.fallbackTitle || 'Component Error'}</h3>
            </div>
            <div className="alert-box critical mt-3">
              <strong>Error Details:</strong>
              <pre className="mt-2 text-xs font-mono">{this.state.error?.message || 'An unexpected rendering error occurred.'}</pre>
            </div>
            <div className="mt-4">
              <button
                className="btn btn-primary"
                onClick={() => {
                  this.setState({ hasError: false, error: null });
                  if (this.props.onReset) this.props.onReset();
                }}
              >
                🔄 Retry View
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
