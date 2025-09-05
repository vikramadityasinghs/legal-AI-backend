import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { AnalysisJob, AnalysisResults } from '../types';

interface AppState {
  currentJob: AnalysisJob | null;
  results: AnalysisResults | null;
  isLoading: boolean;
  error: string | null;
  uploadProgress: number;
}

type AppAction =
  | { type: 'SET_CURRENT_JOB'; payload: AnalysisJob }
  | { type: 'SET_RESULTS'; payload: AnalysisResults }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_UPLOAD_PROGRESS'; payload: number }
  | { type: 'CLEAR_STATE' };

const initialState: AppState = {
  currentJob: null,
  results: null,
  isLoading: false,
  error: null,
  uploadProgress: 0,
};

const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_CURRENT_JOB':
      return { ...state, currentJob: action.payload, error: null };
    case 'SET_RESULTS':
      return { ...state, results: action.payload, isLoading: false };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'SET_UPLOAD_PROGRESS':
      return { ...state, uploadProgress: action.payload };
    case 'CLEAR_STATE':
      return initialState;
    default:
      return state;
  }
};

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
