import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
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
    console.error('Uncaught React render error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '30px', color: '#ff6b6b', background: '#121418', minHeight: '100vh', fontFamily: 'sans-serif' }}>
          <h2>Application Rendering Error</h2>
          <p style={{ marginTop: '10px', color: '#fff' }}>
            {this.state.error?.message || 'An unexpected error occurred.'}
          </p>
          <pre style={{ marginTop: '15px', padding: '15px', background: '#0a0c0f', borderRadius: '6px', color: '#888', overflowX: 'auto' }}>
            {this.state.error?.stack}
          </pre>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: '20px',
              padding: '10px 18px',
              background: '#38bdf8',
              color: '#000',
              fontWeight: 700,
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
            }}
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
