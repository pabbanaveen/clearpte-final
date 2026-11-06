// src/components/LoginModal.tsx
import React, { useEffect, useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  CircularProgress,
  Alert,
  Link
} from '@mui/material';

interface LoginModalProps {
  open: boolean;
  onClose: () => void;
  onLogin: (credentials: { email: string; password: string; name?: string }) => Promise<AuthFormResult | void>;
  onRegister: (data: { name: string; email: string; password: string }) => Promise<AuthFormResult | void>;
  onResendVerification?: (email: string, password: string) => Promise<{ success: boolean; message: string }>;
  loading?: boolean;
  selectedMode: string; // 'login' or 'register'
}

interface AuthFormResult {
  requiresEmailVerification?: boolean;
  email?: string;
  message?: string;
}

const LoginModal: React.FC<LoginModalProps> = ({ open, onClose, onLogin, onRegister, onResendVerification, loading = false, selectedMode }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [localLoading, setLocalLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [verificationEmail, setVerificationEmail] = useState<string | null>(null);
  const [verificationMessage, setVerificationMessage] = useState<string | null>(null);

  useEffect(() => {
    if (selectedMode === 'register') {
      setMode('register');
    }
    else {
      setMode('login');
    }
  }, [selectedMode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setVerificationMessage(null);
    setLocalLoading(true);

    try {
      let result: AuthFormResult | void;
      if (mode === 'login') {
        result = await onLogin({ email, password });
      } else {
        result = await onRegister({ name, email, password });
      }
      if (result?.requiresEmailVerification) {
        setVerificationEmail(result.email || email.trim());
        setVerificationMessage(result.message || 'Please verify your email before continuing.');
        setMode('login');
      }
      // success -> app will close modal
    } catch (err: any) {
      setError(err?.message || 'Authentication failed');
    } finally {
      setLocalLoading(false);
    }
  };

  const handleResendVerification = async () => {
    if (!onResendVerification || !verificationEmail || !password) return;
    setError(null);
    setLocalLoading(true);
    try {
      const result = await onResendVerification(verificationEmail, password);
      if (result.success) {
        setVerificationMessage(result.message);
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err?.message || 'Could not resend the verification email.');
    } finally {
      setLocalLoading(false);
    }
  };

  const handleClose = () => {
    if (localLoading || loading) return;
    setName('');
    setEmail('');
    setPassword('');
    setError(null);
    setVerificationEmail(null);
    setVerificationMessage(null);
    onClose();
  };

  const isLoading = localLoading || loading;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ textAlign: 'center', pb: 2 }}>
        {mode === 'login' ? 'Login to PTE Practice' : 'Create your account'}
      </DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {verificationMessage && (
          <Alert severity="info" sx={{ mb: 2 }}>
            {verificationMessage}
            {verificationEmail && onResendVerification && (
              <Box sx={{ mt: 1 }}>
                <Button
                  size="small"
                  onClick={handleResendVerification}
                  disabled={isLoading || !password}
                >
                  Resend verification email
                </Button>
              </Box>
            )}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          {mode === 'register' && (
            <TextField
              autoFocus
              margin="dense"
              label="Full Name"
              type="text"
              fullWidth
              variant="outlined"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={isLoading}
              required
              sx={{ mb: 2 }}
            />
          )}

          <TextField
            autoFocus={mode === 'login'}
            margin="dense"
            label="Email Address"
            type="email"
            fullWidth
            variant="outlined"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isLoading}
            required
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Password"
            type="password"
            fullWidth
            variant="outlined"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            required
            sx={{ mb: 2 }}
          />

          <DialogActions sx={{ px: 0, pt: 2 }}>
            <Button onClick={handleClose} disabled={isLoading} color="inherit">Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={isLoading || !email || !password || (mode === 'register' && !name)}
              startIcon={isLoading ? <CircularProgress size={16} /> : null}
              sx={{ minWidth: 100 }}
            >
              {isLoading ? (mode === 'login' ? 'Logging in...' : 'Registering...') : (mode === 'login' ? 'Login' : 'Register')}
            </Button>
          </DialogActions>
        </form>

        <Box sx={{ textAlign: 'center', mt: 2 }}>
          {mode === 'login' ? (
            <Typography variant="body2">
              Don’t have an account?{' '}
              <Link component="button" variant="body2" onClick={() => { setError(null); setMode('register'); }}>Register here</Link>
            </Typography>
          ) : (
            <Typography variant="body2">
              Already have an account?{' '}
              <Link component="button" variant="body2" onClick={() => { setError(null); setMode('login'); }}>Login</Link>
            </Typography>
          )}
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default LoginModal;
