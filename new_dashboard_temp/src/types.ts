export interface Lead {
  id: string;
  businessName: string;
  website: string;
  niche: string;
  city: string;
  opportunityScore: number;
  revenueLoss: number;
  status: 'New' | 'High Intel Ready' | 'Contacted' | 'Replied' | 'Demo Sent' | 'Closed';
  replyStatus?: 'positive' | 'neutral' | 'negative';
  lastContactedAt?: string;
  speedScore: number;
  seoScore: number;
  mobileScore: number;
  monthlyValue: number;
  websiteRoast?: string;
  demoLink?: string;
  paymentStatus?: string;
  amountPaid?: number;
}

export interface AgentStatus {
  name: string;
  status: 'LIVE' | 'IDLE' | 'DOWN';
  lastActive: string;
}

export interface LogEntry {
  timestamp: string;
  message: string;
  service: string;
}

export interface Task {
  id: string;
  leadId: string;
  title: string;
  description: string;
  status: 'Pending' | 'In Progress' | 'Completed';
  assignee: string;
  dueDate: string;
  createdAt: string;
}
