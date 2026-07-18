import { Users } from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../utils/api';

interface LandingPageProps {
  onLogin: (token: string, role: string) => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onLogin }) => {
  
  const handleLogin = async (username: string) => {
    try {
      const response = await api.post('/login', new URLSearchParams({
        username: username,
        password: username
      }));
      onLogin(response.data.access_token, response.data.role);
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed. Ensure backend is running.');
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden flex flex-col items-center justify-center p-6">
      {/* Background Particles Mock */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-1/4 left-1/4 w-1 h-1 bg-white/20 rounded-full shadow-[0_0_10px_rgba(255,255,255,0.8)] animate-pulse"></div>
        <div className="absolute top-1/3 right-1/4 w-1 h-1 bg-white/20 rounded-full shadow-[0_0_10px_rgba(255,255,255,0.8)] animate-pulse" style={{animationDelay: '1s'}}></div>
        <div className="absolute bottom-1/4 left-1/3 w-1 h-1 bg-white/20 rounded-full shadow-[0_0_10px_rgba(255,255,255,0.8)] animate-pulse" style={{animationDelay: '0.5s'}}></div>
      </div>

      <div className="z-10 w-full max-w-2xl flex flex-col items-center text-center space-y-8">
        
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h1 className="text-6xl md:text-8xl font-black tracking-tight">
            Recruiter <span className="text-primary glow-text">AI</span>
          </h1>
          <p className="text-sm md:text-base tracking-[0.3em] text-gray-400 font-medium uppercase">
            Intelligent Screening & Matching
          </p>
        </motion.div>

        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="max-w-xl text-gray-400 leading-relaxed text-sm md:text-base"
        >
          Upload job descriptions and candidate resumes. Let our specialized agents instantly parse, filter, score, and rank profiles with detailed reasoning.
        </motion.p>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="w-full mt-8 flex flex-col md:flex-row gap-6 justify-center"
        >
          {/* Admin */}
          <div className="glass-card p-6 flex flex-col items-center text-center hover:border-purple-500/50 transition-colors cursor-pointer flex-1" onClick={() => handleLogin('admin')}>
            <Users className="w-10 h-10 text-purple-500 mb-4" />
            <h3 className="text-xl font-bold mb-2">Admin</h3>
            <p className="text-gray-400 text-xs mb-4">Full Access & Analytics</p>
            <button className="w-full py-2 bg-purple-500/20 text-purple-400 font-medium hover:bg-purple-500 hover:text-white transition-all rounded-lg text-sm">
              Login as Admin
            </button>
          </div>

          {/* Recruiter */}
          <div className="glass-card p-6 flex flex-col items-center text-center hover:border-blue-500/50 transition-colors cursor-pointer flex-1" onClick={() => handleLogin('recruiter')}>
            <Users className="w-10 h-10 text-blue-500 mb-4" />
            <h3 className="text-xl font-bold mb-2">Recruiter</h3>
            <p className="text-gray-400 text-xs mb-4">Manage & Analyze</p>
            <button className="w-full py-2 bg-blue-500/20 text-blue-400 font-medium hover:bg-blue-500 hover:text-white transition-all rounded-lg text-sm">
              Login as Recruiter
            </button>
          </div>

          {/* Hiring Manager */}
          <div className="glass-card p-6 flex flex-col items-center text-center hover:border-green-500/50 transition-colors cursor-pointer flex-1" onClick={() => handleLogin('hiring_manager')}>
            <Users className="w-10 h-10 text-green-500 mb-4" />
            <h3 className="text-xl font-bold mb-2">Hiring Manager</h3>
            <p className="text-gray-400 text-xs mb-4">View Candidates</p>
            <button className="w-full py-2 bg-green-500/20 text-green-400 font-medium hover:bg-green-500 hover:text-white transition-all rounded-lg text-sm">
              Login as Manager
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default LandingPage;
