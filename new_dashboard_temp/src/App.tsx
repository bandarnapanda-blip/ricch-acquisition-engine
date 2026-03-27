import React, { useState, useEffect } from 'react';
import { 
  Rocket, Funnel, Globe, Stars, Eye, Settings, LogOut, Activity, Search, ChevronRight, ArrowUpDown, ArrowUp, ArrowDown, Moon, Sun, X, MapPin, Target, Zap, Radar, CheckCircle2, Plus, Trash2, CheckSquare, Calendar, User, PanelLeftClose, PanelLeftOpen, Database
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from './lib/utils';
import { MetricCard } from './components/MetricCard';
import { AiImageGenerator } from './components/AiImageGenerator';
import { useLeads, useMetrics, useLogs, useAgents, useTasks, useGodView, api } from './api';
import { Lead, Task } from './types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area, LineChart, Line } from 'recharts';

const TABS = [
  { id: 'COMMAND', icon: Rocket, label: 'Dashboard' },
  { id: 'PIPELINE', icon: Funnel, label: 'Pipeline' },
  { id: 'TASKS', icon: CheckSquare, label: 'Tasks' },
  { id: 'INTEL', icon: Globe, label: 'Intelligence' },
  { id: 'SHOWCASE', icon: Stars, label: 'Showcase' },
  { id: 'GOD VIEW', icon: Eye, label: 'God View' },
  { id: 'CONFIG', icon: Settings, label: 'Settings' },
];

const TAB_BACKGROUNDS: Record<string, string> = {
  'COMMAND': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop',
  'PIPELINE': 'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?q=80&w=2564&auto=format&fit=crop',
  'TASKS': 'https://images.unsplash.com/photo-1507925922893-cb95f736568c?q=80&w=2564&auto=format&fit=crop',
  'INTEL': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2564&auto=format&fit=crop',
  'SHOWCASE': 'https://images.unsplash.com/photo-1614850523459-c2f4c699c52e?q=80&w=2564&auto=format&fit=crop',
  'GOD VIEW': 'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=2564&auto=format&fit=crop',
  'CONFIG': 'https://images.unsplash.com/photo-1600132806370-bf17e65e942f?q=80&w=2564&auto=format&fit=crop',
};

type SortKey = 'opportunityScore' | 'revenueLoss' | 'monthlyValue';
type SortOrder = 'asc' | 'desc' | null;

const GodView = () => {
  const { events, liveLeads, hotLeads } = useGodView();
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2 space-y-8">
        <div className="liquid-glass-panel rounded-[2rem] p-8 border border-white/10">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-2xl font-bold text-apple-base flex items-center gap-3">
                <Radar className="text-primary animate-pulse" size={24} /> Live System Pulse
              </h3>
              <p className="text-sm text-apple-muted mt-1">Real-time terminal output from Silas, Vex, and Diamond.</p>
            </div>
            <div className="flex gap-2">
              <span className="px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-ping" /> Synchronized
              </span>
            </div>
          </div>
          
          <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-4 terminal-scrollbar">
            {events.length === 0 ? (
              <div className="h-40 flex items-center justify-center text-apple-muted opacity-30 italic">
                Awaiting first pulse...
              </div>
            ) : (
              events.map((e, i) => (
                <motion.div 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  key={i} 
                  className="flex gap-4 group p-3 hover:bg-white/5 rounded-xl transition-colors border border-transparent hover:border-white/5"
                >
                  <span className="text-[10px] font-mono text-apple-muted/50 pt-1 shrink-0">
                    [{new Date(e.timestamp).toLocaleTimeString([], { hour12: false })}]
                  </span>
                  <div className="space-y-1 overflow-hidden">
                    <div className="flex items-center gap-2">
                      <span className={cn(
                        "text-[10px] font-bold px-1.5 py-0.5 rounded-sm uppercase tracking-tighter",
                        e.event.includes('Silas') || e.event.includes('Outreach') ? "bg-orange-500/10 text-orange-500" :
                        e.event.includes('Diamond') || e.event.includes('Intel') ? "bg-blue-500/10 text-blue-500" :
                        e.event.includes('Vex') || e.event.includes('QA') ? "bg-purple-500/10 text-purple-500" :
                        "bg-zinc-500/10 text-zinc-400"
                      )}>
                        {e.event.split(':')[0]}
                      </span>
                      <span className="text-xs font-medium text-apple-base truncate">
                        {e.event.includes(':') ? e.event.split(':').slice(1).join(':') : e.event}
                      </span>
                    </div>
                    {e.metadata && Object.keys(e.metadata).length > 0 && (
                      <div className="text-[10px] font-mono text-apple-muted/70 bg-black/20 p-2 rounded-lg border border-white/5 overflow-x-auto">
                        {JSON.stringify(e.metadata)}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="space-y-8">
        <div className="liquid-glass-panel rounded-[2rem] p-8 border border-white/10">
          <h3 className="text-xl font-bold text-apple-base mb-6 flex items-center gap-2">
            <Zap className="text-[#ffcc00]" size={20} /> Hot Activity
          </h3>
          <div className="space-y-4">
            {hotLeads.length === 0 ? (
              <p className="text-sm text-apple-muted italic opacity-50">No high-intent signals detected.</p>
            ) : (
              hotLeads.map((h, i) => (
                <div key={i} className="p-4 rounded-2xl bg-white/5 border border-[#ffcc00]/20 flex items-center justify-between group hover:border-[#ffcc00]/50 transition-all">
                  <div>
                    <div className="text-xs font-bold text-apple-base mb-1 truncate max-w-[140px]">{h.leadId}</div>
                    <div className="text-[10px] text-[#ffcc00] font-bold uppercase tracking-widest">{h.event}</div>
                  </div>
                  <ChevronRight size={16} className="text-[#ffcc00] opacity-0 group-hover:opacity-100 transition-all" />
                </div>
              ))
            )}
          </div>
        </div>

        <div className="liquid-glass-panel rounded-[2rem] p-8 border border-white/10">
          <h3 className="text-xl font-bold text-apple-base mb-6 flex items-center gap-2">
            <CheckCircle2 className="text-green-500" size={20} /> Active Nodes
          </h3>
          <div className="space-y-4">
            {['Silas', 'Diamond', 'Vex'].map((node) => (
              <div key={node} className="flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-apple-base/5 flex items-center justify-center">
                    <User size={18} className="text-apple-muted" />
                  </div>
                  <div>
                    <div className="text-sm font-bold text-apple-base">{node}</div>
                    <div className="text-[10px] text-apple-muted">Core Module Agent</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
                  <span className="text-[10px] font-bold text-green-500 uppercase tracking-widest">Live</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const IntelView = ({ metrics }: { metrics: any }) => (
  <div className="space-y-8">
    <div className="liquid-glass-panel rounded-[2rem] p-8 border border-white/10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h3 className="text-3xl font-bold text-apple-base flex items-center gap-4">
            <Globe className="text-blue-500" size={32} /> Intelligence Center
          </h3>
          <p className="text-apple-muted mt-2">Deep market analysis and territory mapping for the active fleet.</p>
        </div>
        <button className="px-6 py-2.5 bg-blue-500 text-white rounded-2xl text-sm font-bold hover:bg-blue-600 transition-all shadow-lg shadow-blue-500/20">
          Launch Territory Scan
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Market Depth', value: metrics?.totalLeads?.toLocaleString() ?? '0', sub: 'Total Scraped', color: 'blue' },
          { label: 'High Intent', value: metrics?.whaleLeads?.toLocaleString() ?? '0', sub: 'Whales Identified', color: 'orange' },
          { label: 'Est. Leakage', value: metrics?.totalLeakage ? `$${(metrics.totalLeakage / 1000000).toFixed(1)}M` : '$0', sub: 'Annually (Global)', color: 'red' },
          { label: 'Conversion', value: `${(metrics?.replyRate ?? 0).toFixed(1)}%`, sub: 'Avg Reply Rate', color: 'green' },
        ].map((stat, i) => (
          <div key={i} className="p-6 rounded-3xl bg-white/5 border border-white/10 hover:border-white/20 transition-all">
            <div className="text-xs font-bold text-apple-muted uppercase mb-2">{stat.label}</div>
            <div className="text-3xl font-black text-apple-base mb-1">{stat.value}</div>
            <div className={`text-[10px] font-bold text-${stat.color}-500 uppercase`}>{stat.sub}</div>
          </div>
        ))}
      </div>
    </div>

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div className="liquid-glass-panel rounded-[2rem] p-8">
        <h4 className="text-xl font-bold text-apple-base mb-6 flex items-center gap-2">
          <Database size={20} className="text-primary" /> Territory Command
        </h4>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-4 rounded-2xl bg-white/5 border border-white/5">
            <span className="text-sm text-apple-base">Active Databases</span>
            <span className="text-sm font-bold text-primary">Supabase-V2 (Live)</span>
          </div>
          <div className="flex justify-between items-center p-4 rounded-2xl bg-white/5 border border-white/5">
            <span className="text-sm text-apple-base">Deduplication Status</span>
            <span className="text-sm font-bold text-green-500 truncate max-w-[150px]">Synced & Optimized</span>
          </div>
          <div className="flex justify-between items-center p-4 rounded-2xl bg-white/5 border border-white/5">
            <span className="text-sm text-apple-base">Shadow Site Integrity</span>
            <span className="text-sm font-bold text-blue-500">100% Reachable</span>
          </div>
        </div>
      </div>

      <div className="liquid-glass-panel rounded-[2rem] p-8">
        <h4 className="text-xl font-bold text-apple-base mb-6 flex items-center gap-2">
          <Zap size={20} className="text-orange-500" /> Diamond's Intel Feed
        </h4>
        <div className="space-y-3">
          {[
            "Detected 50+ sites with critical Mobile LCP issues in Austin.",
            "Identified 12 attorneys with outdated domain expirations.",
            "High-intent signal: 3 Solar whales visited bridge sites today.",
            "Territory Sync: Los Angeles market depth increased by 12%."
          ].map((msg, i) => (
            <div key={i} className="text-xs text-apple-muted p-3 rounded-xl bg-white/5 border border-white/5 border-l-orange-500/50 border-l-2">
              {msg}
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

export default function App() {
  const [activeTab, setActiveTab] = useState('COMMAND');
  const [searchQuery, setSearchQuery] = useState('');
  
  // LIVE HOOKS
  const { leads, loading: leadsLoading, refetch: refetchLeads } = useLeads();
  const { metrics } = useMetrics();
  const logs = useLogs();
  const agents = useAgents();
  const { tasks, createTask, updateTask, deleteTask } = useTasks();

  const [workers, setWorkers] = useState([
    { id: '1', name: 'Silas', role: 'Outreach & Closing', status: 'LIVE' },
    { id: '2', name: 'Kael', role: 'Lead Scraping', status: 'LIVE' },
    { id: '3', name: 'Diamond', role: 'Technical Intelligence', status: 'LIVE' },
    { id: '4', name: 'Vex', role: 'Shadow Site QA', status: 'LIVE' },
  ]);
  const [sortConfig, setSortConfig] = useState<{ key: SortKey; order: SortOrder }>({
    key: 'opportunityScore',
    order: 'desc'
  });

  const [isDark, setIsDark] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [weather, setWeather] = useState({ code: 0, isDay: 1 });
  const [selectedNiche, setSelectedNiche] = useState<{name: string, value: number, description: string, stats: any[]} | null>(null);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  
  // Scrape Hub State
  const [isScrapeModalOpen, setIsScrapeModalOpen] = useState(false);
  const [scrapeCity, setScrapeCity] = useState<string | null>(null);
  const [scrapeNiche, setScrapeNiche] = useState<string | null>(null);
  const [isScraping, setIsScraping] = useState(false);
  const [scrapeProgress, setScrapeProgress] = useState(0);

  // Audit Surprise State
  const [isAuditModalOpen, setIsAuditModalOpen] = useState(false);
  const [auditPhase, setAuditPhase] = useState<'scanning' | 'complete'>('scanning');

  // New Modals State
  const [isInboxModalOpen, setIsInboxModalOpen] = useState(false);
  const [isTotalLeadsModalOpen, setIsTotalLeadsModalOpen] = useState(false);
  const [selectedInboxLead, setSelectedInboxLead] = useState<Lead | null>(null);
  const [isWarRoomModalOpen, setIsWarRoomModalOpen] = useState(false);
  const [warRoomLeads, setWarRoomLeads] = useState<Lead[]>([]);
  const [inboxMessages, setInboxMessages] = useState<Record<string, {text: string, isUser: boolean, timestamp: string}[]>>({});
  const [replyText, setReplyText] = useState('');

  const handleSendMessage = async () => {
    if (!replyText.trim() || !selectedInboxLead) return;
    
    const leadId = selectedInboxLead.id;
    const msgText = replyText.trim();
    
    // Optimistic UI update
    setInboxMessages(prev => ({
      ...prev,
      [leadId]: [...(prev[leadId] || []), { text: msgText, isUser: true, timestamp: 'Just now' }]
    }));
    setReplyText('');

    try {
      const res = await api.chatWorker(leadId, msgText);
      setInboxMessages(prev => ({
        ...prev,
        [leadId]: [...(prev[leadId] || []), { text: res.response, isUser: false, timestamp: 'Just now' }]
      }));
    } catch (err: any) {
      setInboxMessages(prev => ({
        ...prev,
        [leadId]: [...(prev[leadId] || []), { text: `[System Error]: ${err.message}`, isUser: false, timestamp: 'Just now' }]
      }));
    }
  };

  const nicheDataInfo = {
    'Solar': {
      description: 'Solar panel installers and renewable energy providers with high monthly ad spend.',
      stats: [
        { label: 'Avg Deal', value: '$12k' },
        { label: 'Conversion', value: '14%' },
        { label: 'Active', value: '412' }
      ]
    },
    'Dentist': {
      description: 'Private dental practices and clinics focusing on high-value cosmetic procedures.',
      stats: [
        { label: 'Avg Deal', value: '$8k' },
        { label: 'Conversion', value: '18%' },
        { label: 'Active', value: '385' }
      ]
    },
    'Lawyers': {
      description: 'Personal injury, family law, and corporate attorneys needing better lead intake.',
      stats: [
        { label: 'Avg Deal', value: '$15k' },
        { label: 'Conversion', value: '11%' },
        { label: 'Active', value: '294' }
      ]
    },
    'HVAC': {
      description: 'Heating, ventilation, and air conditioning contractors specializing in emergency repairs.',
      stats: [
        { label: 'Avg Deal', value: '$6k' },
        { label: 'Conversion', value: '22%' },
        { label: 'Active', value: '215' }
      ]
    },
    'Roofing': {
      description: 'Residential and commercial roofing contractors with high seasonal demand.',
      stats: [
        { label: 'Avg Deal', value: '$10k' },
        { label: 'Conversion', value: '9%' },
        { label: 'Active', value: '182' }
      ]
    },
    'Other': {
      description: 'Diverse mix of local businesses across various trades and services.',
      stats: [
        { label: 'Avg Deal', value: '$5k' },
        { label: 'Conversion', value: '10%' },
        { label: 'Active', value: '1600' }
      ]
    }
  };

  useEffect(() => {
    // Fetch user's weather based on geolocation
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          fetch(`https://api.open-meteo.com/v1/forecast?latitude=${pos.coords.latitude}&longitude=${pos.coords.longitude}&current_weather=true`)
            .then(res => res.json())
            .then(data => {
              if (data.current_weather) {
                setWeather({
                  code: data.current_weather.weathercode,
                  isDay: data.current_weather.is_day
                });
                // Auto-set dark mode if it's night time
                if (data.current_weather.is_day === 0) {
                  setIsDark(true);
                }
              }
            })
            .catch(err => console.error("Failed to fetch weather", err));
        },
        () => {
          console.log("Geolocation denied, using default weather.");
        }
      );
    }
  }, []);

  // Stats calculations (Live)
  const totalLeads    = metrics?.totalLeads ?? 0;
  const whaleLeads    = metrics?.whaleLeads ?? 0;
  const totalLeakage  = metrics?.totalLeakage ?? 0;
  const expectedMRR   = metrics?.expectedMRR ?? 0;
  const actualMRR     = metrics?.actualMRR ?? 0;
  const potentialMRR  = metrics?.potentialMRR ?? 0;
  const replyRate     = metrics?.replyRate ?? 0;
  const totalSent     = metrics?.totalSent ?? 0;
  const totalReplies  = metrics?.totalReplies ?? 0;
  const funnelData    = metrics?.funnel ?? [];
  const nicheData     = metrics?.nicheData ?? [];
  const avgScore      = metrics?.avgScore ?? 0;

  // Redundant mock data removed to use live metrics hooks.

  const revenueByNicheData = [
    { name: 'SaaS', revenue: 12500 },
    { name: 'Energy', revenue: 8000 },
    { name: 'Logistics', revenue: 4500 },
    { name: 'Health', revenue: 6000 },
    { name: 'Real Estate', revenue: 3000 },
  ];

  const scoreDistributionData = [
    { range: '0-20', count: 2 },
    { range: '21-40', count: 5 },
    { range: '41-60', count: 12 },
    { range: '61-80', count: 18 },
    { range: '81-100', count: 8 },
  ];

  const COLORS = ['#0066cc', '#34c759', '#ff9500', '#af52de'];

  const [isNewTaskModalOpen, setIsNewTaskModalOpen] = useState(false);
  const [newTaskForm, setNewTaskForm] = useState<Partial<Task>>({
    status: 'Pending',
    assignee: 'Alice',
    dueDate: new Date().toISOString().split('T')[0]
  });



  const handleCreateTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskForm.title || !newTaskForm.leadId) return;
    
    const newTask: Task = {
      id: `t${Date.now()}`,
      leadId: newTaskForm.leadId,
      title: newTaskForm.title,
      description: newTaskForm.description || '',
      status: newTaskForm.status as 'Pending' | 'In Progress' | 'Completed',
      assignee: newTaskForm.assignee || 'Alice',
      dueDate: new Date(newTaskForm.dueDate!).toISOString(),
      createdAt: new Date().toISOString(),
    };
    
    createTask(newTask);
    setIsNewTaskModalOpen(false);
    setNewTaskForm({
      status: 'Pending',
      assignee: 'Alice',
      dueDate: new Date().toISOString().split('T')[0]
    });
  };

  const handleSort = (key: SortKey) => {
    let order: SortOrder = 'desc';
    if (sortConfig.key === key && sortConfig.order === 'desc') {
      order = 'asc';
    } else if (sortConfig.key === key && sortConfig.order === 'asc') {
      order = null;
    }
    setSortConfig({ key, order });
  };

  const getSortedLeads = () => {
    let filtered = leads.filter(l => 
      l.businessName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      l.website.toLowerCase().includes(searchQuery.toLowerCase())
    );

    if (sortConfig.order) {
      filtered = [...filtered].sort((a, b) => {
        const valA = a[sortConfig.key];
        const valB = b[sortConfig.key];
        if (sortConfig.order === 'asc') {
          return valA > valB ? 1 : -1;
        } else {
          return valA < valB ? 1 : -1;
        }
      });
    }
    return filtered;
  };

  const SortIcon = ({ column }: { column: SortKey }) => {
    if (sortConfig.key !== column || !sortConfig.order) return <ArrowUpDown size={12} className="opacity-30" />;
    return sortConfig.order === 'asc' ? <ArrowUp size={12} className="text-primary" /> : <ArrowDown size={12} className="text-primary" />;
  };

  return (
    <div className={cn("h-screen overflow-hidden font-sans transition-colors duration-500 bg-gray-50 dark:bg-zinc-950", isDark ? "dark" : "")}>
      
      {/* Tab Morphing Background */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.img
            key={activeTab}
            src={TAB_BACKGROUNDS[activeTab]}
            initial={{ opacity: 0, scale: 1.05 }}
            animate={{ opacity: isDark ? 0.15 : 0.3, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.5, ease: "easeInOut" }}
            className="absolute inset-0 w-full h-full object-cover"
          />
        </AnimatePresence>
        <div className="absolute inset-0 bg-gray-50/70 dark:bg-zinc-950/70 backdrop-blur-3xl" />
      </div>

      <div className="flex flex-col md:flex-row h-full relative z-10">
        {/* Sidebar */}
        <AnimatePresence initial={false}>
          {isSidebarOpen && (
            <motion.aside 
              initial={{ width: 0, opacity: 0, margin: 0 }}
              animate={{ width: 256, opacity: 1, margin: 16 }}
              exit={{ width: 0, opacity: 0, margin: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="hidden md:flex liquid-glass border-r-0 border-r border-white/20 dark:border-white/10 flex-col relative z-10 rounded-[2rem] overflow-hidden shrink-0"
            >
              <div className="w-64 flex flex-col h-full">
                <div className="py-6 flex items-center justify-center">
                  <img 
                    src={isDark ? "/logo-white.png" : "/logo-black.png"} 
                    alt="RI2CH OS Logo" 
                    className="h-32 w-auto px-6 object-contain transition-all duration-300" 
                  />
                </div>

                <div className="px-4 mb-6">
                  <div className="text-[10px] font-semibold text-apple-muted mb-3 px-3 uppercase tracking-wider whitespace-nowrap">
                    Agent Status
                  </div>
                  <div className="space-y-1">
                    {agents.map((agent) => (
                      <div key={agent.name} className="flex items-center gap-3 px-3 py-2 rounded-xl hover:bg-white/20 dark:hover:bg-black/20 transition-colors group">
                        <div className={cn(
                          "w-2 h-2 rounded-full shrink-0",
                          agent.status === 'LIVE' ? "bg-success shadow-[0_0_8px_rgba(52,199,89,0.5)]" : 
                          agent.status === 'IDLE' ? "bg-warning shadow-[0_0_8px_rgba(255,149,0,0.5)]" : "bg-danger shadow-[0_0_8px_rgba(255,59,48,0.5)]"
                        )} />
                        <span className="text-sm text-apple-base font-medium whitespace-nowrap">{agent.name}</span>
                        <span className={cn(
                          "ml-auto text-[10px] font-medium whitespace-nowrap",
                          agent.status === 'LIVE' ? "text-success" : 
                          agent.status === 'IDLE' ? "text-warning" : "text-danger"
                        )}>
                          {agent.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <nav className="flex-1 px-4 space-y-1 overflow-y-auto">
                  {TABS.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={cn(
                        "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                        activeTab === tab.id 
                          ? "bg-white/40 dark:bg-black/40 text-apple-base shadow-sm" 
                          : "text-apple-muted hover:bg-white/20 dark:hover:bg-black/20 hover:text-apple-base"
                      )}
                    >
                      <tab.icon size={18} className={cn("shrink-0", activeTab === tab.id ? "text-apple-base" : "text-apple-muted")} />
                      <span className="whitespace-nowrap">{tab.label}</span>
                    </button>
                  ))}
                </nav>

                <div className="p-6 space-y-3">
                  <div 
                    className="p-4 bg-white/20 dark:bg-black/20 rounded-2xl cursor-pointer hover:bg-white/30 dark:hover:bg-black/30 transition-colors"
                    onClick={() => setIsTotalLeadsModalOpen(true)}
                  >
                    <div className="text-[10px] font-semibold text-apple-muted mb-1 uppercase tracking-wider whitespace-nowrap">Total Leads</div>
                    <div className="flex items-center justify-between">
                       <div className="text-2xl font-light tracking-tight text-apple-base">{totalLeads.toLocaleString()}</div>
                       <ChevronRight size={14} className="text-apple-muted" />
                    </div>
                  </div>
                  <div className="p-4 bg-white/20 dark:bg-black/20 rounded-2xl">
                    <div className="text-[10px] font-semibold text-apple-muted mb-1 uppercase tracking-wider whitespace-nowrap">Whales (75+)</div>
                    <div className="text-2xl font-light tracking-tight text-apple-base">{whaleLeads}</div>
                  </div>
                  <button className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium text-apple-muted hover:bg-white/20 dark:hover:bg-black/20 hover:text-apple-base transition-all">
                    <LogOut size={16} className="shrink-0" />
                    <span className="whitespace-nowrap">Sign Out</span>
                  </button>
                </div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Mobile Bottom Nav */}
        <div className="md:hidden fixed bottom-0 left-0 right-0 z-50 liquid-glass border-t border-white/20 dark:border-white/10 p-2 pb-safe flex justify-around items-center rounded-t-[2rem] backdrop-blur-xl">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex flex-col items-center gap-1 p-2 rounded-xl transition-all",
                activeTab === tab.id ? "text-apple-base scale-110" : "text-apple-muted hover:text-apple-base"
              )}
            >
              <tab.icon size={20} />
              <span className="text-[10px] font-medium">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Main Content */}
        <main className="flex-1 p-4 md:p-8 overflow-y-auto pb-24 md:pb-8 w-full">
          {/* Header Controls */}
          <div className="flex justify-between items-center mb-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="hidden md:flex liquid-glass-button p-3 rounded-full text-apple-base"
            >
              {isSidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
            </button>
            <div className="flex justify-end flex-1">
              <button 
                onClick={() => setIsDark(!isDark)}
                className="liquid-glass-button p-3 rounded-full text-apple-base"
              >
                {isDark ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            </div>
          </div>

          <AnimatePresence mode="wait">
            {activeTab === 'COMMAND' && (
              <motion.div
                key="command"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="max-w-6xl mx-auto"
              >
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h1 className="text-3xl font-semibold tracking-tight text-apple-base">Dashboard</h1>
                    <p className="text-sm text-apple-muted mt-1">Overview of your agency's performance.</p>
                  </div>
                  <div className="text-sm text-apple-muted font-medium">
                    {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                  <MetricCard 
                    label="Total Leads" 
                    value={totalLeads.toLocaleString()} 
                    sub="Scraped this session"
                    change={`+${whaleLeads} whales`}
                    details={{
                      title: "Total Leads",
                      subtitle: "Full breakdown of your scraped lead pool",
                      stats: [
                        { label: "Total", value: totalLeads.toString() },
                        { label: "Whales 75+", value: whaleLeads.toString() },
                        { label: "High Ticket", value: leads.filter(l => l.opportunityScore >= 60).length.toString() }
                      ],
                      rows: [
                        { label: "New (uncontacted)", value: leads.filter(l => l.status === 'New').length.toString() },
                        { label: "Contacted", value: leads.filter(l => l.status === 'Contacted').length.toString() },
                        { label: "Replied", value: totalReplies.toString() },
                        { label: "Avg Opportunity Score", value: `${avgScore.toFixed(1)}/100` }
                      ]
                    }}
                  />
                  <MetricCard 
                    label="Expected MRR" 
                    value={`$${actualMRR.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} 
                    sub="Gross Revenue Confirmed"
                    details={{
                      title: "Revenue Pipeline",
                      subtitle: "MRR breakdown across pipeline stages",
                      stats: [
                        { label: "Actual MRR", value: `$${actualMRR.toLocaleString()}` },
                        { label: "Potential", value: `$${potentialMRR.toLocaleString()}` },
                        { label: "Pipeline", value: `$${(expectedMRR - actualMRR - potentialMRR).toLocaleString()}` }
                      ],
                      rows: [
                        { label: "Closed deals", value: `$${actualMRR.toLocaleString()}/mo` },
                        { label: "Replied + Demo Sent", value: `$${potentialMRR.toLocaleString()}/mo` },
                        { label: "Annual run rate", value: `$${(expectedMRR * 12).toLocaleString()}/yr` }
                      ]
                    }}
                  />
                  <MetricCard 
                    label="Reply Rate" 
                    value={`${replyRate.toFixed(1)}%`} 
                    sub={`${totalReplies} of ${totalSent} contacted`}
                    details={{
                      title: "Outreach Performance",
                      subtitle: "Reply rate and engagement funnel",
                      stats: [
                        { label: "Emails Sent", value: totalSent.toString() },
                        { label: "Replies", value: totalReplies.toString() },
                        { label: "Hot Leads", value: leads.filter(l => l.replyStatus === 'positive').length.toString() }
                      ],
                      rows: [
                        { label: "Reply rate", value: `${replyRate.toFixed(1)}%` },
                        { label: "Conversion to hot", value: `${((leads.filter(l => l.replyStatus === 'positive').length / totalReplies) * 100).toFixed(1)}%` }
                      ]
                    }}
                  />
                  <MetricCard 
                    label="Revenue Leakage" 
                    value={`$${(totalLeakage / 1000000).toFixed(1)}M`} 
                    sub="Monthly lost across all leads"
                    details={{
                      title: "Revenue Leakage Analysis",
                      subtitle: "What your leads are losing monthly to bad websites",
                      stats: [
                        { label: "Monthly", value: `$${(totalLeakage / 1000000).toFixed(1)}M` },
                        { label: "Annual", value: `$${(totalLeakage * 12 / 1000000).toFixed(0)}M` },
                        { label: "Per Lead", value: `$${(totalLeakage / totalLeads).toLocaleString(undefined, { maximumFractionDigits: 0 })}` }
                      ],
                      rows: [
                        { label: "Total monthly leakage", value: `$${totalLeakage.toLocaleString(undefined, { maximumFractionDigits: 0 })}` },
                        { label: "Potential annual revenue", value: `$${(totalLeakage * 12 * 0.25 / 1000000).toFixed(0)}M` }
                      ]
                    }}
                  />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                  <div className="lg:col-span-2 liquid-glass rounded-3xl p-6 h-[350px]">
                    <div className="text-sm font-semibold text-apple-base mb-6">Conversion Funnel</div>
                    <div className="h-full w-full pb-8">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={funnelData}>
                          <CartesianGrid strokeDasharray="3 3" stroke={isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)"} vertical={false} />
                          <XAxis 
                            dataKey="name" 
                            axisLine={false} 
                            tickLine={false} 
                            tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12, fontWeight: 500 }}
                            dy={10}
                          />
                          <YAxis hide />
                          <Tooltip 
                            cursor={{ fill: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)' }}
                            contentStyle={{ backgroundColor: isDark ? 'rgba(0,0,0,0.8)' : 'rgba(255,255,255,0.8)', backdropFilter: 'blur(12px)', border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)', borderRadius: '16px', boxShadow: '0 4px 24px rgba(0,0,0,0.1)' }}
                            itemStyle={{ color: isDark ? '#fff' : '#000', fontSize: '14px', fontWeight: '500' }}
                          />
                          <Bar dataKey="count" fill={isDark ? "rgba(255,255,255,0.8)" : "rgba(0,0,0,0.8)"} radius={[6, 6, 0, 0]} barSize={48} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  <div className="liquid-glass rounded-3xl p-6 h-[350px]">
                    <div className="text-sm font-semibold text-apple-base mb-2">Niche Distribution</div>
                    <div className="h-full w-full flex items-center justify-center pb-8">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={nicheData}
                            cx="50%"
                            cy="50%"
                            innerRadius={70}
                            outerRadius={90}
                            paddingAngle={2}
                            dataKey="value"
                            stroke="none"
                            onClick={(data) => {
                               const info = nicheDataInfo[data.name as keyof typeof nicheDataInfo] || nicheDataInfo['Other'];
                               setSelectedNiche({ ...data, ...info });
                             }}
                          >
                            {nicheData.map((entry, index) => (
                              <Cell 
                                key={`cell-${index}`} 
                                fill={COLORS[index % COLORS.length]} 
                                className="cursor-pointer hover:opacity-80 transition-opacity outline-none"
                              />
                            ))}
                          </Pie>
                          <Tooltip 
                            contentStyle={{ backgroundColor: isDark ? 'rgba(0,0,0,0.8)' : 'rgba(255,255,255,0.8)', backdropFilter: 'blur(12px)', border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)', borderRadius: '16px', boxShadow: '0 4px 24px rgba(0,0,0,0.1)' }}
                            itemStyle={{ color: isDark ? '#fff' : '#000', fontSize: '14px', fontWeight: '500' }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                  <div className="liquid-glass rounded-3xl p-6 h-[350px]">
                    <div className="text-sm font-semibold text-apple-base mb-6">Revenue Potential by Niche</div>
                    <div className="h-full w-full pb-8">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={revenueByNicheData}>
                          <defs>
                            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#34c759" stopOpacity={0.3}/>
                              <stop offset="95%" stopColor="#34c759" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke={isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)"} vertical={false} />
                          <XAxis 
                            dataKey="name" 
                            axisLine={false} 
                            tickLine={false} 
                            tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12, fontWeight: 500 }}
                            dy={10}
                          />
                          <YAxis hide />
                          <Tooltip 
                            cursor={{ stroke: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)', strokeWidth: 2 }}
                            contentStyle={{ backgroundColor: isDark ? 'rgba(0,0,0,0.8)' : 'rgba(255,255,255,0.8)', backdropFilter: 'blur(12px)', border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)', borderRadius: '16px', boxShadow: '0 4px 24px rgba(0,0,0,0.1)' }}
                            itemStyle={{ color: isDark ? '#fff' : '#000', fontSize: '14px', fontWeight: '500' }}
                            formatter={(value: number) => {
                              const total = revenueByNicheData.reduce((acc, curr) => acc + curr.revenue, 0);
                              const percentage = ((value / total) * 100).toFixed(1);
                              return [`$${value.toLocaleString()} (${percentage}%)`, 'Revenue'];
                            }}
                          />
                          <Area type="monotone" dataKey="revenue" stroke="#34c759" strokeWidth={3} fillOpacity={1} fill="url(#colorRevenue)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="liquid-glass rounded-3xl p-6 h-[350px]">
                    <div className="text-sm font-semibold text-apple-base mb-6">Lead Opportunity Score Distribution</div>
                    <div className="h-full w-full pb-8">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={scoreDistributionData}>
                          <CartesianGrid strokeDasharray="3 3" stroke={isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)"} vertical={false} />
                          <XAxis 
                            dataKey="range" 
                            axisLine={false} 
                            tickLine={false} 
                            tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12, fontWeight: 500 }}
                            dy={10}
                          />
                          <YAxis hide />
                          <Tooltip 
                            cursor={{ stroke: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)', strokeWidth: 2 }}
                            contentStyle={{ backgroundColor: isDark ? 'rgba(0,0,0,0.8)' : 'rgba(255,255,255,0.8)', backdropFilter: 'blur(12px)', border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)', borderRadius: '16px', boxShadow: '0 4px 24px rgba(0,0,0,0.1)' }}
                            itemStyle={{ color: isDark ? '#fff' : '#000', fontSize: '14px', fontWeight: '500' }}
                            formatter={(value: number) => [value, 'Leads']}
                          />
                          <Line type="monotone" dataKey="count" stroke="#0066cc" strokeWidth={3} dot={{ r: 4, fill: '#0066cc', strokeWidth: 2, stroke: isDark ? '#000' : '#fff' }} activeDot={{ r: 6, strokeWidth: 0 }} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                <div className="mb-8">
                  <div className="text-sm font-semibold text-apple-base mb-4">Quick Actions</div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <button 
                      onClick={() => setIsScrapeModalOpen(true)}
                      className="liquid-glass-button py-3.5 rounded-2xl text-sm font-medium text-apple-base flex items-center justify-center gap-2"
                    >
                      <Target size={16} />
                      Launch Scrape Hub
                    </button>
                    <button 
                      onClick={() => {
                        setIsAuditModalOpen(true);
                        setAuditPhase('scanning');
                        setTimeout(() => setAuditPhase('complete'), 3500);
                      }}
                      className="liquid-glass-button py-3.5 rounded-2xl text-sm font-medium text-apple-base flex items-center justify-center gap-2"
                    >
                      <Radar size={16} />
                      Audit Pending Leads
                    </button>
                    <button 
                      onClick={() => setIsInboxModalOpen(true)}
                      className="liquid-glass-button py-3.5 rounded-2xl text-sm font-medium text-apple-base"
                    >
                      Inbox & Nurture
                    </button>
                    <button 
                      onClick={() => setIsWarRoomModalOpen(true)}
                      className="bg-[#ffcc00] text-black py-3.5 rounded-2xl text-sm font-bold hover:bg-[#e6b800] transition-colors shadow-lg"
                    >
                      War Room: {warRoomLeads.length} Pinned
                    </button>
                  </div>
                </div>

                <div>
                  <div className="text-sm font-semibold text-apple-base mb-4">System Log</div>
                  <div className="liquid-glass rounded-3xl p-6 font-mono text-xs text-apple-muted h-48 overflow-y-auto space-y-2">
                    {logs.map((log, i) => (
                      <div key={i} className="flex gap-4">
                        <span className="opacity-60">[{log.timestamp}]</span>
                        <span className="text-apple-base">{log.message}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'PIPELINE' && (
              <motion.div
                key="pipeline"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="max-w-6xl mx-auto"
              >
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h1 className="text-3xl font-semibold tracking-tight text-apple-base">Pipeline</h1>
                    <p className="text-sm text-apple-muted mt-1">Manage and track your leads.</p>
                  </div>
                </div>

                <div className="flex flex-col md:flex-row gap-4 mb-6">
                  <div className="flex-1 relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-apple-muted" size={18} />
                    <input 
                      type="text" 
                      placeholder="Search by domain or business name..."
                      className="w-full liquid-glass rounded-2xl py-3 pl-11 pr-4 text-sm text-apple-base placeholder:text-apple-muted focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>
                  <select className="liquid-glass rounded-2xl px-4 py-3 text-sm text-apple-base focus:outline-none focus:ring-2 focus:ring-white/50 transition-all appearance-none">
                    <option className="text-black">All Statuses</option>
                    <option className="text-black">New</option>
                    <option className="text-black">High Intel Ready</option>
                    <option className="text-black">Contacted</option>
                    <option className="text-black">Replied</option>
                  </select>
                </div>

                {/* Sortable Headers */}
                <div className="flex items-center justify-between px-6 mb-2 text-xs font-medium text-apple-muted">
                  <div className="flex-1">Lead Details</div>
                  <div className="flex items-center gap-8">
                    <button 
                      onClick={() => handleSort('monthlyValue')}
                      className="flex items-center gap-1.5 hover:text-apple-base transition-colors"
                    >
                      Monthly Value <SortIcon column="monthlyValue" />
                    </button>
                    <button 
                      onClick={() => handleSort('revenueLoss')}
                      className="flex items-center gap-1.5 hover:text-apple-base transition-colors"
                    >
                      Revenue Loss <SortIcon column="revenueLoss" />
                    </button>
                    <button 
                      onClick={() => handleSort('opportunityScore')}
                      className="flex items-center gap-1.5 hover:text-apple-base transition-colors"
                    >
                      Score <SortIcon column="opportunityScore" />
                    </button>
                    <div className="w-8" /> {/* Spacer for chevron */}
                  </div>
                </div>

                <div className="space-y-3">
                  {getSortedLeads().map((lead) => (
                    <motion.div 
                      layout
                      key={lead.id}
                      onClick={() => setSelectedLead(lead)}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="liquid-glass rounded-2xl p-4 flex items-center justify-between hover:bg-white/50 dark:hover:bg-black/50 transition-all cursor-pointer group"
                    >
                      <div className="flex items-center gap-4">
                        <div className={cn(
                          "badge",
                          lead.status === 'New' ? "badge-new" :
                          lead.status === 'Replied' ? "badge-replied" :
                          lead.status === 'Contacted' ? "badge-sent" : "badge-hot"
                        )}>
                          {lead.status}
                        </div>
                        <div>
                          <div className="text-sm font-semibold text-apple-base">{lead.website.replace('https://', '')}</div>
                          <div className="text-xs text-apple-muted mt-0.5">
                            {lead.niche} • {lead.city}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-10">
                        <div className="text-right hidden lg:block w-24">
                          <div className="text-sm font-medium text-apple-base">${lead.monthlyValue.toLocaleString()}/mo</div>
                        </div>
                        <div className="text-right hidden md:block w-24">
                          <div className="text-sm font-medium text-apple-base">${lead.revenueLoss.toLocaleString()}/mo</div>
                        </div>
                        <div className="text-right w-16">
                          <div className="text-xl font-semibold tracking-tight text-apple-base">{lead.opportunityScore}</div>
                        </div>
                        <button className="p-2 rounded-full text-apple-muted group-hover:bg-white/20 dark:group-hover:bg-black/20 group-hover:text-apple-base transition-all">
                          <ChevronRight size={18} />
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'TASKS' && (
              <motion.div
                key="tasks"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="max-w-6xl mx-auto"
              >
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h1 className="text-3xl font-semibold tracking-tight text-apple-base">Tasks</h1>
                    <p className="text-apple-muted mt-1">Manage follow-ups and action items</p>
                  </div>
                  <button 
                    onClick={() => setIsNewTaskModalOpen(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-apple-base text-white dark:text-black rounded-full font-medium hover:opacity-90 transition-opacity"
                  >
                    <Plus size={18} />
                    New Task
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {['Pending', 'In Progress', 'Completed'].map(status => (
                    <div key={status} className="liquid-glass rounded-3xl p-6">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="font-semibold text-apple-base">{status}</h3>
                        <span className="px-2.5 py-1 rounded-full bg-white/20 dark:bg-black/20 text-xs font-medium text-apple-base">
                          {tasks.filter(t => t.status === status).length}
                        </span>
                      </div>
                      <div className="space-y-4">
                        {tasks.filter(t => t.status === status).map(task => {
                          const lead = leads.find(l => l.id === task.leadId);
                          return (
                            <div key={task.id} className="p-4 rounded-2xl bg-white/40 dark:bg-black/40 border border-white/20 dark:border-white/10 hover:bg-white/60 dark:hover:bg-black/60 transition-colors cursor-pointer group">
                              <div className="flex items-start justify-between mb-2">
                                <h4 className="font-medium text-apple-base text-sm">{task.title}</h4>
                                <button 
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    deleteTask(task.id);
                                  }}
                                  className="opacity-0 group-hover:opacity-100 transition-opacity text-apple-muted hover:text-red-500"
                                >
                                  <Trash2 size={14} />
                                </button>
                              </div>
                              <p className="text-xs text-apple-muted mb-3 line-clamp-2">{task.description}</p>
                              {lead && (
                                <div className="flex items-center gap-2 mb-3">
                                  <div className="w-5 h-5 rounded-full bg-apple-base/10 flex items-center justify-center">
                                    <Target size={10} className="text-apple-base" />
                                  </div>
                                  <span className="text-xs font-medium text-apple-base">{lead.businessName}</span>
                                </div>
                              )}
                              <div className="flex items-center justify-between text-[10px] text-apple-muted pt-3 border-t border-black/5 dark:border-white/5">
                                <div className="flex items-center gap-3">
                                  <div className="flex items-center gap-1.5">
                                    <Calendar size={12} />
                                    <span>{new Date(task.dueDate).toLocaleDateString()}</span>
                                  </div>
                                  <div className="flex items-center gap-1.5">
                                    <User size={12} />
                                    <span>{task.assignee}</span>
                                  </div>
                                </div>
                                <select
                                  value={task.status}
                                  onChange={(e) => {
                                    e.stopPropagation();
                                    updateTask(task.id, { status: e.target.value as Task['status'] });
                                  }}
                                  className="bg-transparent border-none outline-none text-apple-base font-medium cursor-pointer"
                                >
                                  <option value="Pending">Pending</option>
                                  <option value="In Progress">In Progress</option>
                                  <option value="Completed">Completed</option>
                                </select>
                              </div>
                            </div>
                          );
                        })}
                        {tasks.filter(t => t.status === status).length === 0 && (
                          <div className="text-center py-8 text-apple-muted text-sm border-2 border-dashed border-black/5 dark:border-white/5 rounded-2xl">
                            No tasks
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'SHOWCASE' && (
              <motion.div
                key="showcase"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="max-w-6xl mx-auto"
              >
                <AiImageGenerator />
              </motion.div>
            )}

            {activeTab === 'INTEL' && (
              <motion.div
                key="intel"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                className="max-w-6xl mx-auto"
              >
                <IntelView metrics={metrics} />
              </motion.div>
            )}

            {activeTab === 'GOD VIEW' && (
              <motion.div
                key="godview"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="max-w-7xl mx-auto"
              >
                <GodView />
              </motion.div>
            )}

            {activeTab === 'CONFIG' && (
              <motion.div
                key="config"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="max-w-4xl mx-auto"
              >
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h1 className="text-3xl font-semibold tracking-tight text-apple-base">Settings</h1>
                    <p className="text-sm text-apple-muted mt-1">Manage your agency configuration and AI workers.</p>
                  </div>
                </div>

                <div className="liquid-glass-panel rounded-[2rem] p-8">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold tracking-tight text-apple-base">AI Workers</h2>
                    <button 
                      onClick={() => setWorkers([...workers, { id: Date.now().toString(), name: 'New AI Agent', role: 'General', status: 'IDLE' }])}
                      className="px-4 py-2 rounded-full liquid-glass-button text-sm font-medium text-apple-base flex items-center gap-2 hover:bg-white/10 dark:hover:bg-black/10 transition-colors"
                    >
                      <Plus size={16} /> Add Worker
                    </button>
                  </div>
                  <div className="space-y-4">
                    {workers.map(worker => (
                      <div key={worker.id} className="flex items-center justify-between p-4 bg-white/10 dark:bg-black/10 rounded-2xl group">
                        <div className="flex items-center gap-4">
                          <div className={cn(
                            "w-3 h-3 rounded-full",
                            worker.status === 'LIVE' ? "bg-success shadow-[0_0_8px_rgba(52,199,89,0.5)]" : "bg-warning shadow-[0_0_8px_rgba(255,149,0,0.5)]"
                          )} />
                          <div>
                            <input
                              type="text"
                              value={worker.name}
                              onChange={(e) => setWorkers(workers.map(w => w.id === worker.id ? { ...w, name: e.target.value } : w))}
                              className="bg-transparent border-b border-transparent hover:border-white/20 focus:border-primary focus:outline-none text-apple-base font-medium transition-colors"
                            />
                            <div className="flex items-center gap-2 mt-1">
                              <select
                                value={worker.role}
                                onChange={(e) => setWorkers(workers.map(w => w.id === worker.id ? { ...w, role: e.target.value } : w))}
                                className="bg-transparent text-xs text-apple-muted focus:outline-none cursor-pointer hover:text-apple-base transition-colors"
                              >
                                <option value="Lead Scraping">Lead Scraping</option>
                                <option value="Outreach & Closing">Outreach & Closing</option>
                                <option value="Technical Intelligence">Technical Intelligence</option>
                                <option value="Shadow Site QA">Shadow Site QA</option>
                                <option value="General">General</option>
                              </select>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <select
                            value={worker.status}
                            onChange={(e) => setWorkers(workers.map(w => w.id === worker.id ? { ...w, status: e.target.value } : w))}
                            className="text-sm font-medium text-apple-muted bg-white/5 dark:bg-black/5 px-3 py-1 rounded-full focus:outline-none cursor-pointer appearance-none text-center"
                          >
                            <option value="LIVE">LIVE</option>
                            <option value="IDLE">IDLE</option>
                            <option value="OFFLINE">OFFLINE</option>
                          </select>
                          <button 
                            onClick={() => setWorkers(workers.filter(w => w.id !== worker.id))}
                            className="p-2 rounded-full hover:bg-white/10 dark:hover:bg-black/10 text-apple-muted hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                            title="Remove Worker"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Niche Details Modal */}
          <AnimatePresence>
            {selectedNiche && (
              <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setSelectedNiche(null)}
                  className="absolute inset-0 bg-black/20 dark:bg-black/40 backdrop-blur-sm"
                />
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 20 }}
                  className="relative w-full max-w-lg liquid-glass-panel rounded-[2rem] overflow-hidden"
                >
                  <button
                    onClick={() => setSelectedNiche(null)}
                    className="absolute top-6 right-6 w-8 h-8 rounded-full liquid-glass-button flex items-center justify-center text-apple-muted transition-all"
                  >
                    <X size={16} />
                  </button>

                  <div className="p-10">
                    <div className="flex items-center gap-4 mb-4">
                      <div 
                        className="w-4 h-4 rounded-full shadow-sm" 
                        style={{ backgroundColor: COLORS[nicheData.findIndex(n => n.name === selectedNiche.name) % COLORS.length] }}
                      />
                      <h3 className="text-2xl font-semibold tracking-tight text-apple-base">
                        {selectedNiche.name} Niche
                      </h3>
                    </div>
                    
                    <p className="text-sm text-apple-muted mb-8 leading-relaxed">
                      {selectedNiche.description}
                    </p>

                    <div className="grid grid-cols-3 gap-px bg-white/20 dark:bg-black/20 rounded-2xl overflow-hidden backdrop-blur-md">
                      {selectedNiche.stats.map((stat, i) => (
                        <div key={i} className="bg-white/30 dark:bg-black/30 p-4 text-center">
                          <div className="text-xl font-light tracking-tight text-apple-base mb-1">
                            {stat.value}
                          </div>
                          <div className="text-[10px] font-medium text-apple-muted uppercase tracking-wider">
                            {stat.label}
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    <div className="mt-8 pt-6 border-t border-white/20 dark:border-white/10">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-apple-muted">Total Distribution</span>
                        <span className="text-lg font-medium text-apple-base">{selectedNiche.value}%</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>

          {/* Lead Details Modal */}
          <AnimatePresence>
            {selectedLead && (
              <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setSelectedLead(null)}
                  className="absolute inset-0 bg-black/20 dark:bg-black/40 backdrop-blur-sm"
                />
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 20 }}
                  className="relative w-full max-w-2xl liquid-glass-panel rounded-[2rem] overflow-hidden"
                >
                  <button
                    onClick={() => setSelectedLead(null)}
                    className="absolute top-6 right-6 w-8 h-8 rounded-full liquid-glass-button flex items-center justify-center text-apple-muted transition-all z-10"
                  >
                    <X size={16} />
                  </button>

                  <div className="p-10">
                    <div className="flex items-start justify-between mb-8">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-2xl font-semibold tracking-tight text-apple-base">
                            {selectedLead.businessName}
                          </h3>
                          <div className={cn(
                            "badge",
                            selectedLead.status === 'New' ? "badge-new" :
                            selectedLead.status === 'Replied' ? "badge-replied" :
                            selectedLead.status === 'Contacted' ? "badge-sent" : "badge-hot"
                          )}>
                            {selectedLead.status}
                          </div>
                        </div>
                        {selectedLead.demoLink && selectedLead.demoLink !== "https://ri2ch.agency/demo-portfolio" ? (
                          <a 
                            href={selectedLead.demoLink} 
                            target="_blank" 
                            rel="noreferrer" 
                            className="text-sm text-primary hover:underline flex items-center gap-1"
                          >
                            View Shadow Site <Globe size={12} />
                          </a>
                        ) : (
                          <span className="text-sm text-apple-muted flex items-center gap-1 cursor-not-allowed" title="Shadow site is currently pending generation">
                            Pending Shadow Site <Globe size={12} className="opacity-50" />
                          </span>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-semibold tracking-tight text-apple-base">{selectedLead.opportunityScore}</div>
                        <div className="text-[10px] font-medium text-apple-muted uppercase tracking-wider">Opp Score</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-8">
                      <div className="liquid-glass rounded-2xl p-5">
                        <div className="text-[10px] font-medium text-apple-muted uppercase tracking-wider mb-1">Monthly Value</div>
                        <div className="text-2xl font-light text-apple-base">${selectedLead.monthlyValue.toLocaleString()}</div>
                      </div>
                      <div className="liquid-glass rounded-2xl p-5">
                        <div className="text-[10px] font-medium text-apple-muted uppercase tracking-wider mb-1">Revenue Loss</div>
                        <div className="text-2xl font-light text-danger">${selectedLead.revenueLoss.toLocaleString()}</div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="flex items-center gap-3 text-sm text-apple-base">
                        <MapPin size={16} className="text-apple-muted" />
                        {selectedLead.city}
                      </div>
                      <div className="flex items-center gap-3 text-sm text-apple-base">
                        <Target size={16} className="text-apple-muted" />
                        {selectedLead.niche}
                      </div>
                      {selectedLead.contactEmail && (
                        <div className="flex items-center gap-3 text-sm text-apple-base">
                          <LogOut size={16} className="text-apple-muted" />
                          {selectedLead.contactEmail}
                        </div>
                      )}
                    </div>

                    <div className="mt-8 pt-6 border-t border-white/20 dark:border-white/10 grid grid-cols-2 gap-3">
                      <button 
                        onClick={() => api.fireSilas(selectedLead.id).then(() => {
                          setSelectedLead(prev => prev ? {...prev, status: 'Contacted'} : null);
                          refetchLeads();
                        })}
                        className="bg-apple-base text-bg dark:bg-white dark:text-black py-3 rounded-xl text-sm font-medium hover:opacity-90 transition-all shadow-lg flex items-center justify-center gap-2"
                      >
                        <Rocket size={16} />
                        Fire Silas 📧
                      </button>
                      
                      {selectedLead.websiteRoast && (
                        <button 
                          onClick={() => {
                            const data = JSON.parse(selectedLead.websiteRoast || '{}');
                            if (data.diamond_audit_url) window.open(data.diamond_audit_url, '_blank');
                          }}
                          className="liquid-glass-button py-3 rounded-xl text-sm font-medium text-apple-base flex items-center justify-center gap-2"
                        >
                          <Stars size={16} />
                          Open Audit
                        </button>
                      )}
                      
                      <button 
                        onClick={() => {
                           if (!warRoomLeads.find(l => l.id === selectedLead.id)) {
                             setWarRoomLeads(prev => [...prev, selectedLead]);
                             alert("Lead added to War Room!");
                           } else {
                             alert("Lead is already in the War Room.");
                           }
                        }}
                        className="col-span-2 bg-[#ffcc00] text-black py-3 rounded-xl text-sm font-semibold hover:bg-[#e6b800] transition-colors shadow-lg flex items-center justify-center gap-2"
                      >
                        <Target size={16} />
                        Add to War Room
                      </button>

                      <button 
                        onClick={() => api.generateSite(selectedLead).then(() => alert("Generation Started"))}
                        disabled={selectedLead.status === 'Contacted'}
                        className={cn("col-span-2 py-3 rounded-xl text-sm font-medium transition-all", selectedLead.status === 'Contacted' ? "bg-white/5 dark:bg-black/5 text-apple-muted cursor-not-allowed" : "liquid-glass-button text-apple-base")}
                      >
                        {selectedLead.status === 'Contacted' ? "Cannot Re-Generate (Already Contacted)" : "Re-Generate Shadow Site"}
                      </button>
                    </div>
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>

          {/* New Task Modal */}
          <AnimatePresence>
            {isNewTaskModalOpen && (
              <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setIsNewTaskModalOpen(false)}
                  className="absolute inset-0 bg-black/20 dark:bg-black/40 backdrop-blur-sm"
                />
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 20 }}
                  className="relative w-full max-w-md bg-white/80 dark:bg-black/80 backdrop-blur-xl border border-white/20 dark:border-white/10 rounded-3xl shadow-2xl overflow-hidden"
                >
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-xl font-semibold text-apple-base">New Task</h2>
                      <button 
                        onClick={() => setIsNewTaskModalOpen(false)}
                        className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 text-apple-muted transition-colors"
                      >
                        <X size={20} />
                      </button>
                    </div>

                    <form onSubmit={handleCreateTask} className="space-y-4">
                      <div>
                        <label className="block text-xs font-medium text-apple-muted mb-1.5">Task Title</label>
                        <input 
                          type="text" 
                          required
                          value={newTaskForm.title || ''}
                          onChange={e => setNewTaskForm({...newTaskForm, title: e.target.value})}
                          className="w-full bg-white/50 dark:bg-black/50 border border-black/10 dark:border-white/10 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-apple-base transition-colors"
                          placeholder="e.g. Follow up on proposal"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-apple-muted mb-1.5">Related Lead</label>
                        <select 
                          required
                          value={newTaskForm.leadId || ''}
                          onChange={e => setNewTaskForm({...newTaskForm, leadId: e.target.value})}
                          className="w-full bg-white/50 dark:bg-black/50 border border-black/10 dark:border-white/10 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-apple-base transition-colors appearance-none"
                        >
                          <option value="">Select a lead...</option>
                          {leads.map(lead => (
                            <option key={lead.id} value={lead.id}>{lead.businessName}</option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-apple-muted mb-1.5">Description (Optional)</label>
                        <textarea 
                          value={newTaskForm.description || ''}
                          onChange={e => setNewTaskForm({...newTaskForm, description: e.target.value})}
                          className="w-full bg-white/50 dark:bg-black/50 border border-black/10 dark:border-white/10 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-apple-base transition-colors resize-none h-24"
                          placeholder="Add any additional details..."
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-xs font-medium text-apple-muted mb-1.5">Due Date</label>
                          <input 
                            type="date" 
                            required
                            value={newTaskForm.dueDate || ''}
                            onChange={e => setNewTaskForm({...newTaskForm, dueDate: e.target.value})}
                            className="w-full bg-white/50 dark:bg-black/50 border border-black/10 dark:border-white/10 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-apple-base transition-colors"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-apple-muted mb-1.5">Assignee</label>
                          <select 
                            value={newTaskForm.assignee || ''}
                            onChange={e => setNewTaskForm({...newTaskForm, assignee: e.target.value})}
                            className="w-full bg-white/50 dark:bg-black/50 border border-black/10 dark:border-white/10 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-apple-base transition-colors appearance-none"
                          >
                            <option value="Alice">Alice</option>
                            <option value="Bob">Bob</option>
                            <option value="Charlie">Charlie</option>
                          </select>
                        </div>
                      </div>

                      <div className="pt-4">
                        <button 
                          type="submit"
                          className="w-full py-3 bg-apple-base text-white dark:text-black rounded-xl font-medium hover:opacity-90 transition-opacity"
                        >
                          Create Task
                        </button>
                      </div>
                    </form>
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>

          {/* Scrape Hub Modal */}
          <AnimatePresence>
            {isScrapeModalOpen && (
              <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => {
                    setIsScrapeModalOpen(false);
                    setIsScraping(false);
                  }}
                  className="absolute inset-0 bg-black/20 dark:bg-black/40 backdrop-blur-sm"
                />
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 20 }}
                  className="relative w-full max-w-3xl liquid-glass-panel rounded-[2rem] overflow-hidden flex flex-col max-h-[80vh]"
                >
                  <div className="p-8 border-b border-white/20 dark:border-white/10 flex justify-between items-center shrink-0">
                    <div>
                      <h3 className="text-2xl font-semibold tracking-tight text-apple-base">Scrape Hub</h3>
                      <p className="text-sm text-apple-muted mt-1">Target new markets and extract high-value leads.</p>
                    </div>
                    <button
                      onClick={() => {
                        setIsScrapeModalOpen(false);
                        setIsScraping(false);
                      }}
                      className="w-8 h-8 rounded-full liquid-glass-button flex items-center justify-center text-apple-muted transition-all"
                    >
                      <X size={16} />
                    </button>
                  </div>

                  <div className="p-8 overflow-y-auto flex-1">
                    {!isScraping ? (
                      <div className="space-y-8">
                        <div>
                          <label className="text-sm font-medium text-apple-base mb-3 block">1. Select Target City</label>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            {['New York', 'London', 'Dubai', 'Tokyo', 'Austin', 'Miami', 'Berlin', 'Singapore'].map(city => (
                              <button
                                key={city}
                                onClick={() => setScrapeCity(city)}
                                className={cn(
                                  "py-3 px-4 rounded-xl text-sm font-medium transition-all border",
                                  scrapeCity === city 
                                    ? "bg-primary/10 border-primary text-primary" 
                                    : "liquid-glass-button border-transparent text-apple-base"
                                )}
                              >
                                {city}
                              </button>
                            ))}
                          </div>
                        </div>

                        <div>
                          <label className="text-sm font-medium text-apple-base mb-3 block">2. Select Niche</label>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            {['SaaS', 'Energy', 'Logistics', 'Health', 'Real Estate', 'Finance', 'E-commerce', 'Legal'].map(niche => (
                              <button
                                key={niche}
                                onClick={() => setScrapeNiche(niche)}
                                className={cn(
                                  "py-3 px-4 rounded-xl text-sm font-medium transition-all border",
                                  scrapeNiche === niche 
                                    ? "bg-primary/10 border-primary text-primary" 
                                    : "liquid-glass-button border-transparent text-apple-base"
                                )}
                              >
                                {niche}
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center py-12">
                        <div className="relative w-32 h-32 mb-8">
                          <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                            <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="2" className="text-apple-muted/20" />
                            <motion.circle 
                              cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="4" 
                              className="text-primary"
                              strokeDasharray="283"
                              animate={{ strokeDashoffset: 283 - (283 * scrapeProgress) / 100 }}
                              transition={{ duration: 0.5 }}
                            />
                          </svg>
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-2xl font-light text-apple-base">{Math.round(scrapeProgress)}%</span>
                          </div>
                        </div>
                        <h4 className="text-lg font-medium text-apple-base mb-2">Extracting Leads...</h4>
                        <p className="text-sm text-apple-muted">Scanning {scrapeCity} for {scrapeNiche} businesses</p>
                      </div>
                    )}
                  </div>

                  <div className="p-8 border-t border-white/20 dark:border-white/10 shrink-0">
                    {!isScraping ? (
                      <button 
                        disabled={!scrapeCity || !scrapeNiche}
                        onClick={() => {
                          setIsScraping(true);
                          setScrapeProgress(0);
                          const interval = setInterval(() => {
                            setScrapeProgress(p => {
                              if (p >= 100) {
                                clearInterval(interval);
                                setTimeout(() => {
                                  setIsScraping(false);
                                  setIsScrapeModalOpen(false);
                                  setScrapeCity(null);
                                  setScrapeNiche(null);
                                }, 1000);
                                return 100;
                              }
                              return p + (Math.random() * 15);
                            });
                          }, 500);
                        }}
                        className="w-full bg-apple-base text-bg dark:bg-white dark:text-black py-4 rounded-xl text-sm font-medium hover:opacity-90 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                      >
                        <Zap size={16} />
                        Initialize Scrape Protocol
                      </button>
                    ) : (
                      <div className="w-full py-4 text-center text-sm font-medium text-apple-muted">
                        Please wait while the AI agents gather data...
                      </div>
                    )}
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>

          {/* Audit Pending Leads Surprise Modal */}
          <AnimatePresence>
            {isAuditModalOpen && (
              <div className="fixed inset-0 z-[200] flex items-center justify-center">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="absolute inset-0 bg-black/80 backdrop-blur-md"
                />
                
                {auditPhase === 'scanning' ? (
                  <motion.div 
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 1.2, opacity: 0 }}
                    className="relative z-10 flex flex-col items-center"
                  >
                    <button
                      onClick={() => setIsAuditModalOpen(false)}
                      className="absolute -top-12 right-0 w-8 h-8 rounded-full liquid-glass-button flex items-center justify-center text-white/50 hover:text-white transition-all z-10"
                    >
                      <X size={16} />
                    </button>
                    <div className="relative w-64 h-64 rounded-full border border-primary/30 flex items-center justify-center overflow-hidden mb-8">
                      <div className="absolute inset-0 bg-primary/10 rounded-full animate-ping" style={{ animationDuration: '2s' }} />
                      <div className="absolute inset-0 bg-primary/5 rounded-full animate-ping" style={{ animationDuration: '3s', animationDelay: '0.5s' }} />
                      <Radar size={48} className="text-primary animate-pulse" />
                      
                      {/* Radar Sweep Line */}
                      <motion.div 
                        className="absolute top-1/2 left-1/2 w-32 h-1 origin-left bg-gradient-to-r from-transparent via-primary to-primary"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      />
                    </div>
                    <h2 className="text-2xl font-light tracking-widest text-white uppercase">Deep Audit Initiated</h2>
                    <p className="text-sm text-white/50 mt-2 font-mono">Scanning pipeline for neglected revenue...</p>
                  </motion.div>
                ) : (
                  <motion.div 
                    initial={{ scale: 0.8, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    className="relative z-10 liquid-glass-panel p-12 rounded-[3rem] text-center max-w-lg mx-4"
                  >
                    <button
                      onClick={() => setIsAuditModalOpen(false)}
                      className="absolute top-6 right-6 w-8 h-8 rounded-full liquid-glass-button flex items-center justify-center text-white/50 hover:text-white transition-all z-10"
                    >
                      <X size={16} />
                    </button>
                    <div className="w-20 h-20 bg-success/20 rounded-full flex items-center justify-center mx-auto mb-6">
                      <CheckCircle2 size={40} className="text-success" />
                    </div>
                    <h2 className="text-3xl font-semibold text-white mb-2">Audit Complete</h2>
                    <p className="text-white/70 mb-8">The AI has identified hidden opportunities in your existing pipeline.</p>
                    
                    <div className="bg-black/30 rounded-2xl p-6 mb-8 border border-white/10">
                      <div className="text-sm text-white/50 uppercase tracking-wider mb-1">Recoverable Revenue Found</div>
                      <div className="text-5xl font-light text-success">$24,500</div>
                      <div className="text-sm text-white/70 mt-3">Across 12 neglected leads</div>
                    </div>

                    <button 
                      onClick={() => {
                        setIsAuditModalOpen(false);
                        setIsWarRoomModalOpen(true);
                      }}
                      className="w-full bg-white text-black py-4 rounded-xl font-medium hover:scale-[1.02] transition-transform"
                    >
                      Add to War Room
                    </button>
                  </motion.div>
                )}
              </div>
            )}
          </AnimatePresence>
          {/* War Room Modal */}
          <AnimatePresence>
            {isWarRoomModalOpen && (
              <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setIsWarRoomModalOpen(false)}
                  className="absolute inset-0 bg-black/20 dark:bg-black/40 backdrop-blur-sm"
                />
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 20 }}
                  className="relative w-full max-w-4xl h-[80vh] liquid-glass-panel rounded-[2rem] overflow-hidden flex flex-col"
                >
                  <div className="p-6 md:p-8 border-b border-white/20 dark:border-white/10 flex justify-between items-center shrink-0">
                    <div>
                      <h3 className="text-2xl font-semibold tracking-tight text-apple-base flex items-center gap-2">
                        <Zap className="text-primary" /> War Room
                      </h3>
                      <p className="text-sm text-apple-muted mt-1">High Intel Ready leads requiring immediate action.</p>
                    </div>
                    <button
                      onClick={() => setIsWarRoomModalOpen(false)}
                      className="w-8 h-8 rounded-full liquid-glass-button flex items-center justify-center text-apple-muted transition-all"
                    >
                      <X size={16} />
                    </button>
                  </div>
                  <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-4">
                    {leads.filter(l => l.status === 'High Intel Ready').map(lead => (
                      <div key={lead.id} className="liquid-glass rounded-2xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div>
                          <div className="text-lg font-semibold text-apple-base">{lead.businessName}</div>
                          <div className="text-sm text-apple-muted">{lead.niche} • {lead.city}</div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right hidden sm:block">
                            <div className="text-sm font-medium text-apple-base">${lead.monthlyValue.toLocaleString()}/mo</div>
                            <div className="text-xs text-apple-muted">Value</div>
                          </div>
                          <div className="text-right">
                            <div className="text-xl font-semibold text-apple-base">{lead.opportunityScore}</div>
                            <div className="text-xs text-apple-muted">Score</div>
                          </div>
                          <button className="bg-primary text-white px-4 py-2 rounded-xl text-sm font-medium hover:opacity-90 transition-all">
                            Attack
                          </button>
                        </div>
                      </div>
                    ))}
                    {leads.filter(l => l.status === 'High Intel Ready').length === 0 && (
                      <div className="text-center text-apple-muted py-12">No leads currently in the War Room.</div>
                    )}
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>

          {/* Inbox & Nurture Modal */}
          <AnimatePresence>
            {isInboxModalOpen && (
              <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setIsInboxModalOpen(false)}
                  className="absolute inset-0 bg-black/20 dark:bg-black/40 backdrop-blur-sm"
                />
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 20 }}
                  className="relative w-full max-w-5xl h-[85vh] liquid-glass-panel rounded-[2rem] overflow-hidden flex flex-col md:flex-row"
                >
                  <button
                    onClick={() => setIsInboxModalOpen(false)}
                    className="absolute top-6 right-6 w-8 h-8 rounded-full liquid-glass-button flex items-center justify-center text-apple-muted transition-all z-10 md:hidden"
                  >
                    <X size={16} />
                  </button>
                  
                  {/* Sidebar for Inbox */}
                  <div className="w-full md:w-80 border-b md:border-b-0 md:border-r border-white/20 dark:border-white/10 flex flex-col shrink-0 h-1/2 md:h-full">
                    <div className="p-6 border-b border-white/20 dark:border-white/10 flex justify-between items-center">
                      <h3 className="text-xl font-semibold tracking-tight text-apple-base">Inbox</h3>
                      <button
                        onClick={() => setIsInboxModalOpen(false)}
                        className="hidden md:flex w-8 h-8 rounded-full liquid-glass-button items-center justify-center text-apple-muted transition-all"
                      >
                        <X size={16} />
                      </button>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 space-y-2">
                      {leads.filter(l => ['Replied', 'Contacted', 'Demo Sent'].includes(l.status)).map(lead => {
                        const isOverdue = lead.lastContactedAt && (new Date().getTime() - new Date(lead.lastContactedAt).getTime()) > 1000 * 60 * 60 * 24 * 2; // 2 days
                        return (
                          <div 
                            key={lead.id} 
                            onClick={() => setSelectedInboxLead(lead)}
                            className={cn(
                              "p-3 rounded-xl cursor-pointer transition-all border",
                              selectedInboxLead?.id === lead.id 
                                ? "bg-white/20 dark:bg-black/20 border-white/30 dark:border-white/20" 
                                : "hover:bg-white/10 dark:hover:bg-black/10 border-transparent",
                              isOverdue && selectedInboxLead?.id !== lead.id ? "border-warning/30 bg-warning/5" : ""
                            )}
                          >
                            <div className="flex justify-between items-start mb-1">
                              <span className="font-medium text-apple-base text-sm flex items-center gap-2">
                                {lead.businessName}
                                {isOverdue && <span className="w-2 h-2 rounded-full bg-warning animate-pulse" title="Follow-up needed" />}
                              </span>
                              <span className="text-[10px] text-apple-muted">
                                {lead.lastContactedAt ? new Date(lead.lastContactedAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : '2h ago'}
                              </span>
                            </div>
                            <p className="text-xs text-apple-muted truncate">
                              {lead.status === 'Replied' ? 'Thanks for reaching out, we are interested...' : 
                               lead.status === 'Demo Sent' ? 'Here is the link to the demo...' : 'Follow up sequence initiated...'}
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  
                  {/* Main Content for Inbox */}
                  <div className="flex-1 flex flex-col h-1/2 md:h-full bg-white/5 dark:bg-black/5">
                    {selectedInboxLead ? (
                      <>
                        <div className="p-6 border-b border-white/20 dark:border-white/10 flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold shrink-0">
                              {selectedInboxLead.businessName.substring(0, 2).toUpperCase()}
                            </div>
                            <div>
                              <div className="font-medium text-apple-base flex items-center gap-2">
                                {selectedInboxLead.businessName}
                                {selectedInboxLead.lastContactedAt && (new Date().getTime() - new Date(selectedInboxLead.lastContactedAt).getTime()) > 1000 * 60 * 60 * 24 * 2 && (
                                  <span className="text-[10px] bg-warning/20 text-warning px-2 py-0.5 rounded-full font-medium">
                                    Follow-up Overdue
                                  </span>
                                )}
                              </div>
                              <div className="text-xs text-apple-muted">contact@{selectedInboxLead.website.replace('https://', '')}</div>
                            </div>
                          </div>
                          <div className="text-xs font-medium px-3 py-1 rounded-full bg-white/10 dark:bg-black/10 text-apple-base">
                            {selectedInboxLead.status}
                          </div>
                        </div>
                        <div className="flex-1 overflow-y-auto p-6 space-y-4 flex flex-col">
                          <div className="flex flex-col gap-1 max-w-[85%] md:max-w-[70%] self-end items-end">
                            <div className="bg-primary text-white p-3 rounded-2xl rounded-tr-sm text-sm">
                              Hi there, noticed your site is losing about ${selectedInboxLead.revenueLoss.toLocaleString()}/mo due to slow load times. We can fix this.
                            </div>
                            <span className="text-[10px] text-apple-muted mr-1">
                              {selectedInboxLead.lastContactedAt ? new Date(selectedInboxLead.lastContactedAt).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : 'Yesterday, 10:00 AM'}
                            </span>
                          </div>
                          {selectedInboxLead.status === 'Replied' && (
                            <div className="flex flex-col gap-1 max-w-[85%] md:max-w-[70%]">
                              <div className="bg-white/10 dark:bg-black/10 p-3 rounded-2xl rounded-tl-sm text-sm text-apple-base">
                                Thanks for reaching out. Do you have a portfolio I can look at?
                              </div>
                              <span className="text-[10px] text-apple-muted ml-1">Today, 2:30 PM</span>
                            </div>
                          )}
                          {inboxMessages[selectedInboxLead.id]?.map((msg, idx) => (
                            <div key={idx} className={cn("flex flex-col gap-1 max-w-[85%] md:max-w-[70%]", msg.isUser ? "self-end items-end" : "")}>
                              <div className={cn("p-3 rounded-2xl text-sm", msg.isUser ? "bg-primary text-white rounded-tr-sm" : "bg-white/10 dark:bg-black/10 text-apple-base rounded-tl-sm")}>
                                {msg.text}
                              </div>
                              <span className={cn("text-[10px] text-apple-muted", msg.isUser ? "mr-1" : "ml-1")}>{msg.timestamp}</span>
                            </div>
                          ))}
                        </div>
                        <div className="p-4 border-t border-white/20 dark:border-white/10">
                          <div className="relative">
                            <input 
                              type="text" 
                              value={replyText}
                              onChange={(e) => setReplyText(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  handleSendMessage();
                                }
                              }}
                              placeholder={`Reply to ${selectedInboxLead.businessName}...`}
                              className="w-full liquid-glass rounded-full py-3 pl-4 pr-12 text-sm text-apple-base placeholder:text-apple-muted focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                            />
                            <button 
                              onClick={handleSendMessage}
                              disabled={!replyText.trim()}
                              className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              <ArrowUp size={16} />
                            </button>
                          </div>
                        </div>
                      </>
                    ) : (
                      <div className="flex-1 flex flex-col items-center justify-center text-apple-muted">
                        <div className="w-16 h-16 rounded-full bg-white/5 dark:bg-black/5 flex items-center justify-center mb-4">
                          <Activity size={24} className="opacity-50" />
                        </div>
                        <p className="text-sm">Select a conversation to view</p>
                      </div>
                    )}
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>

          {/* Total Leads Modal */}
          <AnimatePresence>
            {isTotalLeadsModalOpen && (
              <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setIsTotalLeadsModalOpen(false)}
                  className="absolute inset-0 bg-black/40 dark:bg-black/60 backdrop-blur-md"
                />
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 20 }}
                  className="relative w-full max-w-7xl h-[90vh] flex flex-col liquid-glass-panel rounded-[2rem] overflow-hidden shadow-2xl"
                >
                  <div className="p-8 border-b border-white/20 dark:border-white/10 flex justify-between items-center shrink-0">
                    <div>
                      <h3 className="text-3xl font-semibold tracking-tight text-apple-base">System Vault</h3>
                      <p className="text-sm text-apple-muted mt-1">Direct view of all {totalLeads.toLocaleString()} scraped leads in the database pipeline.</p>
                    </div>
                    <button
                      onClick={() => setIsTotalLeadsModalOpen(false)}
                      className="w-10 h-10 rounded-full liquid-glass-button flex items-center justify-center text-apple-muted hover:text-red-500 transition-all z-10"
                    >
                      <X size={20} />
                    </button>
                  </div>
                  <div className="flex-1 overflow-y-auto p-8 relative z-0">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                      {leads.map((l) => (
                        <div key={l.id} className="liquid-glass rounded-2xl p-4 flex flex-col justify-between hover:bg-white/40 dark:hover:bg-black/40 transition-colors cursor-pointer border border-white/5 dark:border-white/5">
                          <div>
                            <div className="flex justify-between items-start mb-2">
                              <h4 className="text-sm font-bold text-apple-base truncate">{l.businessName}</h4>
                              <span className={cn(
                                "text-[10px] font-bold px-2 py-0.5 rounded-sm whitespace-nowrap",
                                l.status === 'New' ? "bg-gray-200 text-gray-800 dark:bg-zinc-800 dark:text-gray-200" :
                                l.status === 'Replied' ? "bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300" :
                                l.status === 'Contacted' ? "bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300" : "bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300"
                              )}>{l.status}</span>
                            </div>
                            <div className="text-xs text-apple-muted mb-4">{l.niche} • {l.city}</div>
                          </div>
                          <div className="flex items-center justify-between text-xs">
                            <span className="font-semibold text-danger">-${l.revenueLoss.toLocaleString()}/mo</span>
                            <span className="font-medium text-apple-muted">Score: {l.opportunityScore}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>

          {/* War Room Modal */}
          <AnimatePresence>
            {isWarRoomModalOpen && (
              <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setIsWarRoomModalOpen(false)}
                  className="absolute inset-0 bg-black/50 dark:bg-black/80 backdrop-blur-md"
                />
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 20 }}
                  className="relative w-full max-w-6xl h-[85vh] flex flex-col liquid-glass-panel rounded-[2rem] overflow-hidden shadow-2xl border-2 border-[#ffcc00]/30"
                >
                  <div className="p-8 border-b border-white/20 dark:border-white/10 flex justify-between items-center shrink-0 bg-[#ffcc00]/5">
                    <div>
                      <h3 className="text-3xl font-semibold tracking-tight text-apple-base flex items-center gap-3">
                        <Target className="text-[#ffcc00]" size={28} /> War Room Command
                      </h3>
                      <p className="text-sm text-apple-muted mt-1">High-priority targets pinned for immediate manual action or Diamond tracking.</p>
                    </div>
                    <button
                      onClick={() => setIsWarRoomModalOpen(false)}
                      className="w-10 h-10 rounded-full liquid-glass-button flex items-center justify-center text-apple-muted hover:text-red-500 transition-all z-10"
                    >
                      <X size={20} />
                    </button>
                  </div>
                  <div className="flex-1 overflow-y-auto p-8 relative z-0">
                    {warRoomLeads.length === 0 ? (
                      <div className="h-full flex flex-col items-center justify-center text-apple-muted opacity-50 space-y-4">
                        <Target size={64} className="mb-2" />
                        <p className="text-lg">No leads pinned to the War Room yet.</p>
                        <p className="text-sm">Use the "Add to War Room" button in the Pipeline to pin targets here.</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {warRoomLeads.map((l) => (
                          <div key={l.id} className="liquid-glass rounded-2xl p-5 flex flex-col justify-between border border-[#ffcc00]/20 hover:border-[#ffcc00]/50 transition-colors relative group">
                            <button 
                              onClick={() => setWarRoomLeads(prev => prev.filter(w => w.id !== l.id))}
                              className="absolute top-4 right-4 w-6 h-6 bg-red-500/10 text-red-500 opacity-0 group-hover:opacity-100 rounded-full flex items-center justify-center hover:bg-red-500 hover:text-white transition-all"
                            >
                              <X size={12} />
                            </button>
                            <div className="mb-4 pr-6">
                              <h4 className="text-base font-bold text-apple-base truncate mb-1">{l.businessName}</h4>
                              <div className="text-xs text-apple-muted mb-2">{l.niche} • {l.city}</div>
                              <div className={cn(
                                "inline-block text-[10px] font-bold px-2 py-0.5 rounded-sm whitespace-nowrap",
                                l.status === 'New' ? "bg-gray-200 text-gray-800 dark:bg-zinc-800 dark:text-gray-200" :
                                l.status === 'Replied' ? "bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300" :
                                l.status === 'Contacted' ? "bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300" : "bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300"
                              )}>{l.status}</div>
                            </div>
                            <div className="bg-[#ffcc00]/10 rounded-xl p-4 mt-auto">
                              <div className="flex justify-between items-center mb-1">
                                <span className="text-[10px] uppercase font-bold text-apple-muted">Opportunity Score</span>
                                <span className="text-lg font-bold text-apple-base">{l.opportunityScore}</span>
                              </div>
                              <div className="flex justify-between items-center">
                                <span className="text-[10px] uppercase font-bold text-apple-muted">Revenue Leakage</span>
                                <span className="text-base font-semibold text-danger">${l.revenueLoss.toLocaleString()}/mo</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
