import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import SkillGapAnalyzer from './pages/SkillGapAnalyzer';
import ResumeScoring from './pages/ResumeScoring';
import ImprovementSuggestions from './pages/ImprovementSuggestions';
import Profile from './pages/Profile';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/skill-gap-analyzer" element={
              <ProtectedRoute>
                <SkillGapAnalyzer />
              </ProtectedRoute>
            } />
            <Route path="/resume-scoring" element={
              <ProtectedRoute>
                <ResumeScoring />
              </ProtectedRoute>
            } />
            <Route path="/improvement-suggestions" element={
              <ProtectedRoute>
                <ImprovementSuggestions />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;