import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import {
  Text,
  TextInput,
  Button,
  Card,
  Title,
  Paragraph,
  HelperText,
} from 'react-native-paper';
import { useAuthStore } from '../../store';
import { mlbApi } from '../../services/mlbApi';

interface Props {
  navigation: any;
}

export default function RegisterScreen({ navigation }: Props) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const { login, register } = useAuthStore();

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!formData.firstName) {
      newErrors.firstName = 'First name is required';
    }

    if (!formData.lastName) {
      newErrors.lastName = 'Last name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleRegister = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      await register({
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName,
      });

      Alert.alert('Success', 'Account created successfully!');
    } catch (error: any) {
      Alert.alert('Registration Failed', error.message || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.logoContainer}>
          <Title style={styles.title}>Join MLB Analytics</Title>
          <Paragraph style={styles.subtitle}>
            Create your account to get started
          </Paragraph>
        </View>

        <Card style={styles.card}>
          <Card.Content>
            <Title style={styles.cardTitle}>Sign Up</Title>
            
            <View style={styles.nameContainer}>
              <TextInput
                mode="outlined"
                label="First Name"
                value={formData.firstName}
                onChangeText={(value) => updateField('firstName', value)}
                style={[styles.input, styles.nameInput]}
                disabled={loading}
                error={!!errors.firstName}
              />
              <TextInput
                mode="outlined"
                label="Last Name"
                value={formData.lastName}
                onChangeText={(value) => updateField('lastName', value)}
                style={[styles.input, styles.nameInput]}
                disabled={loading}
                error={!!errors.lastName}
              />
            </View>
            
            {errors.firstName && (
              <HelperText type="error">{errors.firstName}</HelperText>
            )}
            {errors.lastName && (
              <HelperText type="error">{errors.lastName}</HelperText>
            )}

            <TextInput
              mode="outlined"
              label="Email"
              value={formData.email}
              onChangeText={(value) => updateField('email', value)}
              keyboardType="email-address"
              autoCapitalize="none"
              style={styles.input}
              disabled={loading}
              error={!!errors.email}
            />
            {errors.email && (
              <HelperText type="error">{errors.email}</HelperText>
            )}

            <TextInput
              mode="outlined"
              label="Password"
              value={formData.password}
              onChangeText={(value) => updateField('password', value)}
              secureTextEntry
              style={styles.input}
              disabled={loading}
              error={!!errors.password}
            />
            {errors.password && (
              <HelperText type="error">{errors.password}</HelperText>
            )}

            <TextInput
              mode="outlined"
              label="Confirm Password"
              value={formData.confirmPassword}
              onChangeText={(value) => updateField('confirmPassword', value)}
              secureTextEntry
              style={styles.input}
              disabled={loading}
              error={!!errors.confirmPassword}
            />
            {errors.confirmPassword && (
              <HelperText type="error">{errors.confirmPassword}</HelperText>
            )}

            <Button
              mode="contained"
              onPress={handleRegister}
              loading={loading}
              disabled={loading}
              style={styles.button}
              contentStyle={styles.buttonContent}
            >
              Create Account
            </Button>

            <View style={styles.linkContainer}>
              <Text style={styles.linkText}>Already have an account? </Text>
              <Button
                mode="text"
                onPress={() => navigation.navigate('Login')}
                disabled={loading}
                compact
              >
                Sign In
              </Button>
            </View>
          </Card.Content>
        </Card>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1976d2',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  card: {
    elevation: 4,
    borderRadius: 12,
  },
  cardTitle: {
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  nameContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  nameInput: {
    flex: 1,
    marginHorizontal: 4,
  },
  input: {
    marginBottom: 8,
  },
  button: {
    marginTop: 10,
    marginBottom: 20,
  },
  buttonContent: {
    paddingVertical: 8,
  },
  linkContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  linkText: {
    color: '#666',
  },
});
