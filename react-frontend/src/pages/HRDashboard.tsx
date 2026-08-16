import { useState, useEffect } from 'react';
import { LogOut, Users, Play, FileText, CheckCircle, UploadCloud, ChevronDown, ChevronUp, Trash2, Edit2, X, MessageSquare, Send, Shield, UserPlus } from 'lucide-react';
import api from '../utils/api';

interface Props {
  onLogout: () => void;
  role: string;
  token: string;
}

const parseJson = (str: any) => {
  if (!str) return [];
  if (typeof str === 'string') {
    try {
      return JSON.parse(str);
    } catch (e) {
      return [];
    }
  }
  return str;
};

const getRecAndReason = (recString: string) => {
  if (!recString) return { rec: "", reason: "" };
  // Split on first colon and capture the rest
  const parts = recString.split(/:\s*(.+)/s);
  if (parts.length > 1) {
    return { rec: parts[0], reason: parts[1] };
  }
  return { rec: recString, reason: "N/A" };
};

const HRDashboard: React.FC<Props> = ({ onLogout, role }) => {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [jdText, setJdText] = useState("");
  const [analyzingId, setAnalyzingId] = useState<number | null>(null);
  const [workflowRunningId, setWorkflowRunningId] = useState<number | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [modalStep, setModalStep] = useState(0);
  const [activeTab, setActiveTab] = useState<'candidates' | 'matching' | 'analytics' | 'sourcing' | 'lifecycle'>('candidates');
  const [candidateJourneys, setCandidateJourneys] = useState<Record<number, any[]>>({});
  const [diversityData, setDiversityData] = useState<any>(null);
  const [isDiversityLoading, setIsDiversityLoading] = useState(false);

  // Candidate Sourcing State
  const [sourcedCandidates, setSourcedCandidates] = useState<any[]>([]);
  const [sourcingFilter, setSourcingFilter] = useState({ platform: '', skills: '', location: '', stage: '', search: '' });
  const [showAddSourcedModal, setShowAddSourcedModal] = useState(false);
  const [newSourced, setNewSourced] = useState({
    name: '', email: '', phone: '', current_company: '', preferred_location: '',
    skills: '', experience: '', education: '', source_platform: 'LinkedIn',
    source_url: '', github_username: '', initial_notes: ''
  });
  const [rankJdText, setRankJdText] = useState('');
  const [rankingId, setRankingId] = useState<number | null>(null);

  // Lifecycle State
  const [jobs, setJobs] = useState<any[]>([]);
  const [interviews, setInterviews] = useState<any[]>([]);
  const [offers, setOffers] = useState<any[]>([]);
  const [onboardings, setOnboardings] = useState<any[]>([]);
  const [activityLogs, setActivityLogs] = useState<any[]>([]);
  const [showCreateJobModal, setShowCreateJobModal] = useState(false);
  const [newJob, setNewJob] = useState({ title: '', department: '', location: '', description: '', requirements: '' });
  const [showScheduleInterviewModal, setShowScheduleInterviewModal] = useState(false);
  const [newInterview, setNewInterview] = useState({ candidate_id: 0, interviewer: '', scheduled_at: '', interview_type: 'Technical', meeting_link: '' });
  const [showCreateOfferModal, setShowCreateOfferModal] = useState(false);
  const [newOffer, setNewOffer] = useState({ candidate_id: 0, salary: 120000, currency: 'USD', status: 'Sent' });

  const fetchJourney = async (id: number) => {
    try {
      const res = await api.get(`/candidates/${id}/journey`);
      setCandidateJourneys(prev => ({...prev, [id]: res.data}));
    } catch (e) {
      console.error("Failed to fetch journey", e);
    }
  };

  const handleLogJourneyEvent = async (candidateId: number, stage: string, remarks: string) => {
    try {
      await api.post(`/candidates/${candidateId}/journey`, {
        stage,
        status: "Completed",
        remarks
      });
      fetchJourney(candidateId);
      fetchCandidates();
    } catch (e) {
      alert("Failed to log stage transition");
    }
  };

  const fetchDiversityAnalytics = async () => {
    setIsDiversityLoading(true);
    try {
      const res = await api.get('/analytics/diversity');
      setDiversityData(res.data);
    } catch (e) {
      console.error("Failed to fetch diversity analytics", e);
    } finally {
      setIsDiversityLoading(false);
    }
  };

  const fetchSourcedCandidates = async () => {
    try {
      const params = new URLSearchParams();
      if (sourcingFilter.platform) params.append('source_platform', sourcingFilter.platform);
      if (sourcingFilter.skills) params.append('skills', sourcingFilter.skills);
      if (sourcingFilter.location) params.append('location', sourcingFilter.location);
      if (sourcingFilter.stage) params.append('stage', sourcingFilter.stage);
      if (sourcingFilter.search) params.append('search', sourcingFilter.search);
      const res = await api.get(`/sourcing/candidates?${params.toString()}`);
      setSourcedCandidates(res.data);
    } catch (e) {
      console.error("Failed to fetch sourced candidates", e);
    }
  };

  const fetchLifecycleData = async () => {
    try {
      const [jobsRes, intRes, offerRes, onboardRes, logsRes] = await Promise.all([
        api.get('/jobs'),
        api.get('/interviews'),
        api.get('/offers'),
        api.get('/onboarding'),
        api.get('/activity-logs')
      ]);
      setJobs(jobsRes.data);
      setInterviews(intRes.data);
      setOffers(offerRes.data);
      setOnboardings(onboardRes.data);
      setActivityLogs(logsRes.data);
    } catch (e) {
      console.error("Failed to fetch lifecycle data", e);
    }
  };

  useEffect(() => {
    if (activeTab === 'analytics') {
      fetchDiversityAnalytics();
    } else if (activeTab === 'sourcing') {
      fetchSourcedCandidates();
    } else if (activeTab === 'lifecycle') {
      fetchLifecycleData();
    }
  }, [activeTab, sourcingFilter]);

  const handleAddSourced = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = {
        name: newSourced.name,
        email: newSourced.email || undefined,
        phone: newSourced.phone || undefined,
        current_company: newSourced.current_company || undefined,
        preferred_location: newSourced.preferred_location || undefined,
        skills: newSourced.skills || undefined,
        experience: newSourced.experience || undefined,
        education: newSourced.education || undefined,
        source_platform: newSourced.source_platform,
        source_url: newSourced.source_url || undefined,
        initial_notes: newSourced.initial_notes || undefined,
      };

      if (newSourced.github_username) {
        payload.social_profiles = [{
          platform: 'GitHub',
          profile_url: `https://github.com/${newSourced.github_username}`,
          username: newSourced.github_username
        }];
      }

      await api.post('/sourcing/candidates', payload);
      setShowAddSourcedModal(false);
      setNewSourced({
        name: '', email: '', phone: '', current_company: '', preferred_location: '',
        skills: '', experience: '', education: '', source_platform: 'LinkedIn',
        source_url: '', github_username: '', initial_notes: ''
      });
      fetchSourcedCandidates();
    } catch (e) {
      alert("Failed to add sourced candidate");
    }
  };

  const handlePipelineMove = async (candidateId: number, stage: string) => {
    try {
      await api.put(`/sourcing/candidates/${candidateId}/pipeline`, { stage });
      fetchSourcedCandidates();
    } catch (e) {
      alert("Failed to move pipeline stage");
    }
  };

  const handleRankSourced = async (candidateId: number) => {
    if (!rankJdText.trim()) {
      alert("Please enter a Job Description in the ranking input field first.");
      return;
    }
    setRankingId(candidateId);
    try {
      await api.post(`/sourcing/candidates/${candidateId}/rank`, { job_description: rankJdText });
      fetchSourcedCandidates();
      alert("Candidate AI Rank updated!");
    } catch (e) {
      alert("Failed to rank candidate");
    } finally {
      setRankingId(null);
    }
  };

  const handleCreateJobSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/jobs', newJob);
      setShowCreateJobModal(false);
      setNewJob({ title: '', department: '', location: '', description: '', requirements: '' });
      fetchLifecycleData();
    } catch (e) {
      alert("Failed to create job");
    }
  };

  const handleScheduleInterviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/interviews', newInterview);
      setShowScheduleInterviewModal(false);
      fetchLifecycleData();
    } catch (e) {
      alert("Failed to schedule interview");
    }
  };

  const handleCreateOfferSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/offers', newOffer);
      setShowCreateOfferModal(false);
      fetchLifecycleData();
    } catch (e) {
      alert("Failed to create offer");
    }
  };
  const [selectedCandidateId, setSelectedCandidateId] = useState<number | null>(null);
  const [matchingJd, setMatchingJd] = useState("");
  const [matchingResult, setMatchingResult] = useState<any | null>(null);
  const [isMatchingLoading, setIsMatchingLoading] = useState(false);
  const [matchingError, setMatchingError] = useState<string | null>(null);

  // Admin Panel States
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [adminTab, setAdminTab] = useState<'analytics'|'users'|'logs'>('analytics');
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [adminUsers, setAdminUsers] = useState<any[]>([]);
  const [adminLogs, setAdminLogs] = useState<string[]>([]);
  const [newUser, setNewUser] = useState({username: '', password: '', role: 'recruiter'});

  // Comments State
  const [candidateComments, setCandidateComments] = useState<Record<number, any[]>>({});
  const [newCommentText, setNewCommentText] = useState("");

  // Chat Widget State
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<{role: string, content: string}[]>([{
    role: "ai", content: "Hi! I'm your AI Recruiter Assistant. Ask me anything about our candidates."
  }]);
  const [chatInput, setChatInput] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);

  // Filter States
  const [searchFilter, setSearchFilter] = useState("");
  const [scoreFilter, setScoreFilter] = useState<number | "">("");
  const [skillsFilter, setSkillsFilter] = useState("");
  const [noticeFilter, setNoticeFilter] = useState("");
  const [recFilter, setRecFilter] = useState("");
  const [sortBy, setSortBy] = useState("");

  const fetchAnalytics = async () => {
    try {
      const res = await api.get('/analytics');
      setAnalyticsData(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchAdminUsers = async () => {
    try {
      const res = await api.get('/admin/users');
      setAdminUsers(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchAdminLogs = async () => {
    try {
      const res = await api.get('/admin/logs?lines=100');
      setAdminLogs(res.data.logs);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/admin/users', newUser);
      setNewUser({username: '', password: '', role: 'recruiter'});
      fetchAdminUsers();
    } catch (e) {
      alert("Failed to create user");
    }
  };

  const handleDeleteUser = async (id: number) => {
    if(!window.confirm("Delete this user?")) return;
    try {
      await api.delete(`/admin/users/${id}`);
      fetchAdminUsers();
    } catch(e) {
      alert("Failed to delete user");
    }
  };

  useEffect(() => {
    if (showAdminPanel) {
      if (adminTab === 'analytics') fetchAnalytics();
      if (adminTab === 'users') fetchAdminUsers();
      if (adminTab === 'logs') fetchAdminLogs();
    }
  }, [showAdminPanel, adminTab]);

  // Resume upload state
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  // Expand state for detailed logs
  const [expandedId, setExpandedId] = useState<number | null>(null);
  
  // Edit candidate state
  const [editCandidate, setEditCandidate] = useState<any>(null);

  useEffect(() => {
    fetchCandidates();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchFilter, scoreFilter, skillsFilter, noticeFilter, recFilter, sortBy]);

  // Polling logic when analyzingId is set
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (analyzingId !== null) {
      interval = setInterval(async () => {
        try {
          const response = await api.get(`/candidates/${analyzingId}`);
          if (response.data.match_score !== null) {
            // Analysis complete
            setAnalyzingId(null);
            setShowModal(false);
            setModalStep(0);
            fetchCandidates();
            setExpandedId(analyzingId); // Auto-expand the newly analyzed candidate
          }
        } catch (error) {
          console.error("Polling error", error);
        }
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [analyzingId]);

  // Fake step progression for UI visual
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (showModal && modalStep < 4) {
      interval = setInterval(() => {
        setModalStep((prev) => prev + 1);
      }, 2500); // Progress fake steps every 2.5s
    }
    return () => clearInterval(interval);
  }, [showModal, modalStep]);

  const fetchCandidates = async () => {
    try {
      const params = new URLSearchParams();
      if (searchFilter) params.append('search', searchFilter);
      if (scoreFilter) params.append('min_score', scoreFilter.toString());
      if (skillsFilter) params.append('skills', skillsFilter);
      if (noticeFilter) params.append('notice_period', noticeFilter);
      if (recFilter) params.append('recommendation_filter', recFilter);
      if (sortBy) params.append('sort_by', sortBy);
      
      const response = await api.get(`/candidates?${params.toString()}`);
      setCandidates(response.data);
    } catch (error) {
      console.error("Failed to fetch candidates", error);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setFile(null);
      fetchCandidates();
    } catch (error) {
      console.error("Upload failed", error);
      alert("Failed to upload resume.");
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async (candidateId: number) => {
    if (!jdText.trim()) {
      alert("Please enter a Job Description first.");
      return;
    }
    setAnalyzingId(candidateId);
    setShowModal(true);
    setModalStep(0);
    try {
      await api.post('/analyze', {
        candidate_id: candidateId,
        job_description: jdText
      });
    } catch (error) {
      console.error("Failed to start analysis", error);
      alert("Analysis failed.");
      setAnalyzingId(null);
      setShowModal(false);
    }
  };

  const handleRunWorkflow = async (candidateId: number) => {
    if (!jdText.trim()) {
      alert("Please enter a Job Description first.");
      return;
    }
    setWorkflowRunningId(candidateId);
    try {
      await api.post('/recruitment/workflow', {
        candidate_id: candidateId,
        job_description: jdText
      });
      fetchCandidates();
      alert("Workflow execution complete!");
    } catch (error: any) {
      console.error("Failed to run workflow", error);
      alert(error.response?.data?.detail || "Workflow execution failed.");
    } finally {
      setWorkflowRunningId(null);
    }
  };

  const handleJobMatch = async () => {
    if (!selectedCandidateId) {
      alert("Please select a candidate first.");
      return;
    }
    if (!matchingJd.trim()) {
      alert("Please enter a Job Description.");
      return;
    }
    setIsMatchingLoading(true);
    setMatchingError(null);
    setMatchingResult(null);
    try {
      const res = await api.post('/job/match', {
        candidate_id: selectedCandidateId,
        job_description: matchingJd
      });
      setMatchingResult(res.data);
    } catch (err: any) {
      console.error("Job matching failed", err);
      setMatchingError(err.response?.data?.detail || "An error occurred during job matching.");
    } finally {
      setIsMatchingLoading(false);
    }
  };

  const toggleExpand = async (id: number) => {
    const isExpanding = expandedId !== id;
    setExpandedId(isExpanding ? id : null);
    
    if (isExpanding) {
      if (!candidateComments[id]) {
        try {
          const res = await api.get(`/candidates/${id}/comments`);
          setCandidateComments(prev => ({...prev, [id]: res.data}));
        } catch (e) {
          console.error("Failed to fetch comments", e);
        }
      }
      fetchJourney(id);
    }
  };

  const handleAddComment = async (id: number) => {
    if (!newCommentText.trim()) return;
    try {
      await api.post(`/candidates/${id}/comments`, { text: newCommentText });
      setNewCommentText("");
      const res = await api.get(`/candidates/${id}/comments`);
      setCandidateComments(prev => ({...prev, [id]: res.data}));
    } catch (e) {
      alert("Failed to add comment");
    }
  };

  const handleApprove = async (id: number) => {
    if (!window.confirm("Approve this candidate? This will update their status to Hired.")) return;
    try {
      await api.post(`/candidates/${id}/approve`);
      fetchCandidates();
    } catch (e) {
      alert("Failed to approve candidate");
    }
  };

  const handleSaveCandidate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editCandidate) return;
    try {
      await api.put(`/candidates/${editCandidate.id}`, {
        name: editCandidate.name,
        current_company: editCandidate.current_company,
        current_ctc: editCandidate.current_ctc,
        expected_ctc: editCandidate.expected_ctc,
        notice_period: editCandidate.notice_period,
        preferred_location: editCandidate.preferred_location,
        employment_type: editCandidate.employment_type,
        immediate_joiner: editCandidate.immediate_joiner
      });
      setEditCandidate(null);
      fetchCandidates();
    } catch (error) {
      console.error("Failed to update candidate", error);
      alert("Failed to update candidate details.");
    }
  };

  const handleDeleteCandidate = async (id: number) => {
    if (window.confirm("Are you sure you want to delete this candidate? This action cannot be undone.")) {
      try {
        await api.delete(`/candidates/${id}`);
        fetchCandidates();
      } catch (error) {
        console.error("Failed to delete candidate", error);
        alert("Failed to delete candidate.");
      }
    }
  };

  const handleStatusChange = async (id: number, newStatus: string) => {
    try {
      await api.put(`/candidates/${id}`, { status: newStatus });
      fetchCandidates();
      fetchJourney(id);
    } catch (err) {
      console.error("Failed to update status", err);
      alert("Failed to update status");
    }
  };

  const handleIntegration = async (id: number, integration: string) => {
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'https://recruiter-ai-production-9983.up.railway.app';
      const response = await fetch(`${API_URL}/api/v1/integrations/${integration}/${id}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        alert(`${integration.split('/')[0].toUpperCase()} integration triggered successfully!`);
        fetchCandidates();
      } else {
        alert(`Failed to trigger ${integration}`);
      }
    } catch (err) {
      console.error(err);
      alert(`Error triggering ${integration}`);
    }
  };

  const handleNaukriImport = async () => {
    const url = window.prompt("Enter Naukri Profile URL:");
    if (!url) return;
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'https://recruiter-ai-production-9983.up.railway.app';
      const response = await fetch(`${API_URL}/api/v1/integrations/naukri/import`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ profile_url: url })
      });
      if (response.ok) {
        alert("Candidate imported from Naukri successfully!");
        fetchCandidates();
      } else {
        alert("Failed to import candidate");
      }
    } catch (err) {
      console.error(err);
      alert("Error importing candidate");
    }
  };

  const handleChatSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = chatInput;
    setChatMessages(prev => [...prev, {role: "user", content: userMsg}]);
    setChatInput("");
    setIsChatLoading(true);

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'https://recruiter-ai-production-9983.up.railway.app';
      const response = await fetch(`${API_URL}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userMsg, candidate_id: null })
      });

      if (response.ok) {
        const data = await response.json();
        setChatMessages(prev => [...prev, {role: "ai", content: data.reply}]);
      } else {
        setChatMessages(prev => [...prev, {role: "ai", content: "Sorry, I encountered an error. Please try again."}]);
      }
    } catch (err) {
      console.error(err);
      setChatMessages(prev => [...prev, {role: "ai", content: "Network error. Please try again."}]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const analysisSteps = [
    "Initializing Supervisor Agent...",
    "Running Resume, JD, and DB Agents (Parallel)...",
    "Evaluating Match (Evaluation Agent)...",
    "Generating Recommendation (Recommendation Agent)...",
    "Returning Recruiter Response & Saving..."
  ];

  return (
    <div className="min-h-screen p-8 text-white relative">
      {/* Edit Candidate Modal */}
      {editCandidate && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm overflow-y-auto py-8">
          <div className="bg-gray-900 border border-white/10 p-8 rounded-2xl max-w-2xl w-full shadow-2xl relative my-auto">
            <button 
              onClick={() => setEditCandidate(null)}
              className="absolute top-6 right-6 text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
            <h3 className="text-2xl font-bold mb-6">Edit Candidate Details</h3>
            
            <form onSubmit={handleSaveCandidate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Name</label>
                  <input type="text" required value={editCandidate.name || ""} onChange={(e) => setEditCandidate({...editCandidate, name: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm focus:outline-none focus:border-blue-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Current Company</label>
                  <input type="text" value={editCandidate.current_company || ""} onChange={(e) => setEditCandidate({...editCandidate, current_company: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm focus:outline-none focus:border-blue-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Current CTC</label>
                  <input type="text" value={editCandidate.current_ctc || ""} onChange={(e) => setEditCandidate({...editCandidate, current_ctc: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm focus:outline-none focus:border-blue-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Expected CTC</label>
                  <input type="text" value={editCandidate.expected_ctc || ""} onChange={(e) => setEditCandidate({...editCandidate, expected_ctc: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm focus:outline-none focus:border-blue-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Notice Period</label>
                  <input type="text" value={editCandidate.notice_period || ""} onChange={(e) => setEditCandidate({...editCandidate, notice_period: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm focus:outline-none focus:border-blue-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Preferred Location</label>
                  <input type="text" value={editCandidate.preferred_location || ""} onChange={(e) => setEditCandidate({...editCandidate, preferred_location: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm focus:outline-none focus:border-blue-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Employment Type</label>
                  <select value={editCandidate.employment_type || ""} onChange={(e) => setEditCandidate({...editCandidate, employment_type: e.target.value})} className="w-full bg-gray-800 border border-white/10 rounded p-2 text-sm focus:outline-none focus:border-blue-500">
                    <option value="">Select Type</option>
                    <option value="Full-time">Full-time</option>
                    <option value="Contract">Contract</option>
                    <option value="Internship">Internship</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Immediate Joiner</label>
                  <select value={editCandidate.immediate_joiner || ""} onChange={(e) => setEditCandidate({...editCandidate, immediate_joiner: e.target.value})} className="w-full bg-gray-800 border border-white/10 rounded p-2 text-sm focus:outline-none focus:border-blue-500">
                    <option value="">Select Option</option>
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                  </select>
                </div>
              </div>
              <div className="mt-8 flex justify-end gap-4 border-t border-white/10 pt-4">
                <button type="button" onClick={() => setEditCandidate(null)} className="px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-sm transition-colors">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg text-sm transition-colors text-white font-medium">Save Details</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Analysis Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-gray-900 border border-white/10 p-8 rounded-2xl max-w-md w-full shadow-2xl">
            <h3 className="text-2xl font-bold mb-2 flex items-center">
              <Play className="w-5 h-5 mr-2 text-blue-500 animate-pulse" />
              Analyzing Candidate...
            </h3>
            <p className="text-gray-400 text-sm mb-6">
              Our LangGraph AI is currently evaluating the candidate against your Job Description.
            </p>
            
            <div className="space-y-4">
              {analysisSteps.map((step, index) => {
                const isActive = index === modalStep;
                const isCompleted = index < modalStep;
                
                return (
                  <div key={index} className="flex items-center">
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center mr-3 border ${
                      isCompleted ? 'bg-green-500 border-green-500 text-black' :
                      isActive ? 'border-blue-500 bg-transparent' :
                      'border-gray-600 bg-transparent'
                    }`}>
                      {isCompleted && <CheckCircle className="w-3 h-3" />}
                      {isActive && <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping" />}
                    </div>
                    <span className={`text-sm ${
                      isCompleted ? 'text-gray-300' :
                      isActive ? 'text-white font-medium' :
                      'text-gray-600'
                    }`}>
                      {step}
                    </span>
                  </div>
                );
              })}
            </div>
            
            <div className="mt-8 pt-4 border-t border-white/10 flex justify-end">
              <button 
                onClick={() => { setShowModal(false); }}
                className="px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-sm transition-colors"
              >
                Hide (Run in Background)
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Admin Panel Modal */}
      {showAdminPanel && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-gray-900 border border-white/10 p-6 rounded-2xl max-w-4xl w-full h-[80vh] shadow-2xl relative flex flex-col">
            <button 
              onClick={() => setShowAdminPanel(false)}
              className="absolute top-6 right-6 text-gray-400 hover:text-white transition-colors z-10"
            >
              <X className="w-6 h-6" />
            </button>
            <h3 className="text-2xl font-bold mb-6 flex items-center text-purple-400">
              <Shield className="w-6 h-6 mr-3" /> Admin Dashboard
            </h3>

            <div className="flex border-b border-white/10 mb-6 space-x-4">
              <button onClick={() => setAdminTab('analytics')} className={`pb-2 px-2 text-sm font-medium ${adminTab === 'analytics' ? 'text-purple-400 border-b-2 border-purple-400' : 'text-gray-400 hover:text-white'}`}>Analytics</button>
              <button onClick={() => setAdminTab('users')} className={`pb-2 px-2 text-sm font-medium ${adminTab === 'users' ? 'text-purple-400 border-b-2 border-purple-400' : 'text-gray-400 hover:text-white'}`}>User Management</button>
              <button onClick={() => setAdminTab('logs')} className={`pb-2 px-2 text-sm font-medium ${adminTab === 'logs' ? 'text-purple-400 border-b-2 border-purple-400' : 'text-gray-400 hover:text-white'}`}>System Logs</button>
            </div>
            
            <div className="flex-1 overflow-y-auto">
              {adminTab === 'analytics' && analyticsData && (
                <div className="space-y-6">
                  {/* General System Metrics */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">System & Parse Performance</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                        <p className="text-gray-400 text-xs uppercase mb-1">Avg Parse Time</p>
                        <p className="text-xl font-bold">{analyticsData.average_resume_parsing_time_s.toFixed(2)}s</p>
                      </div>
                      <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                        <p className="text-gray-400 text-xs uppercase mb-1">Avg AI Response</p>
                        <p className="text-xl font-bold">{analyticsData.ai_response_time_s.toFixed(2)}s</p>
                      </div>
                      <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                        <p className="text-gray-400 text-xs uppercase mb-1">Avg API Latency</p>
                        <p className="text-xl font-bold">{analyticsData.api_latency_s.toFixed(2)}s</p>
                      </div>
                      <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                        <p className="text-gray-400 text-xs uppercase mb-1">Cache Hit Rate</p>
                        <p className="text-xl font-bold">{analyticsData.cache_hit_rate_pct}%</p>
                      </div>
                      <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                        <p className="text-gray-400 text-xs uppercase mb-1">Analyses Completed</p>
                        <p className="text-xl font-bold text-green-400">{analyticsData.analyses_completed}</p>
                      </div>
                      <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                        <p className="text-gray-400 text-xs uppercase mb-1">Failed Analyses</p>
                        <p className="text-xl font-bold text-red-400">{analyticsData.failed_analyses}</p>
                      </div>
                    </div>
                  </div>

                  {/* Job Matching Statistics */}
                  {analyticsData.job_matching_stats && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Job Matching Statistics</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                          <p className="text-gray-400 text-xs uppercase mb-1">Total Matches Run</p>
                          <p className="text-xl font-bold text-blue-400">{analyticsData.job_matching_stats.total_matches}</p>
                        </div>
                        <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                          <p className="text-gray-400 text-xs uppercase mb-1">Avg Match Score</p>
                          <p className="text-xl font-bold text-purple-400">{analyticsData.job_matching_stats.average_score}%</p>
                        </div>
                        <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                          <p className="text-gray-400 text-xs uppercase mb-1">Highest Match Score</p>
                          <p className="text-xl font-bold text-green-400">{analyticsData.job_matching_stats.highest_score}%</p>
                        </div>
                        <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                          <p className="text-gray-400 text-xs uppercase mb-1">Lowest Match Score</p>
                          <p className="text-xl font-bold text-yellow-500">{analyticsData.job_matching_stats.lowest_score}%</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Job Matching Skill Analysis */}
                  {analyticsData.job_matching_analysis && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Matching Skill Gap Analysis</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Top Matched Skills */}
                        <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                          <p className="text-gray-300 text-xs font-semibold uppercase tracking-wider mb-3 text-green-400">Top Matched Skills (Requested & Found)</p>
                          {analyticsData.job_matching_analysis.top_matched_skills && analyticsData.job_matching_analysis.top_matched_skills.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                              {analyticsData.job_matching_analysis.top_matched_skills.map((item: any, idx: number) => (
                                <span key={idx} className="flex items-center gap-1.5 bg-green-500/10 border border-green-500/20 text-green-300 px-2.5 py-1 rounded-full text-xs font-medium">
                                  {item.skill}
                                  <span className="bg-green-500/20 text-green-400 px-1.5 py-0.5 rounded text-[10px] font-bold">
                                    {item.count}
                                  </span>
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-gray-500 text-xs italic">No matching skills tracked yet.</p>
                          )}
                        </div>

                        {/* Top Missing Skills */}
                        <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                          <p className="text-gray-300 text-xs font-semibold uppercase tracking-wider mb-3 text-red-400">Top Missing Skills (Requested but Lacking)</p>
                          {analyticsData.job_matching_analysis.top_missing_skills && analyticsData.job_matching_analysis.top_missing_skills.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                              {analyticsData.job_matching_analysis.top_missing_skills.map((item: any, idx: number) => (
                                <span key={idx} className="flex items-center gap-1.5 bg-red-500/10 border border-red-500/20 text-red-300 px-2.5 py-1 rounded-full text-xs font-medium">
                                  {item.skill}
                                  <span className="bg-red-500/20 text-red-400 px-1.5 py-0.5 rounded text-[10px] font-bold">
                                    {item.count}
                                  </span>
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-gray-500 text-xs italic">No missing skills tracked yet.</p>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {adminTab === 'users' && (
                <div className="space-y-6">
                  <form onSubmit={handleCreateUser} className="bg-black/40 p-4 rounded-lg border border-white/5 flex flex-wrap gap-4 items-end">
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">Username</label>
                      <input type="text" required value={newUser.username} onChange={(e) => setNewUser({...newUser, username: e.target.value})} className="bg-gray-800 border border-white/10 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-purple-500" />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">Password</label>
                      <input type="password" required value={newUser.password} onChange={(e) => setNewUser({...newUser, password: e.target.value})} className="bg-gray-800 border border-white/10 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-purple-500" />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">Role</label>
                      <select value={newUser.role} onChange={(e) => setNewUser({...newUser, role: e.target.value})} className="bg-gray-800 border border-white/10 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-purple-500">
                        <option value="recruiter">Recruiter</option>
                        <option value="hiring_manager">Hiring Manager</option>
                        <option value="admin">Admin</option>
                      </select>
                    </div>
                    <button type="submit" className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-1.5 rounded text-sm font-medium transition-colors flex items-center">
                      <UserPlus className="w-4 h-4 mr-2" /> Add User
                    </button>
                  </form>
                  
                  <div className="bg-black/40 rounded-lg border border-white/5 overflow-hidden">
                    <table className="w-full text-left text-sm">
                      <thead className="bg-white/5">
                        <tr>
                          <th className="px-4 py-3 text-gray-400 font-medium">ID</th>
                          <th className="px-4 py-3 text-gray-400 font-medium">Username</th>
                          <th className="px-4 py-3 text-gray-400 font-medium">Role</th>
                          <th className="px-4 py-3 text-gray-400 font-medium text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {adminUsers.map((user) => (
                          <tr key={user.id} className="border-t border-white/5 hover:bg-white/5">
                            <td className="px-4 py-3 text-gray-300">{user.id}</td>
                            <td className="px-4 py-3 text-gray-300">{user.username}</td>
                            <td className="px-4 py-3 text-gray-300 capitalize">{user.role.replace('_', ' ')}</td>
                            <td className="px-4 py-3 text-right">
                              <button onClick={() => handleDeleteUser(user.id)} disabled={user.username === 'admin'} className="text-red-400 hover:text-red-300 disabled:text-gray-600 transition-colors">
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {adminTab === 'logs' && (
                <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-xs overflow-y-auto h-full max-h-[50vh] border border-white/5 whitespace-pre-wrap">
                  {adminLogs.length > 0 ? adminLogs.join('') : "Loading logs..."}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">HR Master Dashboard</h1>
        <div className="flex items-center space-x-6">
          {role === 'admin' && (
            <button onClick={() => setShowAdminPanel(true)} className="flex items-center text-purple-400 hover:text-purple-300 transition-colors bg-purple-500/10 px-3 py-1.5 rounded-lg border border-purple-500/20">
              <Shield className="w-4 h-4 mr-2" /> Admin Panel
            </button>
          )}
          <button onClick={onLogout} className="flex items-center text-red-400 hover:text-red-300 transition-colors">
            <LogOut className="w-4 h-4 mr-2" /> Logout
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-white/10 mb-8 space-x-6 overflow-x-auto">
        <button 
          onClick={() => setActiveTab('candidates')} 
          className={`pb-4 px-2 text-lg font-medium transition-colors relative ${activeTab === 'candidates' ? 'text-blue-400 font-bold border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'}`}
        >
          Candidates
        </button>
        <button 
          onClick={() => setActiveTab('matching')} 
          className={`pb-4 px-2 text-lg font-medium transition-colors relative ${activeTab === 'matching' ? 'text-blue-400 font-bold border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'}`}
        >
          Job Matching
        </button>
        <button 
          onClick={() => setActiveTab('analytics')} 
          className={`pb-4 px-2 text-lg font-medium transition-colors relative ${activeTab === 'analytics' ? 'text-blue-400 font-bold border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'}`}
        >
          D&I Analytics
        </button>
        <button 
          onClick={() => setActiveTab('sourcing')} 
          className={`pb-4 px-2 text-lg font-medium transition-colors relative ${activeTab === 'sourcing' ? 'text-blue-400 font-bold border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'}`}
        >
          Candidate Sourcing
        </button>
        <button 
          onClick={() => setActiveTab('lifecycle')} 
          className={`pb-4 px-2 text-lg font-medium transition-colors relative ${activeTab === 'lifecycle' ? 'text-blue-400 font-bold border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'}`}
        >
          Recruitment Lifecycle
        </button>
      </div>

      {activeTab === 'candidates' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Uploads & JD */}
        <div className="lg:col-span-1 flex flex-col space-y-6">
          
          {/* Upload Resume Section */}
          {role !== 'hiring_manager' && (
            <div className="glass-card p-6 flex flex-col">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <UploadCloud className="mr-2 text-primary" /> Upload Resume
              </h2>
              <p className="text-gray-400 mb-4 text-sm">Add a candidate's resume to the pool for analysis.</p>
              
              <input 
                type="file" 
                accept=".pdf,.txt" 
                onChange={handleFileChange} 
                className="block w-full text-sm text-gray-400
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-primary/20 file:text-primary
                  hover:file:bg-primary/30 mb-4 cursor-pointer"
              />

              <button 
                onClick={handleUpload} 
                disabled={!file || uploading}
                className={`w-full py-2 rounded-lg font-medium transition-colors ${file ? 'bg-primary hover:bg-primary/80 text-white' : 'bg-gray-700 text-gray-400 cursor-not-allowed'}`}
              >
                {uploading ? 'Uploading...' : 'Upload Candidate'}
              </button>

              <div className="mt-4 border-t border-gray-700 pt-4">
                <button 
                  onClick={handleNaukriImport} 
                  className="w-full py-2 bg-[#1A73E8]/20 hover:bg-[#1A73E8]/40 text-[#1A73E8] rounded-lg text-sm font-medium transition-colors border border-[#1A73E8]/30"
                >
                  📥 Import from Naukri
                </button>
              </div>
            </div>
          )}

          {/* JD Section */}
          <div className="glass-card p-6 flex flex-col flex-grow">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <FileText className="mr-2 text-blue-500" /> Job Description
            </h2>
            <p className="text-gray-400 mb-4 text-sm">Paste the Job Description to automatically filter and match profiles.</p>
            <textarea
              className="w-full flex-grow bg-white/5 border border-white/10 rounded p-3 text-sm focus:outline-none focus:border-blue-500 transition-colors resize-none min-h-[300px]"
              placeholder="Enter Job Description here..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
            ></textarea>
          </div>
        </div>

        {/* Right Column: Candidates & Logs */}
        <div className="glass-card p-6 lg:col-span-2">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold flex items-center">
              <Users className="mr-2 text-blue-500" /> Candidate Pool
            </h2>
            <button onClick={fetchCandidates} className="text-sm px-3 py-1 bg-white/10 hover:bg-white/20 rounded transition-colors">
              ↻ Refresh List
            </button>
          </div>
          
          {/* Filters Section */}
          <div className="bg-black/30 p-4 rounded-lg border border-white/5 mb-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Search Candidate</label>
              <input type="text" placeholder="Name..." className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm text-white" value={searchFilter} onChange={(e) => setSearchFilter(e.target.value)} />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Filter by Score</label>
              <input type="number" placeholder="Min Score (e.g. 80)" className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm text-white" value={scoreFilter} onChange={(e) => setScoreFilter(e.target.value ? Number(e.target.value) : "")} />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Filter by Skills</label>
              <input type="text" placeholder="e.g. React, Python" className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm text-white" value={skillsFilter} onChange={(e) => setSkillsFilter(e.target.value)} />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Filter by Notice Period</label>
              <select className="w-full bg-black border border-white/10 rounded p-2 text-sm text-white" value={noticeFilter} onChange={(e) => setNoticeFilter(e.target.value)}>
                <option value="">Any</option>
                <option value="immediate">Immediate</option>
                <option value="15">15 Days</option>
                <option value="30">30 Days</option>
                <option value="60">60 Days</option>
                <option value="90">90 Days</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Recommendation</label>
              <select className="w-full bg-black border border-white/10 rounded p-2 text-sm text-white" value={recFilter} onChange={(e) => setRecFilter(e.target.value)}>
                <option value="">Any</option>
                <option value="Strong Hire">Strong Hire</option>
                <option value="Hire">Hire</option>
                <option value="Consider">Consider</option>
                <option value="Reject">Reject</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Sort By</label>
              <select className="w-full bg-black border border-white/10 rounded p-2 text-sm text-white" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="">Latest Uploaded</option>
                <option value="match_score">Match Score (High to Low)</option>
              </select>
            </div>
          </div>

          <div className="space-y-4">
            {candidates.length === 0 ? (
              <div className="py-8 text-center text-gray-400 italic">No candidates uploaded yet.</div>
            ) : (
              candidates.map((c) => (
                <div key={c.id} className="border border-white/10 rounded-lg overflow-hidden bg-black/20">
                  {/* Candidate Header */}
                  <div className="p-4 flex flex-wrap items-center justify-between gap-4 hover:bg-white/5 transition-colors">
                    <div className="flex-grow">
                      <h3 className="font-semibold text-lg flex items-center gap-2">
                        {c.name} (ID: {c.id})
                        {role !== 'hiring_manager' && (
                          <button onClick={() => setEditCandidate({...c})} className="text-gray-400 hover:text-white transition-colors" title="Edit Candidate Details">
                            <Edit2 className="w-4 h-4" />
                          </button>
                        )}
                        {c.match_score !== null && (
                          <span className="ml-1 text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded-full flex items-center">
                            <CheckCircle className="w-3 h-3 mr-1"/> Analyzed
                          </span>
                        )}
                        <select 
                          value={c.status || "New"}
                          onChange={(e) => handleStatusChange(c.id, e.target.value)}
                          disabled={role === 'hiring_manager'}
                          className={`ml-3 text-xs border rounded px-2 py-1 focus:outline-none focus:border-blue-500 ${role === 'hiring_manager' ? 'bg-gray-800 text-gray-400 border-gray-700 cursor-not-allowed' : 'bg-gray-800 text-white border-gray-600'}`}
                          title="Candidate Pipeline Status"
                        >
                          <option value="New">New</option>
                          <option value="Applied">Applied</option>
                          <option value="Resume Parsed">Resume Parsed</option>
                          <option value="AI Screening">AI Screening</option>
                          <option value="Shortlisted">Shortlisted</option>
                          <option value="Interview Scheduled">Interview Scheduled</option>
                          <option value="Interview Completed">Interview Completed</option>
                          <option value="Selected">Selected</option>
                          <option value="Offer Sent">Offer Sent</option>
                          <option value="Hired">Hired</option>
                          <option value="Rejected">Rejected</option>
                        </select>
                      </h3>
                      <p className="text-sm text-gray-400">File: {c.resume_path.split('/').pop() || c.resume_path.split('\\').pop()}</p>
                    </div>

                    <div className="flex items-center gap-4">
                      {c.match_score !== null && (
                        <div className="text-right">
                          <div className="text-xl font-black text-blue-400">{c.match_score}%</div>
                        </div>
                      )}
                      
                      {role !== 'hiring_manager' && (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleAnalyze(c.id)}
                            disabled={analyzingId === c.id || !jdText.trim()}
                            className={`flex items-center px-4 py-2 rounded text-sm font-medium transition-colors ${!jdText.trim() ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30'}`}
                            title={!jdText.trim() ? "Add a JD to analyze" : "Run Analysis"}
                          >
                            <Play className="w-4 h-4 mr-1" />
                            {analyzingId === c.id ? 'Running...' : 'Analyze'}
                          </button>
                          
                          <button
                            onClick={() => handleRunWorkflow(c.id)}
                            disabled={workflowRunningId === c.id || !jdText.trim()}
                            className={`flex items-center px-4 py-2 rounded text-sm font-medium transition-colors ${!jdText.trim() ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-purple-500/20 text-purple-400 hover:bg-purple-500/30'}`}
                            title={!jdText.trim() ? "Add a JD to run workflow" : "Run LangGraph Workflow"}
                          >
                            <Play className="w-4 h-4 mr-1" />
                            {workflowRunningId === c.id ? 'Running...' : 'Run Workflow'}
                          </button>
                        </div>
                      )}

                      {role === 'hiring_manager' && (
                        <button
                          onClick={() => handleApprove(c.id)}
                          className="flex items-center px-4 py-2 rounded text-sm font-medium transition-colors bg-green-500/20 text-green-400 hover:bg-green-500/30"
                          title="Approve Candidate"
                        >
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Approve
                        </button>
                      )}

                      {role === 'admin' && (
                        <button
                          onClick={() => handleDeleteCandidate(c.id)}
                          className="p-2 text-red-500 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                          title="Delete Candidate"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      )}

                      <button 
                        onClick={() => toggleExpand(c.id)}
                        className="p-2 text-gray-400 hover:text-white transition-colors"
                      >
                        {expandedId === c.id ? <ChevronUp className="w-5 h-5"/> : <ChevronDown className="w-5 h-5"/>}
                      </button>
                    </div>
                  </div>

                  {/* Expanded Detailed Logs */}
                  {expandedId === c.id && (
                    <div className="p-6 border-t border-white/10 bg-black/40">
                      
                      {/* Recruitment Details Section */}
                      <div className="mb-6 pb-6 border-b border-white/10">
                        <div className="flex justify-between items-center mb-4">
                          <h4 className="text-sm uppercase font-bold text-gray-400 tracking-wider">Recruitment Details</h4>
                          {role !== 'hiring_manager' && (
                            <button onClick={() => setEditCandidate({...c})} className="text-xs px-2 py-1 bg-white/5 hover:bg-white/10 rounded transition-colors flex items-center">
                              <Edit2 className="w-3 h-3 mr-1"/> Edit
                            </button>
                          )}
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <div className="text-gray-500 text-xs">Current Company</div>
                            <div className="text-gray-200">{c.current_company || '-'}</div>
                          </div>
                          <div>
                            <div className="text-gray-500 text-xs">Current CTC</div>
                            <div className="text-gray-200">{c.current_ctc || '-'}</div>
                          </div>
                          <div>
                            <div className="text-gray-500 text-xs">Expected CTC</div>
                            <div className="text-gray-200">{c.expected_ctc || '-'}</div>
                          </div>
                          <div>
                            <div className="text-gray-500 text-xs">Notice Period</div>
                            <div className="text-gray-200">{c.notice_period || '-'}</div>
                          </div>
                          <div>
                            <div className="text-gray-500 text-xs">Location</div>
                            <div className="text-gray-200">{c.preferred_location || '-'}</div>
                          </div>
                          <div>
                            <div className="text-gray-500 text-xs">Emp. Type</div>
                            <div className="text-gray-200">{c.employment_type || '-'}</div>
                          </div>
                          <div>
                            <div className="text-gray-500 text-xs">Immediate Joiner</div>
                            <div className="text-gray-200">{c.immediate_joiner || '-'}</div>
                          </div>
                        </div>
                      </div>

                      {c.match_score !== null ? (
                        <>
                          <div className="mb-6">
                            <h4 className="text-sm uppercase font-bold text-gray-400 tracking-wider mb-4">Score Breakdown</h4>
                            {c.score_breakdown && Object.keys(parseJson(c.score_breakdown)).length > 0 && (
                              <div className="bg-white/5 rounded-lg p-4 border border-white/10 max-w-sm">
                                {Object.entries(parseJson(c.score_breakdown)).map(([key, data]: [string, any]) => (
                                  <div key={key} className="flex justify-between items-center py-1">
                                    <span className="text-gray-300 w-32">{key}</span>
                                    <div className="flex-grow mx-4 h-2 bg-gray-700 rounded-full overflow-hidden">
                                      <div 
                                        className="h-full bg-blue-500 rounded-full" 
                                        style={{ width: `${data.score}%` }}
                                      ></div>
                                    </div>
                                    <span className="text-white font-mono text-sm w-12 text-right">{data.weight}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                            {/* Matched and Missing Skills */}
                            <div>
                              <h4 className="text-xs uppercase font-bold text-gray-400 tracking-wider mb-3">Matched</h4>
                              {parseJson(c.matched_skills).length > 0 ? (
                                <ul className="space-y-1 mb-6">
                                  {parseJson(c.matched_skills).map((s: string, i: number) => (
                                    <li key={i} className="text-gray-300 text-sm flex items-center">
                                      <span className="text-green-500 mr-2 font-bold">✓</span> {s}
                                    </li>
                                  ))}
                                </ul>
                              ) : (
                                <p className="text-sm text-gray-500 mb-6 italic">No skills matched.</p>
                              )}

                              <h4 className="text-xs uppercase font-bold text-gray-400 tracking-wider mb-3">Missing</h4>
                              {parseJson(c.missing_skills).length > 0 ? (
                                <ul className="space-y-1">
                                  {parseJson(c.missing_skills).map((s: string, i: number) => (
                                    <li key={i} className="text-gray-300 text-sm flex items-center">
                                      <span className="text-red-500 mr-2 font-bold">✗</span> {s}
                                    </li>
                                  ))}
                                </ul>
                              ) : (
                                <p className="text-sm text-gray-500 italic">No missing skills.</p>
                              )}
                            </div>

                            {/* Recommendation and Reason */}
                            <div className="bg-white/5 rounded-lg p-5 border border-white/10 h-fit">
                              {(() => {
                                const { rec, reason } = getRecAndReason(c.recommendation);
                                return (
                                  <>
                                    <h4 className="text-xs uppercase font-bold text-gray-400 tracking-wider mb-2">Recommendation</h4>
                                    <div className={`text-2xl font-bold mb-6 ${rec.toLowerCase().includes('hire') ? 'text-green-400' : rec.toLowerCase().includes('reject') ? 'text-red-400' : 'text-yellow-400'}`}>
                                      {rec}
                                    </div>
                                    
                                    <h4 className="text-xs uppercase font-bold text-gray-400 tracking-wider mb-2">Reason</h4>
                                    <div className="text-sm text-gray-300 leading-relaxed whitespace-pre-line">
                                      {reason}
                                    </div>
                                  </>
                                );
                              })()}
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Previous Raw data mapping can be removed or kept, I will keep it but add Integrations above it */}
                          </div>
                          
                          {/* Integrations Section */}
                          <div className="mt-6 border-t border-white/10 pt-6">
                            <h4 className="text-sm uppercase font-bold text-gray-400 tracking-wider mb-4">Integrations & Actions</h4>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                              <div className="bg-white/5 p-4 rounded-lg border border-white/10 shadow-sm">
                                <h5 className="text-sm font-semibold mb-3 text-blue-400">Zoho ATS</h5>
                                {c.zoho_candidate_id ? (
                                  <div className="text-xs text-green-400 flex items-center font-mono bg-green-500/10 p-2 rounded"><CheckCircle className="w-3 h-3 mr-1"/> {c.zoho_candidate_id}</div>
                                ) : (
                                  <button onClick={() => handleIntegration(c.id, 'zoho/sync')} disabled={role === 'hiring_manager'} className="text-xs bg-blue-500/20 hover:bg-blue-500/40 text-blue-300 py-2 px-3 rounded w-full transition font-medium">Sync to Zoho</button>
                                )}
                              </div>
                              <div className="bg-white/5 p-4 rounded-lg border border-white/10 shadow-sm">
                                <h5 className="text-sm font-semibold mb-3 text-purple-400">HackerEarth</h5>
                                {c.hackerearth_assessment_url ? (
                                  <div className="text-xs text-green-400 flex items-center font-mono bg-green-500/10 p-2 rounded"><CheckCircle className="w-3 h-3 mr-1"/> Sent. Score: {c.hackerearth_score !== null ? `${c.hackerearth_score}%` : 'Pending'}</div>
                                ) : (
                                  <button onClick={() => handleIntegration(c.id, 'hackerearth/invite')} disabled={role === 'hiring_manager'} className="text-xs bg-purple-500/20 hover:bg-purple-500/40 text-purple-300 py-2 px-3 rounded w-full transition font-medium">Send Test</button>
                                )}
                              </div>
                              <div className="bg-white/5 p-4 rounded-lg border border-white/10 shadow-sm">
                                <h5 className="text-sm font-semibold mb-3 text-yellow-400">AuthBridge BGV</h5>
                                {c.authbridge_bgv_status ? (
                                  <div className="text-xs text-yellow-400 flex items-center font-mono bg-yellow-500/10 p-2 rounded">Status: {c.authbridge_bgv_status}</div>
                                ) : (
                                  <button onClick={() => handleIntegration(c.id, 'authbridge/bgv')} disabled={role === 'hiring_manager'} className="text-xs bg-yellow-500/20 hover:bg-yellow-500/40 text-yellow-300 py-2 px-3 rounded w-full transition font-medium">Initiate BGV</button>
                                )}
                              </div>
                              <div className="bg-white/5 p-4 rounded-lg border border-white/10 shadow-sm">
                                <h5 className="text-sm font-semibold mb-3 text-pink-400">Keka HRMS</h5>
                                {c.keka_employee_id ? (
                                  <div className="text-xs text-green-400 flex items-center font-mono bg-green-500/10 p-2 rounded"><CheckCircle className="w-3 h-3 mr-1"/> {c.keka_employee_id}</div>
                                ) : (
                                  <button onClick={() => handleIntegration(c.id, 'keka/onboard')} disabled={role === 'hiring_manager'} className="text-xs bg-pink-500/20 hover:bg-pink-500/40 text-pink-300 py-2 px-3 rounded w-full transition font-medium">Onboard to Keka</button>
                                )}
                              </div>
                            </div>
                          </div>

                          <div className="mt-6">    <h4 className="text-xs uppercase font-bold text-gray-400 tracking-wider mb-2">Education History</h4>
                              {parseJson(c.education).length > 0 ? (
                                <ul className="text-sm space-y-2">
                                  {parseJson(c.education).map((e: any, i: number) => (
                                    <li key={i} className="text-gray-300 border-l-2 border-white/20 pl-3">
                                      <div className="font-semibold text-white">{e.degree}</div>
                                      <div>{e.institution} <span className="text-gray-500">({e.year})</span></div>
                                    </li>
                                  ))}
                                </ul>
                              ) : (
                                <p className="text-sm text-gray-500">None extracted</p>
                              )}
                            </div>
                            <div>
                              <h4 className="text-xs uppercase font-bold text-gray-400 tracking-wider mb-2">Work Experience</h4>
                              {parseJson(c.experience).length > 0 ? (
                                <ul className="text-sm space-y-2">
                                  {parseJson(c.experience).map((e: any, i: number) => (
                                    <li key={i} className="text-gray-300 border-l-2 border-white/20 pl-3">
                                      <div className="font-semibold text-white">{e.title}</div>
                                      <div>{e.company} <span className="text-gray-500">({e.duration})</span></div>
                                    </li>
                                  ))}
                                </ul>
                              ) : (
                                <p className="text-sm text-gray-500">None extracted</p>
                              )}
                            </div>
                        </>
                      ) : (
                        <div className="text-center text-gray-400 italic">
                          Run analysis against a Job Description to view detailed logs.
                        </div>
                      )}
                      {/* Journey Section */}
                      <div className="bg-black/60 p-6 border-t border-white/10 mt-6 rounded-b-lg">
                        <h4 className="text-sm uppercase font-bold text-gray-400 tracking-wider mb-4">Candidate Journey Timeline</h4>
                        
                        <div className="relative border-l border-white/20 ml-3 pl-6 space-y-6">
                          {candidateJourneys[c.id] && candidateJourneys[c.id].length > 0 ? (
                            candidateJourneys[c.id].map((event: any, idx: number) => (
                              <div key={idx} className="relative">
                                {/* Dot marker */}
                                <span className="absolute -left-[31px] top-1.5 flex h-4.5 w-4.5 items-center justify-center rounded-full bg-blue-500 ring-4 ring-black/40">
                                  <span className="h-2 w-2 rounded-full bg-white"></span>
                                </span>
                                <div>
                                  <div className="flex flex-wrap items-center justify-between gap-2">
                                    <span className="font-semibold text-white text-xs bg-blue-500/20 text-blue-400 border border-blue-500/20 px-2.5 py-0.5 rounded-full">
                                      {event.stage}
                                    </span>
                                    <span className="text-xs text-gray-500">
                                      {new Date(event.created_at).toLocaleString()}
                                    </span>
                                  </div>
                                  <p className="text-gray-300 text-sm mt-2 font-medium">
                                    Status: <span className="text-gray-400 font-normal">{event.status}</span>
                                  </p>
                                  {event.remarks && (
                                    <p className="text-gray-400 text-sm mt-1 bg-white/5 p-2 rounded border border-white/5 italic">
                                      "{event.remarks}"
                                    </p>
                                  )}
                                  <p className="text-xs text-gray-500 mt-1">
                                    Updated by: <span className="text-gray-400 font-semibold">{event.updated_by}</span>
                                  </p>
                                </div>
                              </div>
                            ))
                          ) : (
                            <div className="text-gray-500 text-sm italic">No journey history recorded yet.</div>
                          )}
                        </div>

                        {/* Form to log a new journey event */}
                        {role !== 'hiring_manager' && (
                          <div className="mt-8 border-t border-white/10 pt-6">
                            <h5 className="text-sm font-semibold text-gray-300 mb-4">Add Journey Event / Stage Transition</h5>
                            <form onSubmit={(e) => {
                              e.preventDefault();
                              const form = e.target as HTMLFormElement;
                              const stage = (form.elements.namedItem('stage') as HTMLSelectElement).value;
                              const remarks = (form.elements.namedItem('remarks') as HTMLInputElement).value;
                              handleLogJourneyEvent(c.id, stage, remarks);
                              form.reset();
                            }} className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end bg-white/5 p-4 rounded-lg border border-white/10">
                              <div>
                                <label className="block text-xs text-gray-400 mb-1">Target Stage</label>
                                <select name="stage" required className="w-full bg-gray-900 border border-white/10 rounded p-2 text-sm text-white focus:outline-none focus:border-blue-500">
                                  <option value="Applied">Applied</option>
                                  <option value="Resume Parsed">Resume Parsed</option>
                                  <option value="AI Screening">AI Screening</option>
                                  <option value="Shortlisted">Shortlisted</option>
                                  <option value="Interview Scheduled">Interview Scheduled</option>
                                  <option value="Interview Completed">Interview Completed</option>
                                  <option value="Selected">Selected</option>
                                  <option value="Offer Sent">Offer Sent</option>
                                  <option value="Hired">Hired</option>
                                  <option value="Rejected">Rejected</option>
                                </select>
                              </div>
                              <div>
                                <label className="block text-xs text-gray-400 mb-1">Remarks</label>
                                <input type="text" name="remarks" placeholder="Optional comments..." className="w-full bg-gray-900 border border-white/10 rounded p-2 text-sm text-white focus:outline-none focus:border-blue-500" />
                              </div>
                              <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2 px-4 rounded transition-colors w-full h-9">
                                Log Transition
                              </button>
                            </form>
                          </div>
                        )}
                      </div>

                      {/* Comments Section */}
                      <div className="bg-black/60 p-6 border-t border-white/10 mt-6 rounded-b-lg">
                        <h4 className="text-sm uppercase font-bold text-gray-400 tracking-wider mb-4">Internal Comments</h4>
                        <div className="space-y-4 mb-4 max-h-40 overflow-y-auto">
                          {candidateComments[c.id] && candidateComments[c.id].length > 0 ? (
                            candidateComments[c.id].map((comment: any, idx: number) => (
                              <div key={idx} className="bg-gray-800 p-3 rounded-lg border border-white/5">
                                <div className="flex justify-between items-center mb-1">
                                  <span className="font-semibold text-blue-400 text-sm">{comment.author}</span>
                                  <span className="text-xs text-gray-500">{new Date(comment.created_at).toLocaleString()}</span>
                                </div>
                                <p className="text-gray-300 text-sm">{comment.text}</p>
                              </div>
                            ))
                          ) : (
                            <div className="text-gray-500 text-sm italic">No comments yet.</div>
                          )}
                        </div>
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={newCommentText}
                            onChange={(e) => setNewCommentText(e.target.value)}
                            placeholder="Add a comment..."
                            className="flex-1 bg-gray-900 border border-white/10 rounded p-2 text-sm focus:outline-none focus:border-blue-500"
                          />
                          <button
                            onClick={() => handleAddComment(c.id)}
                            disabled={!newCommentText.trim()}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white text-sm font-medium rounded transition-colors"
                          >
                            Post
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    ) : activeTab === 'matching' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-in fade-in duration-300">
          {/* Left Column: Input Selection & JD */}
          <div className="lg:col-span-1 flex flex-col space-y-6">
            <div className="glass-card p-6 flex flex-col">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <FileText className="mr-2 text-blue-500" /> Match Candidate
              </h2>
              <p className="text-gray-400 mb-4 text-sm">Select a candidate and input the target Job Description.</p>
              
              <div className="mb-4">
                <label className="block text-xs uppercase font-bold text-gray-400 tracking-wider mb-2">Select Candidate</label>
                <select 
                  value={selectedCandidateId || ""} 
                  onChange={(e) => {
                    setSelectedCandidateId(e.target.value ? Number(e.target.value) : null);
                    setMatchingResult(null);
                    setMatchingError(null);
                  }}
                  className="w-full bg-gray-800 border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors"
                >
                  <option value="">-- Select Candidate --</option>
                  {candidates.map((c) => (
                    <option key={c.id} value={c.id}>{c.name} (ID: {c.id})</option>
                  ))}
                </select>
              </div>

              <div className="mb-6">
                <label className="block text-xs uppercase font-bold text-gray-400 tracking-wider mb-2">Job Description</label>
                <textarea
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors resize-none min-h-[300px]"
                  placeholder="Paste the target Job Description here..."
                  value={matchingJd}
                  onChange={(e) => setMatchingJd(e.target.value)}
                ></textarea>
              </div>

              <button 
                onClick={handleJobMatch} 
                disabled={isMatchingLoading || !selectedCandidateId || !matchingJd.trim()}
                className={`w-full py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${
                  isMatchingLoading || !selectedCandidateId || !matchingJd.trim()
                    ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                    : 'bg-blue-500 hover:bg-blue-600 text-white shadow-lg shadow-blue-500/20 active:scale-[0.98]'
                }`}
              >
                <Play className="w-4 h-4" />
                {isMatchingLoading ? 'Analyzing Match...' : 'Analyze Match'}
              </button>
            </div>
          </div>

          {/* Right Column: Output Results */}
          <div className="glass-card p-6 lg:col-span-2 min-h-[500px] flex flex-col">
            <h2 className="text-xl font-semibold mb-6 flex items-center">
              <CheckCircle className="mr-2 text-green-500" /> Match Analysis Result
            </h2>

            {matchingError && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-lg text-sm mb-6 flex items-center">
                <span className="font-bold mr-2">Error:</span> {matchingError}
              </div>
            )}

            {isMatchingLoading ? (
              <div className="flex-grow flex flex-col items-center justify-center space-y-4 py-12">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-gray-400 text-sm animate-pulse">Running multi-agent requirements extraction and comparison...</p>
              </div>
            ) : matchingResult ? (
              <div className="space-y-8 animate-in fade-in duration-300">
                {/* Score & Recommendation Summary */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-6 text-center shadow-sm">
                    <span className="block text-xs uppercase font-bold text-gray-500 tracking-wider mb-2">Overall Match Score</span>
                    <div className="text-5xl font-black text-blue-400">{matchingResult.match_score}%</div>
                    <div className="mt-4 h-2.5 bg-gray-800 rounded-full overflow-hidden w-full mx-auto max-w-[120px]">
                      <div 
                        className="h-full bg-blue-400 rounded-full" 
                        style={{ width: `${matchingResult.match_score}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="md:col-span-2 bg-white/5 border border-white/10 rounded-2xl p-6 shadow-sm">
                    <span className="block text-xs uppercase font-bold text-gray-500 tracking-wider mb-2">AI Summary / Fit Assessment</span>
                    <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">{matchingResult.summary}</p>
                  </div>
                </div>

                {/* Tech Skill Match */}
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-sm space-y-6">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-white">Tech Skill Match</h3>
                      <p className="text-xs text-gray-400">Comparison of required technical skills from the job description against the resume.</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-3xl font-black text-blue-400">
                        {matchingResult.tech_match_score !== undefined ? matchingResult.tech_match_score : 100}%
                      </div>
                      <div className="w-24 h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-blue-400 rounded-full" 
                          style={{ width: `${matchingResult.tech_match_score !== undefined ? matchingResult.tech_match_score : 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-sm uppercase font-bold text-gray-400 tracking-wider mb-3 flex items-center">
                        <span className="w-2.5 h-2.5 rounded-full bg-green-500 mr-2"></span>
                        Matched Technologies ({(matchingResult.matched_technologies || []).length})
                      </h4>
                      {(matchingResult.matched_technologies || []).length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {(matchingResult.matched_technologies || []).map((tech: string, idx: number) => (
                            <span key={idx} className="px-3 py-1.5 bg-green-500/10 text-green-400 border border-green-500/20 rounded-full text-xs font-semibold">
                              ✓ {tech}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500 italic">No matched technologies.</p>
                      )}
                    </div>

                    <div>
                      <h4 className="text-sm uppercase font-bold text-gray-400 tracking-wider mb-3 flex items-center">
                        <span className="w-2.5 h-2.5 rounded-full bg-red-500 mr-2"></span>
                        Missing Technologies ({(matchingResult.missing_technologies || []).length})
                      </h4>
                      {(matchingResult.missing_technologies || []).length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {(matchingResult.missing_technologies || []).map((tech: string, idx: number) => (
                            <span key={idx} className="px-3 py-1.5 bg-red-500/10 text-red-400 border border-red-500/20 rounded-full text-xs font-semibold">
                              ✗ {tech}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500 italic">No missing technologies.</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Skills Analysis */}
                <div className="space-y-6">
                  <div>
                    <h3 className="text-sm uppercase font-bold text-gray-400 tracking-wider mb-3 flex items-center">
                      <span className="w-2.5 h-2.5 rounded-full bg-green-500 mr-2"></span>
                      Matched Skills ({matchingResult.matched_skills.length})
                    </h3>
                    {matchingResult.matched_skills.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {matchingResult.matched_skills.map((s: string, idx: number) => (
                          <span key={idx} className="px-3 py-1.5 bg-green-500/10 text-green-400 border border-green-500/20 rounded-full text-xs font-semibold">
                            ✓ {s}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 italic">No matching skills identified.</p>
                    )}
                  </div>

                  <div>
                    <h3 className="text-sm uppercase font-bold text-gray-400 tracking-wider mb-3 flex items-center">
                      <span className="w-2.5 h-2.5 rounded-full bg-red-500 mr-2"></span>
                      Missing Skills ({matchingResult.missing_skills.length})
                    </h3>
                    {matchingResult.missing_skills.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {matchingResult.missing_skills.map((s: string, idx: number) => (
                          <span key={idx} className="px-3 py-1.5 bg-red-500/10 text-red-400 border border-red-500/20 rounded-full text-xs font-semibold">
                            ✗ {s}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 italic">No missing skills identified.</p>
                    )}
                  </div>

                  <div>
                    <h3 className="text-sm uppercase font-bold text-gray-400 tracking-wider mb-3 flex items-center">
                      <span className="w-2.5 h-2.5 rounded-full bg-blue-500 mr-2"></span>
                      Additional / Extra Skills ({matchingResult.extra_skills.length})
                    </h3>
                    {matchingResult.extra_skills.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {matchingResult.extra_skills.map((s: string, idx: number) => (
                          <span key={idx} className="px-3 py-1.5 bg-blue-500/10 text-blue-300 border border-blue-500/20 rounded-full text-xs font-semibold">
                            + {s}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 italic">No additional skills identified.</p>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-grow flex flex-col items-center justify-center text-center p-12 text-gray-400">
                <FileText className="w-16 h-16 text-gray-600 mb-4 stroke-1" />
                <h3 className="text-lg font-medium mb-1">No Match Analysis Performed</h3>
                <p className="text-sm text-gray-500 max-w-sm">Select a candidate and paste a job description on the left, then click "Analyze Match" to generate insights.</p>
              </div>
            )}
          </div>
        </div>
      ) : activeTab === 'analytics' ? (
        <div className="space-y-8 animate-in fade-in duration-300">
          <div className="glass-card p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center text-blue-400 border-b border-white/10 pb-4">
              📊 Diversity & Inclusion Analytics
            </h2>

            {isDiversityLoading || !diversityData ? (
              <div className="flex flex-col items-center justify-center py-16 space-y-4">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-gray-400 text-sm">Aggregating database demographic and hiring metrics...</p>
              </div>
            ) : (
              <div className="space-y-8">
                {/* Metrics Row */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-sm">
                    <span className="block text-xs uppercase font-bold text-gray-500 tracking-wider mb-2">Total Candidates</span>
                    <div className="text-4xl font-black text-white">{candidates.length}</div>
                    <p className="text-xs text-gray-400 mt-2">Active records in pool</p>
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-sm">
                    <span className="block text-xs uppercase font-bold text-gray-500 tracking-wider mb-2">Selection Rate</span>
                    <div className="text-4xl font-black text-green-400">{diversityData.selection_rate}%</div>
                    <p className="text-xs text-gray-400 mt-2">Hired or Selected candidates</p>
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-sm">
                    <span className="block text-xs uppercase font-bold text-gray-500 tracking-wider mb-2">Rejection Rate</span>
                    <div className="text-4xl font-black text-red-400">{diversityData.rejection_rate}%</div>
                    <p className="text-xs text-gray-400 mt-2">Rejected candidates</p>
                  </div>
                </div>

                {/* Distribution Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Gender */}
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-4 border-b border-white/5 pb-2">Gender Representation</h3>
                    <div className="space-y-4">
                      {diversityData.gender_distribution.length > 0 ? (
                        diversityData.gender_distribution.map((item: any, idx: number) => {
                          const percentage = candidates.length > 0 ? (item.value / candidates.length) * 100 : 0;
                          return (
                            <div key={idx} className="space-y-1">
                              <div className="flex justify-between text-sm">
                                <span className="text-gray-300 font-medium">{item.name}</span>
                                <span className="text-gray-400">{item.value} ({percentage.toFixed(1)}%)</span>
                              </div>
                              <div className="h-3 bg-gray-800 rounded-full overflow-hidden w-full">
                                <div className="h-full bg-blue-500 rounded-full transition-all duration-500" style={{ width: `${percentage}%` }}></div>
                              </div>
                            </div>
                          );
                        })
                      ) : (
                        <p className="text-gray-500 text-sm italic">No gender data available.</p>
                      )}
                    </div>
                  </div>

                  {/* Education */}
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-4 border-b border-white/5 pb-2">Education Background</h3>
                    <div className="space-y-4">
                      {diversityData.education_distribution.length > 0 ? (
                        diversityData.education_distribution.map((item: any, idx: number) => {
                          const percentage = candidates.length > 0 ? (item.value / candidates.length) * 100 : 0;
                          return (
                            <div key={idx} className="space-y-1">
                              <div className="flex justify-between text-sm">
                                <span className="text-gray-300 font-medium">{item.name}</span>
                                <span className="text-gray-400">{item.value} ({percentage.toFixed(1)}%)</span>
                              </div>
                              <div className="h-3 bg-gray-800 rounded-full overflow-hidden w-full">
                                <div className="h-full bg-purple-500 rounded-full transition-all duration-500" style={{ width: `${percentage}%` }}></div>
                              </div>
                            </div>
                          );
                        })
                      ) : (
                        <p className="text-gray-500 text-sm italic">No education data available.</p>
                      )}
                    </div>
                  </div>

                  {/* Experience */}
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-4 border-b border-white/5 pb-2">Experience Level</h3>
                    <div className="space-y-4">
                      {diversityData.experience_distribution.length > 0 ? (
                        diversityData.experience_distribution.map((item: any, idx: number) => {
                          const percentage = candidates.length > 0 ? (item.value / candidates.length) * 100 : 0;
                          return (
                            <div key={idx} className="space-y-1">
                              <div className="flex justify-between text-sm">
                                <span className="text-gray-300 font-medium capitalize">{item.name}</span>
                                <span className="text-gray-400">{item.value} ({percentage.toFixed(1)}%)</span>
                              </div>
                              <div className="h-3 bg-gray-800 rounded-full overflow-hidden w-full">
                                <div className="h-full bg-green-500 rounded-full transition-all duration-500" style={{ width: `${percentage}%` }}></div>
                              </div>
                            </div>
                          );
                        })
                      ) : (
                        <p className="text-gray-500 text-sm italic">No experience data available.</p>
                      )}
                    </div>
                  </div>

                  {/* Location */}
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-4 border-b border-white/5 pb-2">Candidate Locations</h3>
                    <div className="space-y-4">
                      {diversityData.location_distribution.length > 0 ? (
                        diversityData.location_distribution.map((item: any, idx: number) => {
                          const percentage = candidates.length > 0 ? (item.value / candidates.length) * 100 : 0;
                          return (
                            <div key={idx} className="space-y-1">
                              <div className="flex justify-between text-sm">
                                <span className="text-gray-300 font-medium">{item.name}</span>
                                <span className="text-gray-400">{item.value} ({percentage.toFixed(1)}%)</span>
                              </div>
                              <div className="h-3 bg-gray-800 rounded-full overflow-hidden w-full">
                                <div className="h-full bg-amber-500 rounded-full transition-all duration-500" style={{ width: `${percentage}%` }}></div>
                              </div>
                            </div>
                          );
                        })
                      ) : (
                        <p className="text-gray-500 text-sm italic">No location data available.</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Funnel Section */}
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-6 border-b border-white/5 pb-2">Hiring Funnel</h3>
                  <div className="space-y-4 max-w-2xl mx-auto">
                    {diversityData.hiring_funnel.length > 0 ? (
                      diversityData.hiring_funnel.map((item: any, idx: number) => {
                        const percentage = candidates.length > 0 ? (item.value / candidates.length) * 100 : 0;
                        return (
                          <div key={idx} className="flex items-center gap-4">
                            <span className="w-40 text-sm text-gray-300 font-semibold text-right">{item.name}</span>
                            <div className="flex-1 h-8 bg-gray-800/50 rounded-lg overflow-hidden border border-white/5 relative">
                              <div className="h-full bg-gradient-to-r from-blue-600/50 to-indigo-600/50 rounded-lg transition-all duration-500" style={{ width: `${percentage}%` }}></div>
                              <span className="absolute inset-0 flex items-center pl-3 text-xs font-bold text-white">
                                {item.value} candidates ({percentage.toFixed(0)}%)
                              </span>
                            </div>
                          </div>
                        );
                      })
                    ) : (
                      <p className="text-gray-500 text-sm italic text-center">No funnel data available.</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : activeTab === 'sourcing' ? (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Sourcing Modal */}
          {showAddSourcedModal && (
            <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm overflow-y-auto py-8">
              <div className="bg-gray-900 border border-white/10 p-8 rounded-2xl max-w-2xl w-full shadow-2xl relative my-auto">
                <button onClick={() => setShowAddSourcedModal(false)} className="absolute top-6 right-6 text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
                <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
                  <UserPlus className="text-blue-400" /> Add Sourced Candidate
                </h3>
                <form onSubmit={handleAddSourced} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Full Name *</label>
                      <input type="text" required value={newSourced.name} onChange={e => setNewSourced({...newSourced, name: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Email</label>
                      <input type="email" value={newSourced.email} onChange={e => setNewSourced({...newSourced, email: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Phone</label>
                      <input type="text" value={newSourced.phone} onChange={e => setNewSourced({...newSourced, phone: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Current Company</label>
                      <input type="text" value={newSourced.current_company} onChange={e => setNewSourced({...newSourced, current_company: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Preferred Location</label>
                      <input type="text" value={newSourced.preferred_location} onChange={e => setNewSourced({...newSourced, preferred_location: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Source Platform *</label>
                      <select value={newSourced.source_platform} onChange={e => setNewSourced({...newSourced, source_platform: e.target.value})} className="w-full bg-gray-800 border border-white/10 rounded p-2 text-sm">
                        <option value="LinkedIn">LinkedIn</option>
                        <option value="GitHub">GitHub</option>
                        <option value="Naukri">Naukri</option>
                        <option value="Indeed">Indeed</option>
                        <option value="Referral">Referral</option>
                        <option value="Career Website">Career Website</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Source / Profile URL</label>
                      <input type="url" value={newSourced.source_url} onChange={e => setNewSourced({...newSourced, source_url: e.target.value})} placeholder="https://..." className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">GitHub Username (Auto-Enrich Stats)</label>
                      <input type="text" value={newSourced.github_username} onChange={e => setNewSourced({...newSourced, github_username: e.target.value})} placeholder="e.g. torvalds" className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Skills (comma separated)</label>
                    <input type="text" value={newSourced.skills} onChange={e => setNewSourced({...newSourced, skills: e.target.value})} placeholder="Python, React, FastAPI, Docker" className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Initial Notes</label>
                    <textarea value={newSourced.initial_notes} onChange={e => setNewSourced({...newSourced, initial_notes: e.target.value})} rows={2} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                  </div>
                  <div className="flex justify-end gap-3 pt-4 border-t border-white/10">
                    <button type="button" onClick={() => setShowAddSourcedModal(false)} className="px-4 py-2 bg-white/5 rounded-lg text-sm">Cancel</button>
                    <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium">Save Sourced Candidate</button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Sourcing Header & Filter Bar */}
          <div className="glass-card p-6 space-y-6">
            <div className="flex flex-wrap justify-between items-center gap-4 border-b border-white/10 pb-4">
              <div>
                <h2 className="text-2xl font-bold text-blue-400 flex items-center gap-2">
                  <Users /> Candidate Sourcing & Social Profiles
                </h2>
                <p className="text-gray-400 text-sm">Manage multi-platform sourcing pipelines (LinkedIn, GitHub, Naukri, Indeed, Referrals)</p>
              </div>
              <button onClick={() => setShowAddSourcedModal(true)} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold flex items-center gap-2 shadow-lg">
                <UserPlus className="w-4 h-4" /> Add Sourced Candidate
              </button>
            </div>

            {/* Filter Bar */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              <input type="text" placeholder="Search by name, company..." value={sourcingFilter.search} onChange={e => setSourcingFilter({...sourcingFilter, search: e.target.value})} className="bg-white/5 border border-white/10 rounded-lg p-2.5 text-sm" />
              <select value={sourcingFilter.platform} onChange={e => setSourcingFilter({...sourcingFilter, platform: e.target.value})} className="bg-gray-800 border border-white/10 rounded-lg p-2.5 text-sm">
                <option value="">All Sources</option>
                <option value="LinkedIn">LinkedIn</option>
                <option value="GitHub">GitHub</option>
                <option value="Naukri">Naukri</option>
                <option value="Indeed">Indeed</option>
                <option value="Referral">Referral</option>
                <option value="Career Website">Career Website</option>
              </select>
              <input type="text" placeholder="Filter by skills..." value={sourcingFilter.skills} onChange={e => setSourcingFilter({...sourcingFilter, skills: e.target.value})} className="bg-white/5 border border-white/10 rounded-lg p-2.5 text-sm" />
              <input type="text" placeholder="Filter by location..." value={sourcingFilter.location} onChange={e => setSourcingFilter({...sourcingFilter, location: e.target.value})} className="bg-white/5 border border-white/10 rounded-lg p-2.5 text-sm" />
              <select value={sourcingFilter.stage} onChange={e => setSourcingFilter({...sourcingFilter, stage: e.target.value})} className="bg-gray-800 border border-white/10 rounded-lg p-2.5 text-sm">
                <option value="">All Pipeline Stages</option>
                <option value="Discovered">Discovered</option>
                <option value="Contacted">Contacted</option>
                <option value="Interested">Interested</option>
                <option value="Applied">Applied</option>
                <option value="Interview">Interview</option>
                <option value="Offer">Offer</option>
                <option value="Hired">Hired</option>
              </select>
            </div>

            {/* AI Ranking JD Input Box */}
            <div className="bg-blue-950/40 border border-blue-500/20 p-4 rounded-xl space-y-2">
              <label className="text-xs font-semibold text-blue-300 uppercase tracking-wider block">Candidate AI Ranking JD Context</label>
              <div className="flex gap-2">
                <input type="text" value={rankJdText} onChange={e => setRankJdText(e.target.value)} placeholder="Paste Job Description here to rank sourced candidates..." className="flex-1 bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm" />
              </div>
            </div>
          </div>

          {/* Sourced Candidates Cards List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {sourcedCandidates.length > 0 ? (
              sourcedCandidates.map(cand => (
                <div key={cand.id} className="glass-card p-6 space-y-4 flex flex-col justify-between border border-white/10 hover:border-blue-500/30 transition-all">
                  <div>
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-xl font-bold text-white">{cand.name}</h3>
                        <p className="text-gray-400 text-xs">{cand.current_company || "Company N/A"} • {cand.preferred_location || "Location N/A"}</p>
                      </div>
                      <span className="px-3 py-1 bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-full text-xs font-semibold">
                        {cand.sources && cand.sources[0] ? cand.sources[0].source_platform : "Sourced"}
                      </span>
                    </div>

                    <div className="mt-3 space-y-1 text-xs text-gray-300">
                      {cand.email && <p>📧 {cand.email}</p>}
                      {cand.phone && <p>📞 {cand.phone}</p>}
                      {cand.skills && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {cand.skills.split(',').map((s: string, idx: number) => (
                            <span key={idx} className="bg-white/10 px-2 py-0.5 rounded text-[11px] text-gray-200">{s.trim()}</span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Social Profiles Info */}
                    {cand.social_profiles && cand.social_profiles.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-white/10 space-y-2">
                        <p className="text-xs font-semibold text-gray-400 uppercase">Social Profiles</p>
                        {cand.social_profiles.map((sp: any, idx: number) => (
                          <div key={idx} className="bg-black/30 p-2.5 rounded-lg text-xs space-y-1 border border-white/5">
                            <div className="flex justify-between font-medium text-blue-400">
                              <span>🔗 {sp.platform} ({sp.username || "Profile"})</span>
                              <a href={sp.profile_url} target="_blank" rel="noreferrer" className="underline hover:text-white">View</a>
                            </div>
                            {sp.bio && <p className="text-gray-400 italic text-[11px] line-clamp-2">{sp.bio}</p>}
                            {sp.platform === "GitHub" && (
                              <div className="flex gap-3 text-[11px] text-gray-300 font-mono mt-1">
                                <span>👥 {sp.followers} followers</span>
                                <span>📁 {sp.repositories_count} repos</span>
                                <span>⭐ {sp.total_stars} stars</span>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* AI Ranking Badge */}
                    {cand.match_score !== null && cand.match_score !== undefined && (
                      <div className="mt-3 p-3 bg-purple-950/40 border border-purple-500/20 rounded-lg flex justify-between items-center">
                        <div>
                          <p className="text-xs font-semibold text-purple-300">AI Rank Match Score</p>
                          <p className="text-xs text-gray-400">{cand.recommendation || "Evaluated"}</p>
                        </div>
                        <span className="text-lg font-bold text-purple-400">{cand.match_score.toFixed(0)}%</span>
                      </div>
                    )}
                  </div>

                  {/* Sourcing Pipeline Stage Actions */}
                  <div className="pt-4 border-t border-white/10 space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-gray-400">Pipeline Stage:</span>
                      <span className="font-bold text-blue-400">{cand.status || "Discovered"}</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {["Discovered", "Contacted", "Interested", "Applied", "Interview", "Offer", "Hired"].map(stg => (
                        <button
                          key={stg}
                          onClick={() => handlePipelineMove(cand.id, stg)}
                          className={`px-2 py-1 rounded text-[10px] font-medium transition-colors ${cand.status === stg ? 'bg-blue-600 text-white font-bold' : 'bg-white/5 hover:bg-white/15 text-gray-300'}`}
                        >
                          {stg}
                        </button>
                      ))}
                    </div>
                    <button
                      onClick={() => handleRankSourced(cand.id)}
                      disabled={rankingId === cand.id}
                      className="w-full mt-2 py-1.5 bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/30 rounded-lg text-xs font-medium text-purple-200 transition-colors flex justify-center items-center gap-1"
                    >
                      {rankingId === cand.id ? "Calculating AI Rank..." : "⚡ Rank Candidate with AI"}
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-2 glass-card p-12 text-center text-gray-400">
                <Users className="w-12 h-12 mx-auto mb-3 text-gray-600" />
                <p className="font-medium text-base">No sourced candidates match criteria.</p>
                <p className="text-xs text-gray-500 mt-1">Click "Add Sourced Candidate" to source profiles from LinkedIn, GitHub, Naukri, or Indeed.</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Lifecycle Management View */
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Create Job Modal */}
          {showCreateJobModal && (
            <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm overflow-y-auto py-8">
              <div className="bg-gray-900 border border-white/10 p-8 rounded-2xl max-w-xl w-full shadow-2xl relative my-auto">
                <button onClick={() => setShowCreateJobModal(false)} className="absolute top-6 right-6 text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
                <h3 className="text-2xl font-bold mb-6">Post New Job</h3>
                <form onSubmit={handleCreateJobSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Job Title *</label>
                    <input type="text" required value={newJob.title} onChange={e => setNewJob({...newJob, title: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Department</label>
                      <input type="text" value={newJob.department} onChange={e => setNewJob({...newJob, department: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Location</label>
                      <input type="text" value={newJob.location} onChange={e => setNewJob({...newJob, location: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Description *</label>
                    <textarea required value={newJob.description} onChange={e => setNewJob({...newJob, description: e.target.value})} rows={3} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Requirements</label>
                    <textarea value={newJob.requirements} onChange={e => setNewJob({...newJob, requirements: e.target.value})} rows={2} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                  </div>
                  <div className="flex justify-end gap-3 pt-4 border-t border-white/10">
                    <button type="button" onClick={() => setShowCreateJobModal(false)} className="px-4 py-2 bg-white/5 rounded-lg text-sm">Cancel</button>
                    <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium">Create Job</button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Schedule Interview Modal */}
          {showScheduleInterviewModal && (
            <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm overflow-y-auto py-8">
              <div className="bg-gray-900 border border-white/10 p-8 rounded-2xl max-w-lg w-full shadow-2xl relative my-auto">
                <button onClick={() => setShowScheduleInterviewModal(false)} className="absolute top-6 right-6 text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
                <h3 className="text-2xl font-bold mb-6">Schedule Candidate Interview</h3>
                <form onSubmit={handleScheduleInterviewSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Select Candidate *</label>
                    <select required value={newInterview.candidate_id} onChange={e => setNewInterview({...newInterview, candidate_id: Number(e.target.value)})} className="w-full bg-gray-800 border border-white/10 rounded p-2 text-sm">
                      <option value={0}>-- Select Candidate --</option>
                      {candidates.map(c => (
                        <option key={c.id} value={c.id}>{c.name} (ID: {c.id})</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Interviewer Name *</label>
                    <input type="text" required value={newInterview.interviewer} onChange={e => setNewInterview({...newInterview, interviewer: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Scheduled Date & Time *</label>
                    <input type="datetime-local" required value={newInterview.scheduled_at} onChange={e => setNewInterview({...newInterview, scheduled_at: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Interview Type</label>
                    <select value={newInterview.interview_type} onChange={e => setNewInterview({...newInterview, interview_type: e.target.value})} className="w-full bg-gray-800 border border-white/10 rounded p-2 text-sm">
                      <option value="Technical">Technical</option>
                      <option value="System Design">System Design</option>
                      <option value="HR">HR</option>
                      <option value="Cultural Fit">Cultural Fit</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Meeting Link</label>
                    <input type="url" value={newInterview.meeting_link} onChange={e => setNewInterview({...newInterview, meeting_link: e.target.value})} placeholder="https://meet.google.com/..." className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                  </div>
                  <div className="flex justify-end gap-3 pt-4 border-t border-white/10">
                    <button type="button" onClick={() => setShowScheduleInterviewModal(false)} className="px-4 py-2 bg-white/5 rounded-lg text-sm">Cancel</button>
                    <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium">Schedule Interview</button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Create Offer Modal */}
          {showCreateOfferModal && (
            <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm overflow-y-auto py-8">
              <div className="bg-gray-900 border border-white/10 p-8 rounded-2xl max-w-lg w-full shadow-2xl relative my-auto">
                <button onClick={() => setShowCreateOfferModal(false)} className="absolute top-6 right-6 text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
                <h3 className="text-2xl font-bold mb-6">Generate Candidate Offer</h3>
                <form onSubmit={handleCreateOfferSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Select Candidate *</label>
                    <select required value={newOffer.candidate_id} onChange={e => setNewOffer({...newOffer, candidate_id: Number(e.target.value)})} className="w-full bg-gray-800 border border-white/10 rounded p-2 text-sm">
                      <option value={0}>-- Select Candidate --</option>
                      {candidates.map(c => (
                        <option key={c.id} value={c.id}>{c.name} (ID: {c.id})</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Annual Salary (CTC) *</label>
                    <input type="number" required value={newOffer.salary} onChange={e => setNewOffer({...newOffer, salary: Number(e.target.value)})} className="w-full bg-white/5 border border-white/10 rounded p-2 text-sm" />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Currency</label>
                    <select value={newOffer.currency} onChange={e => setNewOffer({...newOffer, currency: e.target.value})} className="w-full bg-gray-800 border border-white/10 rounded p-2 text-sm">
                      <option value="USD">USD ($)</option>
                      <option value="INR">INR (₹)</option>
                      <option value="EUR">EUR (€)</option>
                      <option value="GBP">GBP (£)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Offer Status</label>
                    <select value={newOffer.status} onChange={e => setNewOffer({...newOffer, status: e.target.value})} className="w-full bg-gray-800 border border-white/10 rounded p-2 text-sm">
                      <option value="Draft">Draft</option>
                      <option value="Sent">Sent</option>
                      <option value="Accepted">Accepted</option>
                    </select>
                  </div>
                  <div className="flex justify-end gap-3 pt-4 border-t border-white/10">
                    <button type="button" onClick={() => setShowCreateOfferModal(false)} className="px-4 py-2 bg-white/5 rounded-lg text-sm">Cancel</button>
                    <button type="submit" className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium">Create Offer</button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Job Openings & Configurable Stages */}
          <div className="glass-card p-6 space-y-6">
            <div className="flex justify-between items-center border-b border-white/10 pb-4">
              <div>
                <h2 className="text-2xl font-bold text-blue-400 flex items-center gap-2">
                  💼 Active Jobs & Configurable Recruitment Stages
                </h2>
                <p className="text-gray-400 text-sm">Configure hiring stages per job posting</p>
              </div>
              <button onClick={() => setShowCreateJobModal(true)} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold flex items-center gap-2">
                + Create Job Posting
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {jobs.length > 0 ? (
                jobs.map(job => (
                  <div key={job.id} className="bg-black/30 p-5 rounded-xl border border-white/10 space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-bold text-lg text-white">{job.title}</h3>
                        <p className="text-xs text-gray-400">{job.department || "Dept N/A"} • {job.location || "Remote"}</p>
                      </div>
                      <span className="px-2.5 py-0.5 bg-green-500/20 text-green-300 border border-green-500/30 rounded-full text-xs font-semibold">
                        {job.status}
                      </span>
                    </div>
                    <p className="text-xs text-gray-300 line-clamp-2">{job.description}</p>
                    
                    <div className="pt-2">
                      <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Configured Stages</p>
                      <div className="flex flex-wrap gap-1.5">
                        {job.stages && job.stages.map((st: any) => (
                          <span key={st.id} className="bg-blue-500/10 border border-blue-500/20 text-blue-300 px-2 py-0.5 rounded text-[11px]">
                            {st.stage_order}. {st.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-400 text-sm italic col-span-2 text-center py-6">No jobs created yet. Click "Create Job Posting" to add your first job.</p>
              )}
            </div>
          </div>

          {/* Scheduled Interviews & Offers */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Interviews Card */}
            <div className="glass-card p-6 space-y-4">
              <div className="flex justify-between items-center border-b border-white/10 pb-3">
                <h3 className="text-lg font-bold text-blue-400">📅 Scheduled Interviews</h3>
                <button onClick={() => setShowScheduleInterviewModal(true)} className="px-3 py-1.5 bg-blue-600/30 hover:bg-blue-600/50 border border-blue-500/30 rounded-lg text-xs font-semibold text-blue-200">
                  + Schedule Interview
                </button>
              </div>

              <div className="space-y-3 max-h-[350px] overflow-y-auto">
                {interviews.length > 0 ? (
                  interviews.map(int => (
                    <div key={int.id} className="bg-black/30 p-3.5 rounded-lg border border-white/5 space-y-1 text-xs">
                      <div className="flex justify-between font-semibold text-white">
                        <span>Cand ID #{int.candidate_id} - {int.interview_type}</span>
                        <span className="text-blue-400">{int.status}</span>
                      </div>
                      <p className="text-gray-400">Interviewer: {int.interviewer} • Date: {new Date(int.scheduled_at).toLocaleString()}</p>
                      {int.meeting_link && <a href={int.meeting_link} target="_blank" rel="noreferrer" className="text-blue-400 underline">Join Meeting</a>}
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-xs italic text-center py-4">No interviews scheduled yet.</p>
                )}
              </div>
            </div>

            {/* Offers & Onboarding Card */}
            <div className="glass-card p-6 space-y-4">
              <div className="flex justify-between items-center border-b border-white/10 pb-3">
                <h3 className="text-lg font-bold text-blue-400">📜 Offers & Onboarding Status</h3>
                <button onClick={() => setShowCreateOfferModal(true)} className="px-3 py-1.5 bg-green-600/30 hover:bg-green-600/50 border border-green-500/30 rounded-lg text-xs font-semibold text-green-200">
                  + Generate Offer
                </button>
              </div>

              <div className="space-y-3 max-h-[350px] overflow-y-auto">
                {offers.length > 0 ? (
                  offers.map(off => (
                    <div key={off.id} className="bg-black/30 p-3.5 rounded-lg border border-white/5 space-y-1 text-xs">
                      <div className="flex justify-between font-semibold text-white">
                        <span>Cand ID #{off.candidate_id} - Offer {off.currency} {off.salary.toLocaleString()}</span>
                        <span className="text-green-400 font-bold">{off.status}</span>
                      </div>
                      <p className="text-gray-400">Sent Date: {off.sent_date ? new Date(off.sent_date).toLocaleDateString() : "Pending"}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-xs italic text-center py-2">No offer records available.</p>
                )}

                {onboardings.length > 0 && (
                  <div className="pt-2 border-t border-white/10 space-y-2">
                    <p className="text-[11px] font-semibold text-gray-400 uppercase">Active Onboarding Records</p>
                    {onboardings.map(onb => (
                      <div key={onb.id} className="bg-black/40 p-2.5 rounded-lg text-xs border border-white/5 flex justify-between">
                        <div>
                          <span className="font-semibold text-white">Candidate #{onb.candidate_id}</span>
                          <p className="text-gray-400 text-[11px]">BGV: {onb.background_check_status} • Docs: {onb.document_verification}</p>
                        </div>
                        <span className="text-blue-400 font-bold text-[11px]">{onb.joining_status}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Activity / Audit Logs Feed */}
          <div className="glass-card p-6 space-y-4">
            <h3 className="text-lg font-bold text-blue-400 border-b border-white/10 pb-3">📜 Candidate & Application Audit Logs</h3>
            <div className="space-y-2 max-h-[300px] overflow-y-auto font-mono text-xs">
              {activityLogs.length > 0 ? (
                activityLogs.map(log => (
                  <div key={log.id} className="bg-black/40 p-2.5 rounded border border-white/5 flex justify-between text-gray-300">
                    <div>
                      <span className="text-blue-400 font-bold">[{log.action}]</span> <span className="text-gray-400">by {log.performer}:</span> {log.details}
                    </div>
                    <span className="text-[10px] text-gray-500 ml-4">{new Date(log.created_at).toLocaleTimeString()}</span>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-xs italic text-center py-4">No audit logs recorded yet.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Floating Chat Widget */}
      {role !== 'hiring_manager' && (
        <div className="fixed bottom-6 right-6 z-50">
          {isChatOpen ? (
            <div className="bg-gray-900 border border-white/10 rounded-2xl shadow-2xl w-80 sm:w-96 h-[32rem] flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300">
              <div className="bg-primary/20 border-b border-white/10 p-4 flex justify-between items-center">
                <h3 className="font-bold flex items-center"><MessageSquare className="w-4 h-4 mr-2 text-blue-400" /> AI Assistant</h3>
                <button onClick={() => setIsChatOpen(false)} className="text-gray-400 hover:text-white transition">
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {chatMessages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[85%] p-3 rounded-lg text-sm whitespace-pre-wrap ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-gray-800 text-gray-200 border border-white/5 rounded-bl-none shadow-sm'}`}>
                      {msg.content}
                    </div>
                  </div>
                ))}
                {isChatLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-800 text-gray-400 p-3 rounded-lg rounded-bl-none border border-white/5 text-sm flex items-center space-x-2">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
                    </div>
                  </div>
                )}
              </div>

              <div className="p-3 border-t border-white/10 bg-gray-800">
                <form onSubmit={handleChatSend} className="flex gap-2">
                  <input 
                    type="text" 
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask about candidates..."
                    className="flex-1 bg-gray-900 border border-white/10 rounded p-2 text-sm focus:outline-none focus:border-blue-500"
                  />
                  <button type="submit" disabled={isChatLoading || !chatInput.trim()} className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white p-2 rounded transition-colors">
                    <Send className="w-4 h-4" />
                  </button>
                </form>
              </div>
            </div>
          ) : (
            <button 
              onClick={() => setIsChatOpen(true)}
              className="w-14 h-14 bg-blue-600 hover:bg-blue-700 rounded-full shadow-2xl flex items-center justify-center text-white transition-transform hover:scale-105"
            >
              <MessageSquare className="w-6 h-6" />
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default HRDashboard;
