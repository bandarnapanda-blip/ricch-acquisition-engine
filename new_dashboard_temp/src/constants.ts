import { Lead, AgentStatus, LogEntry, Task } from './types';

export const MOCK_LEADS: Lead[] = [
  {
    id: '1',
    businessName: 'Quantum Dynamics',
    website: 'https://quantum-dyn.com',
    niche: 'SaaS',
    city: 'San Francisco',
    opportunityScore: 88,
    revenueLoss: 12500,
    status: 'Replied',
    replyStatus: 'positive',
    lastContactedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1).toISOString(), // 1 day ago
    speedScore: 42,
    seoScore: 55,
    mobileScore: 38,
    monthlyValue: 2500,
  },
  {
    id: '2',
    businessName: 'Solaris Energy',
    website: 'https://solaris-energy.io',
    niche: 'Renewables',
    city: 'Austin',
    opportunityScore: 92,
    revenueLoss: 45000,
    status: 'High Intel Ready',
    speedScore: 28,
    seoScore: 40,
    mobileScore: 22,
    monthlyValue: 5000,
  },
  {
    id: '3',
    businessName: 'Apex Logistics',
    website: 'https://apex-logistics.net',
    niche: 'Logistics',
    city: 'Chicago',
    opportunityScore: 65,
    revenueLoss: 8000,
    status: 'Contacted',
    lastContactedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 4).toISOString(), // 4 days ago
    speedScore: 65,
    seoScore: 72,
    mobileScore: 58,
    monthlyValue: 1500,
  },
  {
    id: '4',
    businessName: 'Zenith Health',
    website: 'https://zenith-health.co',
    niche: 'Healthcare',
    city: 'New York',
    opportunityScore: 78,
    revenueLoss: 22000,
    status: 'Demo Sent',
    replyStatus: 'positive',
    lastContactedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(), // 2 days ago
    speedScore: 35,
    seoScore: 48,
    mobileScore: 31,
    monthlyValue: 3500,
  },
  {
    id: '5',
    businessName: 'Titan Real Estate',
    website: 'https://titan-re.com',
    niche: 'Real Estate',
    city: 'Miami',
    opportunityScore: 45,
    revenueLoss: 5000,
    status: 'New',
    speedScore: 82,
    seoScore: 85,
    mobileScore: 78,
    monthlyValue: 1200,
  }
];

export const AGENT_STATUSES: AgentStatus[] = [
  { name: 'Scraper', status: 'LIVE', lastActive: '2s ago' },
  { name: 'Inbox', status: 'LIVE', lastActive: '45s ago' },
  { name: 'Outreach', status: 'IDLE', lastActive: '10m ago' },
];

export const MOCK_LOGS: LogEntry[] = [
  { timestamp: '16:03:10', message: 'Scraping target: solaris-energy.io', service: 'Scraper' },
  { timestamp: '16:02:45', message: 'Positive reply detected from quantum-dyn.com', service: 'Inbox' },
  { timestamp: '16:01:20', message: 'Audit complete for apex-logistics.net (Score: 65)', service: 'Scraper' },
  { timestamp: '16:00:05', message: 'Outreach sequence started for 12 new leads', service: 'Outreach' },
  { timestamp: '15:58:30', message: 'System heartbeat: All agents operational', service: 'System' },
];

export const MOCK_TASKS: Task[] = [
  {
    id: 't1',
    leadId: '1',
    title: 'Follow up on Demo',
    description: 'Send a follow-up email to Quantum Dynamics regarding the demo sent yesterday.',
    status: 'Pending',
    assignee: 'Alice',
    dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 1).toISOString(), // Tomorrow
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1).toISOString(),
  },
  {
    id: 't2',
    leadId: '2',
    title: 'Prepare Custom Proposal',
    description: 'Create a custom proposal for Solaris Energy based on their high intel score.',
    status: 'In Progress',
    assignee: 'Bob',
    dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 2).toISOString(),
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
  },
  {
    id: 't3',
    leadId: '4',
    title: 'Schedule Discovery Call',
    description: 'Call Zenith Health to schedule a discovery call after positive reply.',
    status: 'Completed',
    assignee: 'Alice',
    dueDate: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1).toISOString(),
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
  }
];
