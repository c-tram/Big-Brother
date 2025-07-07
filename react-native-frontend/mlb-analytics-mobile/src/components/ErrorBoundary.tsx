import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Title, Paragraph, Button } from 'react-native-paper';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error; resetError: () => void }>;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback;
        return <FallbackComponent error={this.state.error!} resetError={this.resetError} />;
      }

      return <DefaultErrorFallback error={this.state.error!} resetError={this.resetError} />;
    }

    return this.props.children;
  }
}

interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
}

const DefaultErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetError }) => (
  <View style={styles.container}>
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.title}>Something went wrong</Title>
        <Paragraph style={styles.message}>
          An unexpected error occurred. Please try again.
        </Paragraph>
        <Paragraph style={styles.errorDetails}>
          {error.message}
        </Paragraph>
        <Button
          mode="contained"
          onPress={resetError}
          style={styles.button}
        >
          Try Again
        </Button>
      </Card.Content>
    </Card>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  card: {
    width: '100%',
    maxWidth: 400,
    elevation: 4,
  },
  title: {
    textAlign: 'center',
    marginBottom: 16,
    color: '#d32f2f',
  },
  message: {
    textAlign: 'center',
    marginBottom: 16,
    color: '#666',
  },
  errorDetails: {
    textAlign: 'center',
    marginBottom: 20,
    fontSize: 12,
    color: '#999',
    fontFamily: 'monospace',
  },
  button: {
    marginTop: 8,
  },
});

export default ErrorBoundary;
