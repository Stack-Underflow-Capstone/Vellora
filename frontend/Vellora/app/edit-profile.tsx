import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, Alert, KeyboardAvoidingView, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { FontAwesome } from '@expo/vector-icons';
import { useState, useEffect } from 'react';
import { getCurrentUser, updateUserProfile, User, UserUpdatePayload } from './services/user';
import { tokenStorage } from './services/tokenStorage';

export default function EditProfile() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const fetchUser = async () => {
    const token = tokenStorage.getToken();
    if (!token) {
      router.replace('/login' as any);
      return;
    }

    try {
      const userData = await getCurrentUser();
      setUser(userData);
      setFullName(userData.full_name || '');
      setUsername(userData.username || '');
    } catch (err) {
      if (err instanceof Error && (err.message.includes("Authorization") || (err as any).status === 401)) {
        tokenStorage.clearToken();
        router.replace('/login' as any);
        return;
      }
      setError(err instanceof Error ? err.message : 'Failed to load user data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const handleSave = async () => {
    if (newPassword || confirmPassword) {
      if (!currentPassword) {
        Alert.alert('Security Required', 'Please enter your current password to change your password');
        return;
      }
      if (newPassword !== confirmPassword) {
        Alert.alert('Password Mismatch', 'New passwords do not match');
        return;
      }
      if (newPassword.length < 8) {
        Alert.alert('Weak Password', 'New password must be at least 8 characters long');
        return;
      }
    }

    setSaving(true);
    setError(null);

    try {
      const payload: UserUpdatePayload = {};
      
      if (fullName.trim() !== (user?.full_name || '')) {
        payload.full_name = fullName.trim() || null;
      }
      
      if (username.trim() !== (user?.username || '')) {
        payload.username = username.trim() || null;
      }

      if (newPassword) {
        payload.current_password = currentPassword;
        payload.new_password = newPassword;
      }

      if (Object.keys(payload).length > 0) {
        const updatedUser = await updateUserProfile(payload);
        setUser(updatedUser);
        setFullName(updatedUser.full_name || '');
        setUsername(updatedUser.username || '');
        
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
        
        Alert.alert('Success', 'Profile updated successfully!', [
          { 
            text: 'OK', 
            onPress: () => {
              router.back();
            }
          }
        ]);
      } else {
        Alert.alert('Info', 'No changes to save');
      }
    } catch (err) {
      if (err instanceof Error && (err.message.includes("Authorization") || (err as any).status === 401)) {
        tokenStorage.clearToken();
        router.replace('/login' as any);
        return;
      }
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <View className="flex-1 bg-gray-60 justify-center items-center">
        <ActivityIndicator size="large" color="#404CCF" />
        <Text className="text-gray-600 mt-2">Loading profile...</Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView 
      className="flex-1 bg-gray-60"
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View className="flex-1 px-6 pt-6">
        {error && (
          <View className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <Text className="text-red-700">{error}</Text>
          </View>
        )}

        <View className="mb-4">
          <Text className="text-gray-700 font-medium mb-2">Email</Text>
          <View className="bg-gray-100 px-4 py-3 rounded-lg">
            <Text className="text-gray-500">{user?.email}</Text>
          </View>
        </View>

        <View className="mb-4">
          <Text className="text-gray-700 font-medium mb-2">Full Name</Text>
          <TextInput
            className="bg-white border border-gray-200 px-4 py-3 rounded-lg"
            value={fullName}
            onChangeText={setFullName}
            placeholder="Enter your full name"
            maxLength={100}
          />
        </View>

        <View className="mb-4">
          <Text className="text-gray-700 font-medium mb-2">Username</Text>
          <TextInput
            className="bg-white border border-gray-200 px-4 py-3 rounded-lg"
            value={username}
            onChangeText={setUsername}
            placeholder="Enter a username"
            maxLength={30}
            autoCapitalize="none"
          />
        </View>

        <Text 
          style={{
            fontSize: 16,
            fontFamily: 'Inter',
            fontWeight: 'bold',
            color: '#404CCF',
            marginTop: 20,
            marginBottom: 12
          }}
        >
          Change Password (Optional)
        </Text>

        <View className="mb-4">
          <Text className="text-gray-700 font-medium mb-2">Current Password</Text>
          <TextInput
            className="bg-white border border-gray-200 px-4 py-3 rounded-lg"
            value={currentPassword}
            onChangeText={setCurrentPassword}
            placeholder="Enter current password"
            secureTextEntry
            maxLength={128}
          />
        </View>

        <View className="mb-4">
          <Text className="text-gray-700 font-medium mb-2">New Password</Text>
          <TextInput
            className="bg-white border border-gray-200 px-4 py-3 rounded-lg"
            value={newPassword}
            onChangeText={setNewPassword}
            placeholder="Enter new password"
            secureTextEntry
            maxLength={128}
          />
        </View>

        <View className="mb-6">
          <Text className="text-gray-700 font-medium mb-2">Confirm New Password</Text>
          <TextInput
            className="bg-white border border-gray-200 px-4 py-3 rounded-lg"
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            placeholder="Confirm new password"
            secureTextEntry
            maxLength={128}
          />
        </View>

        <TouchableOpacity 
          style={{
            backgroundColor: '#22C55E',
            paddingVertical: 14,
            borderRadius: 24,
            alignItems: 'center',
            opacity: saving ? 0.5 : 1,
            marginTop: 24
          }}
          onPress={handleSave}
          disabled={saving}
        >
          {saving ? (
            <View className="flex-row items-center">
              <ActivityIndicator size="small" color="#fff" style={{ marginRight: 8 }} />
              <Text style={{ color: '#fff', fontSize: 16, fontWeight: '600' }}>Saving...</Text>
            </View>
          ) : (
            <Text style={{ color: '#fff', fontSize: 16, fontWeight: '600' }}>Save Changes</Text>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}