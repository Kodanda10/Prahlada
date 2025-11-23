import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import PageWrapper from '../components/PageWrapper';
import PageLoader from '../components/PageLoader';
import { sanitizeHtmlInput } from '../utils/security';

const Login: React.FC = () => {
  const { login, status, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const from = (location.state as { from?: Location })?.from?.pathname ?? '/';

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setFormError(null);

    const sanitizedUsername = sanitizeHtmlInput(username);

    if (!sanitizedUsername || !password) {
      setFormError('उपयोगकर्ता नाम और पासवर्ड आवश्यक हैं।');
      return;
    }

    try {
      await login(sanitizedUsername, password);
      navigate(from, { replace: true });
    } catch (authError) {
      const message = authError instanceof Error ? authError.message : 'लॉगिन विफल रहा।';
      setFormError(message);
    }
  };

  if (status === 'loading') {
    return <PageLoader message="प्रमाणीकरण जारी है…" />;
  }

  return (
    <div className="min-h-screen bg-[#0f172a] flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-500/20 rounded-full blur-[100px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/20 rounded-full blur-[100px]" />
      </div>

      <div className="w-full max-w-md relative z-10">
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2 font-hindi">प्रह्लाद एडमिन</h1>
            <p className="text-slate-400 text-sm font-hindi">सुरक्षित डैशबोर्ड एक्सेस</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="username" className="text-xs font-bold text-slate-300 uppercase tracking-wider font-hindi">
                उपयोगकर्ता आईडी (User ID)
              </label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                placeholder="admin"
                className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3.5 text-white focus:outline-none focus:border-[#8BF5E6] focus:bg-black/40 transition-all placeholder:text-slate-600"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-xs font-bold text-slate-300 uppercase tracking-wider font-hindi">
                पासवर्ड (Password)
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3.5 text-white focus:outline-none focus:border-[#8BF5E6] focus:bg-black/40 transition-all placeholder:text-slate-600"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </div>

            {(formError ?? error) ? (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20">
                <p className="text-xs text-red-200 font-hindi text-center">
                  {formError ?? error}
                </p>
              </div>
            ) : null}

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-[#8BF5E6] to-[#4FD1C5] text-[#0f172a] font-bold py-4 rounded-xl hover:shadow-[0_0_20px_rgba(139,245,230,0.3)] transition-all transform hover:scale-[1.02] active:scale-[0.98] font-hindi text-sm uppercase tracking-wide"
            >
              लॉगिन करें (Login)
            </button>
          </form>
          
          <div className="mt-6 text-center">
             <p className="text-[10px] text-slate-500 font-hindi">
               डिफ़ॉल्ट क्रेडेंशियल्स: admin / SuperSecurePassword123!
             </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
