import React, { useState, useEffect } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Alert, Snackbar } from '@mui/material';
import theme from './theme';
import { User } from './types/index';
import { Header } from './components/Header';
import HomePage from './components/dashboard/HomePage';
import LoginModal from './components/LoginModal';
import PracticeTests from './components/PracticeTests';
import Profile from './components/Profile';
import ProgressTracking from './components/ProgressTracking';
import StudyMaterials from './components/StudyMaterials';
import Dashboard from './components/Dashboard';
import AIPracticeSection from './components/dashboard/AIPracticeSection';
import ReadAloud from './components/practice/speaking/read-a-loud/ReadAloud';
import DescribeImage from './components/practice/speaking/describeImage/DescribeImage';
import FillInBlanks from './components/practice/Reading/fillin-blanks/FillInBlanks';
import ReorderParagraphs from './components/practice/Reading/re-order-paragraphs/ReorderParagraphs';
import RepeatSentence from './components/practice/speaking/repeat-sectence/RepeatSentence';
import WritingEssay from './components/practice/Writing/writing-essay/WritingEssay';
import { ReTellLeacture } from './components/practice/speaking/re-tell-leacture/ReTellLeacture';
import { AnswerShortQuestionsScreen } from './components/practice/speaking/answer-short-questions/AnswerShortQuestionsScreen';
import SummarizeText from './components/practice/Writing/summarize-text/SummarizeText';
import WriteEmail from './components/practice/Writing/emailWriting/writeEmail';
import MultipleChoice from './components/practice/Reading/multiple-choice/MultipleChoice';
import ReadingFillBlanks from './components/practice/Reading/ReadingFillInTheBlanks/ReadingFillInTheBlanks';
import MultipleChoiceSingle from './components/practice/Reading/multiple-choice-single/mutlipleChoiceSingle';
import SummarizeSpokenText from './components/practice/Listening/SummarizeSpokenText/SummarizeSpokenText';
import ListeningMultipleChoice from './components/practice/Listening/MultipleChoiceMultiple/MutlipleChoiceMultiple';
import ListeningFillBlanks from './components/practice/Listening/FillinTheBlanks/FillinTheBlanks';
import HighlightCorrectSummary from './components/practice/Listening/HighlightCorrectSummary/HighlightCorrectSummary';
import SelectMissingWord from './components/practice/Listening/SelectMissingWord/SelectMissingWord';
import HighlightIncorrectWords from './components/practice/Listening/HighlightIncorrectWords/HighlightIncorrectWords';
import WriteFromDictation from './components/practice/Listening/WriteFromDictation/WriteFromDictation';
import { Box } from '@mui/system';
import MultipleChoiceSingleListening from './components/practice/Listening/MultipleChoiceSingle/MultipleChoiceSingle';
import { authService } from './services/authService';
import { SearchProvider } from './components/contexts/SearchContext';
import GlobalSearchButton from './components/GlobalSearchButton';
import FloatingSearchDemo from './components/common/FloatingSearchButton';
import AdminDashboardNew from './components/admin/AdminDashboardNew';
import EnhancedAdminDemo from './components/admin/EnhancedAdminDemo';
import { GlobalStateContext, initialState, reducer } from './store/context';
import CoursePage from './components/course/CoursePage';
import SpellingTest from './components/spelling/SpellingTest';

