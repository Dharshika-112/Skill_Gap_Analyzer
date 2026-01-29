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
import RoleDetail from './pages/RoleDetail';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={
              <>
                <Navbar />
                <LandingPage />
              </>
            } />
            <Route path="/login" element={
              <>
                <Navbar />
                <Login />
              </>
            } />
            <Route path="/signup" element={
              <>
                <Navbar />
                <Signup />
              </>
            } />
            
            {/* User Protected Routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Navbar />
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/skill-gap-analyzer" element={
              <ProtectedRoute>
                <Navbar />
                <SkillGapAnalyzer />
              </ProtectedRoute>
            } />
            <Route path="/resume-scoring" element={
              <ProtectedRoute>
                <Navbar />
                <ResumeScoring />
              </ProtectedRoute>
            } />
            <Route path="/improvement-suggestions" element={
              <ProtectedRoute>
                <Navbar />
                <ImprovementSuggestions />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <Navbar />
                <Profile />
              </ProtectedRoute>
            } />
            <Route path="/role/:roleId" element={
              <ProtectedRoute>
                <Navbar />
                <RoleDetail />
              </ProtectedRoute>
            } />
            
            {/* Admin Routes (No Navbar) */}
            <Route path="/admin" element={<AdminLogin />} />
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;