/**
 * User Context
 * Additional user-related state management
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { useAuth } from './AuthContext';

interface UserContextType {
  isAdmin: boolean;
  isEmployee: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { user } = useAuth();

  const value = {
    isAdmin: user?.role === 'ADMIN',
    isEmployee: user?.role === 'EMPLOYEE',
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};