const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [authActionLoading, setAuthActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selecteOperationMode, setSelectedOperationMode] = useState<string>('');
  const [state, dispatch] = React.useReducer(reducer, initialState);

  // Restore Firebase Auth state first, then any explicitly legacy DB session.
  useEffect(() => {
    let active = true;
    const initAuth = async () => {
      try {
        const { isAuthenticated, user: storedUser } = await authService.initializeAuth();

        if (active && isAuthenticated && storedUser) {
          setIsLoggedIn(true);
          setUser(storedUser);
        } else if (active) {
          setIsLoggedIn(false);
          setUser(null);
        }
      } catch {
        if (active) {
          setError('Failed to restore session. Please sign in again.');
          setIsLoggedIn(false);
          setUser(null);
        }
      } finally {
        if (active) setLoading(false);
      }
    };

    initAuth();
    return () => {
      active = false;
    };
  }, []);

  const handleRegister = async (data: { name: string; email: string; password: string }) => {
    try {
      setAuthActionLoading(true);
      setError(null);

      const response = await authService.registerWithFirebase(data);

      if (response.requiresEmailVerification) {
        return {
          requiresEmailVerification: true,
          email: response.email || data.email,
          message: response.message,
        };
      }

      if (response.success && response.data) {
        setUser(response.data.user);
        setIsLoggedIn(true);
        setLoginOpen(false);
        setError(null);
      } else {
        throw new Error(response.message || 'Registration failed');
      }
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Registration failed. Please try again.');
    } finally {
      setAuthActionLoading(false);
    }
  };

  const handleLogin = async (credentials: { email: string; password: string }) => {
    try {
      setAuthActionLoading(true);
      setError(null);

      const response = await authService.loginWithFirebase(credentials);

      if (response.requiresEmailVerification) {
        return {
          requiresEmailVerification: true,
          email: response.email || credentials.email,
          message: response.message,
        };
      }

      if (response.success && response.data) {
        setUser(response.data.user);
        setIsLoggedIn(true);
        setLoginOpen(false);
        setError(null);
      } else {
        throw new Error(response.message || 'Login failed');
      }
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Login failed. Please try again.');
    } finally {
      setAuthActionLoading(false);
    }
  };

  const handleResendVerification = (email: string, password: string) =>
    authService.resendVerificationEmail(email, password);

  const handleLogout = async () => {
    await authService.logout().catch(() => undefined);
    setUser(null);
    setIsLoggedIn(false);
    setError(null);
  };

  const handleCloseError = () => {
    setError(null);
  };

  const selectedMode = (data: string) => {
    setSelectedOperationMode(data);
  };

  // Show loading spinner while initializing
  if (loading) {
    return (
      <GlobalStateContext.Provider value={{ state, dispatch }}>
        
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="100vh"
          sx={{ backgroundColor: '#f5f5f5' }}
        >
          <Box textAlign="center">
            <div>Loading...</div>
          </Box>
        </Box>
        </ThemeProvider>
      </GlobalStateContext.Provider>
    );
  }

  return (
    <SearchProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <div className="App">
            <Header
              isLoggedIn={isLoggedIn}
              user={user}
              onLoginClick={() => setLoginOpen(true)}
              onLogout={handleLogout}
              isAdmin={authService.isAdmin()}
              selectedMode={selectedMode}
            />

            {/* Global Floating Search Button */}
            <GlobalSearchButton />

            <Routes>
              <Route
                path="/"
                element={
                  isLoggedIn ? (
                    <Dashboard user={user} />
                  ) : (
                    <HomePage onGetStarted={() => setLoginOpen(true)} />
                  )
                }
              />
              {/* Public routes */}
              <Route path="/dashboard" element={isLoggedIn ? <Dashboard user={user} /> : <Navigate to="/" replace />} />
              <Route path="/practice-tests" element={isLoggedIn ? <PracticeTests user={user} /> : <Navigate to="/" replace />} />
              <Route path="/study-materials" element={isLoggedIn ? <StudyMaterials user={user} /> : <Navigate to="/" replace />} />
              <Route path="/ai-practice" element={isLoggedIn ? <AIPracticeSection /> : <Navigate to="/" replace />} />
              <Route path="/progress" element={isLoggedIn ? <ProgressTracking user={user} /> : <Navigate to="/" replace />} />
              <Route path="/profile" element={isLoggedIn ? <Profile user={user} setUser={setUser} /> : <Navigate to="/" replace />} />

              {/* Speaking Practice Routes */}
              <Route path="/practice/speaking/read-aloud" element={isLoggedIn ? <ReadAloud user={user} /> : <Navigate to="/" replace />} />
              <Route path="/practice/speaking/repeat-sentence" element={isLoggedIn ? <RepeatSentence user={user} /> : <Navigate to="/" replace />} />
              <Route path="/practice/speaking/describe-image" element={isLoggedIn ? <DescribeImage /> : <Navigate to="/" replace />} />
              <Route path="/practice/speaking/answer-short-question" element={isLoggedIn ? <AnswerShortQuestionsScreen user={user} /> : <Navigate to="/" replace />} />
              <Route path="/practice/speaking/respond-situation" element={isLoggedIn ? <PracticeTests user={user} /> : <Navigate to="/" replace />} />
              <Route path="/practice/speaking/retell-lecture" element={isLoggedIn ? <ReTellLeacture user={user} /> : <Navigate to="/" replace />} />

              {/* Writing Practice Routes */}
              <Route path="/practice/writing/summarize-text" element={isLoggedIn ? <SummarizeText user={user} /> : <Navigate to="/" replace />} />
              <Route path="/practice/writing/write-email" element={isLoggedIn ? <WriteEmail user={user} /> : <Navigate to="/" replace />} />
              <Route path="/practice/writing/summarize-text-core" element={isLoggedIn ? <PracticeTests user={user} /> : <Navigate to="/" replace />} />
              <Route path="/practice/writing/write-essay" element={isLoggedIn ? <WritingEssay /> : <Navigate to="/" replace />} />

              {/* Reading Practice Routes */}
              <Route path="/practice/reading/fill-blanks-rw" element={isLoggedIn ? <ReadingFillBlanks /> : <Navigate to="/" replace />} />
              <Route path="/practice/reading/multiple-choice-multiple" element={isLoggedIn ? <MultipleChoice user={user} /> : <Navigate to="/" replace />} />
              <Route path="/practice/reading/reorder-paragraphs" element={isLoggedIn ? <ReorderParagraphs /> : <Navigate to="/" replace />} />
              <Route path="/practice/reading/fill-blanks" element={isLoggedIn ? <FillInBlanks /> : <Navigate to="/" replace />} />
              <Route path="/practice/reading/multiple-choice-single" element={isLoggedIn ? <MultipleChoiceSingle /> : <Navigate to="/" replace />} />

              {/* Listening Practice Routes */}
              <Route path="/practice/listening/summarize-spoken-text" element={isLoggedIn ? <SummarizeSpokenText /> : <Navigate to="/" replace />} />
              <Route path="/practice/listening/multiple-choice-multiple" element={isLoggedIn ? <ListeningMultipleChoice user={user} /> : <Navigate to="/" replace />} />
              <Route path="/practice/listening/fill-blanks" element={isLoggedIn ? <ListeningFillBlanks /> : <Navigate to="/" replace />} />
              <Route path="/practice/listening/multiple-choice-single" element={isLoggedIn ? <MultipleChoiceSingleListening /> : <Navigate to="/" replace />} />
              <Route path="/practice/listening/select-missing-word" element={isLoggedIn ? <SelectMissingWord /> : <Navigate to="/" replace />} />
              <Route path="/practice/listening/highlight-incorrect" element={isLoggedIn ? <HighlightIncorrectWords /> : <Navigate to="/" replace />} />
              <Route path="/practice/listening/write-dictation" element={isLoggedIn ? <WriteFromDictation /> : <Navigate to="/" replace />} />
              <Route path="/practice/listening/summarize-spoken-text-core" element={isLoggedIn ? <PracticeTests user={user} /> : <Navigate to="/" replace />} />
              <Route path="/practice/listening/highlight-summary" element={isLoggedIn ? <HighlightCorrectSummary /> : <Navigate to="/" replace />} />

              {/* Additional Feature Routes */}
              <Route path="/vocab-books" element={isLoggedIn ? <StudyMaterials user={user} /> : <Navigate to="/" replace />} />
              <Route path="/shadowing" element={isLoggedIn ? <AIPracticeSection /> : <Navigate to="/" replace />} />
              <Route path="/ai-analysis" element={isLoggedIn ? <ProgressTracking user={user} /> : <Navigate to="/" replace />} />
              <Route path="/ai-study-plan" element={isLoggedIn ? <Dashboard user={user} /> : <Navigate to="/" replace />} />
              <Route path="/mock-tests" element={isLoggedIn ? <PracticeTests user={user} /> : <Navigate to="/" replace />} />
              <Route path="/course" element={isLoggedIn ? <CoursePage /> : <Navigate to="/" replace />} />
              <Route path="/spelling-test" element={isLoggedIn ? <SpellingTest /> : <Navigate to="/" replace />} />
              <Route path="/downloads" element={isLoggedIn ? <StudyMaterials user={user} /> : <Navigate to="/" replace />} />

              {/* Demo Route */}
              <Route path="/demo/floating-search" element={<FloatingSearchDemo />} />

            {/* Enhanced Admin Demo Route */}
            {/* <Route path="/admin/demo" element={
              isLoggedIn && authService.isAdmin() ? <EnhancedAdminDemo /> : <Navigate to="/" replace />
            } /> */}
              {authService.isAdmin() &&
                (<Route path="/admin/new" element={
                  isLoggedIn && authService.isAdmin() ? <AdminDashboardNew /> : <Navigate to="/" replace />
                } />)}
             
            </Routes>

            <LoginModal
              open={loginOpen}
              onClose={() => setLoginOpen(false)}
              onLogin={handleLogin}
              onRegister={handleRegister}
              onResendVerification={handleResendVerification}
              loading={authActionLoading}
              selectedMode={selecteOperationMode}
            />

            {/* Error Snackbar */}
            <Snackbar
              open={!!error}
              autoHideDuration={6000}
              onClose={handleCloseError}
              anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            >
              <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
                {error}
              </Alert>
            </Snackbar>
          </div>
        </Router>
      </ThemeProvider>
    </SearchProvider>
  );
};

export default App;