import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { LogIn, User, Lock, AlertCircle, Sparkles } from 'lucide-react';
import useAuth from '../hooks/useAuth';
import PageLoader from '../components/PageLoader';
import { sanitizeHtmlInput } from '../utils/security';

const Login: React.FC = () => {
  const { login, status, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [isFocused, setIsFocused] = useState<'username' | 'password' | null>(null);
  const from = (location.state as { from?: Location })?.from?.pathname ?? '/';

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setFormError(null);

    const sanitizedUsername = sanitizeHtmlInput(username);

    if (!sanitizedUsername || !password) {
      setFormError('यूजर आईडी और पासवर्ड आवश्यक हैं।');
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
    <div className="min-h-screen w-full bg-[#2e1065] bg-gradient-to-br from-[#1e1b4b] via-[#2e1065] to-[#4c1d95] text-white overflow-hidden font-sans selection:bg-[#8BF5E6] selection:text-[#2e1065] flex items-center justify-center px-4 relative">
      
      {/* Ambient Background Effects - Aurora Style */}
      <motion.div 
        animate={{ 
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        className="fixed top-[-20%] left-[-10%] w-[800px] h-[800px] bg-purple-600/20 rounded-full blur-[120px] pointer-events-none z-0" 
      />
      <motion.div 
        animate={{ 
          scale: [1, 1.1, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut", delay: 2 }}
        className="fixed bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none z-0" 
      />

      {/* Login Card */}
      <motion.div
        initial={{ opacity: 0, y: 50, scale: 0.9 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, type: "spring", stiffness: 100 }}
        className="w-full max-w-md relative z-10"
      >
        <div className="bg-white/5 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 md:p-10 shadow-[0_8px_32px_0_rgba(139,245,230,0.1)] relative overflow-hidden">
          
          {/* Animated Border Glow */}
          <motion.div
            animate={{
              opacity: [0.3, 0.6, 0.3],
            }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            className="absolute inset-0 rounded-3xl bg-gradient-to-r from-[#8BF5E6]/20 via-purple-500/20 to-pink-500/20 blur-xl pointer-events-none"
          />

          {/* Header */}
          <div className="text-center mb-8 relative z-10">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-[#8BF5E6] to-blue-600 mb-4 shadow-lg shadow-[#8BF5E6]/20"
            >
              <Sparkles className="text-[#0f172a]" size={32} strokeWidth={2.5} />
            </motion.div>
            
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-3xl md:text-4xl font-bold text-white mb-2 font-hindi tracking-tight"
            >
              सोशल मीडिया एनालिटिक्स डैशबोर्ड
            </motion.h1>
            
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: "120px", opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.8 }}
              className="h-[2px] bg-gradient-to-r from-transparent via-[#8BF5E6] to-transparent mx-auto rounded-full"
            />
          </div>

          {/* Form */}
          <motion.form
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            onSubmit={handleSubmit}
            className="space-y-5 relative z-10"
          >
            {/* Username Field */}
            <div className="space-y-2">
              <label htmlFor="username" className="text-xs font-bold text-slate-300 uppercase tracking-wider font-hindi flex items-center gap-2">
                <User size={14} className="text-[#8BF5E6]" />
                यूजर आईडी
              </label>
              <motion.div
                animate={{
                  scale: isFocused === 'username' ? 1.02 : 1,
                }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  placeholder="admin"
                  className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3.5 text-white focus:outline-none focus:border-[#8BF5E6] focus:bg-black/40 focus:shadow-[0_0_20px_rgba(139,245,230,0.1)] transition-all placeholder:text-slate-600"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  onFocus={() => setIsFocused('username')}
                  onBlur={() => setIsFocused(null)}
                />
              </motion.div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <label htmlFor="password" className="text-xs font-bold text-slate-300 uppercase tracking-wider font-hindi flex items-center gap-2">
                <Lock size={14} className="text-[#8BF5E6]" />
                पासवर्ड
              </label>
              <motion.div
                animate={{
                  scale: isFocused === 'password' ? 1.02 : 1,
                }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••"
                  className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3.5 text-white focus:outline-none focus:border-[#8BF5E6] focus:bg-black/40 focus:shadow-[0_0_20px_rgba(139,245,230,0.1)] transition-all placeholder:text-slate-600"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  onFocus={() => setIsFocused('password')}
                  onBlur={() => setIsFocused(null)}
                />
              </motion.div>
            </div>

            {/* Error Message */}
            <AnimatePresence>
              {(formError ?? error) && (
                <motion.div
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                  transition={{ type: "spring", stiffness: 300 }}
                  className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 backdrop-blur-sm"
                >
                  <p className="text-xs text-red-200 font-hindi text-center flex items-center justify-center gap-2">
                    <AlertCircle size={14} />
                    {formError ?? error}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Submit Button */}
            <motion.button
              type="submit"
              whileHover={{ scale: 1.02, boxShadow: "0 0 30px rgba(139, 245, 230, 0.4)" }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-gradient-to-r from-[#8BF5E6] to-[#4FD1C5] text-[#0f172a] font-bold py-4 rounded-xl shadow-lg transition-all font-hindi text-sm uppercase tracking-wide flex items-center justify-center gap-2 relative overflow-hidden group"
            >
              <motion.div
                className="absolute inset-0 bg-white/20"
                initial={{ x: "-100%" }}
                whileHover={{ x: "100%" }}
                transition={{ duration: 0.5 }}
              />
              <LogIn size={18} className="relative z-10" />
              <span className="relative z-10">लॉगिन करें</span>
            </motion.button>
          </motion.form>
          
          {/* Footer Hint */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="mt-6 text-center relative z-10"
          >
            <p className="text-[10px] text-slate-500 font-hindi">
              डिफ़ॉल्ट क्रेडेंशियल्स: admin / admin123
            </p>
          </motion.div>
        </div>

        {/* Floating Particles */}
        <motion.div
          animate={{
            y: [0, -20, 0],
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-10 -right-10 w-20 h-20 bg-[#8BF5E6]/10 rounded-full blur-2xl pointer-events-none"
        />
        <motion.div
          animate={{
            y: [0, 20, 0],
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
          className="absolute -bottom-10 -left-10 w-24 h-24 bg-purple-500/10 rounded-full blur-2xl pointer-events-none"
        />
      </motion.div>
    </div>
  );
};

export default Login;
