import { useState, useContext } from 'react';
import { AuthContext } from '../App';

const allCertifications = [
  {
    id: 1,
    title: 'AWS Solutions Architect – Associate',
    provider: 'Amazon Web Services',
    providerShort: 'AWS',
    category: 'Cloud',
    level: 'Associate',
    duration: '3-4 months',
    cost: '$$',
    costValue: 300,
    description: 'Design and deploy scalable, highly available systems on AWS. Covers compute, networking, storage, and database services.',
    skills: ['EC2', 'S3', 'VPC', 'IAM', 'Lambda', 'CloudFormation'],
    featured: true,
    gradient: 'from-amber-500/20 via-orange-500/10 to-yellow-500/20',
    accent: '#FF9900',
    icon: 'cloud',
  },
  {
    id: 2,
    title: 'Google Cloud Professional Cloud Architect',
    provider: 'Google Cloud',
    providerShort: 'GCP',
    category: 'Cloud',
    level: 'Professional',
    duration: '4-6 months',
    cost: '$$',
    costValue: 300,
    description: 'Design, develop, and manage robust, secure, scalable solutions on Google Cloud infrastructure.',
    skills: ['GKE', 'BigQuery', 'Cloud Run', 'IAM', 'Pub/Sub', 'Spanner'],
    featured: true,
    gradient: 'from-blue-500/20 via-cyan-500/10 to-green-500/20',
    accent: '#4285F4',
    icon: 'cloud_circle',
  },
  {
    id: 3,
    title: 'Microsoft Azure Administrator (AZ-104)',
    provider: 'Microsoft',
    providerShort: 'Azure',
    category: 'Cloud',
    level: 'Associate',
    duration: '2-3 months',
    cost: '$$',
    costValue: 165,
    description: 'Implement, manage, and monitor identity, governance, storage, compute, and virtual networks in Azure.',
    skills: ['Azure AD', 'VMs', 'Storage', 'Networking', 'Monitor', 'ARM'],
    featured: true,
    gradient: 'from-sky-500/20 via-blue-500/10 to-indigo-500/20',
    accent: '#0078D4',
    icon: 'deployed_code',
  },
  {
    id: 4,
    title: 'CompTIA Security+',
    provider: 'CompTIA',
    providerShort: 'CompTIA',
    category: 'Security',
    level: 'Associate',
    duration: '2-3 months',
    cost: '$$',
    costValue: 392,
    description: 'Validate baseline cybersecurity skills including threat management, cryptography, and identity management.',
    skills: ['Threat Analysis', 'Cryptography', 'PKI', 'Risk Mgmt', 'Compliance'],
    featured: false,
    icon: 'shield_lock',
  },
  {
    id: 5,
    title: 'Certified Kubernetes Administrator (CKA)',
    provider: 'CNCF',
    providerShort: 'CNCF',
    category: 'DevOps',
    level: 'Professional',
    duration: '2-4 months',
    cost: '$$',
    costValue: 395,
    description: 'Demonstrate the skills to design, build, configure, and manage Kubernetes clusters in production.',
    skills: ['Pods', 'Services', 'RBAC', 'Networking', 'Storage', 'Troubleshooting'],
    featured: false,
    icon: 'view_in_ar',
  },
  {
    id: 6,
    title: 'HashiCorp Terraform Associate',
    provider: 'HashiCorp',
    providerShort: 'HashiCorp',
    category: 'DevOps',
    level: 'Associate',
    duration: '1-2 months',
    cost: '$',
    costValue: 70,
    description: 'Understand infrastructure as code concepts and HashiCorp Terraform for provisioning and managing cloud resources.',
    skills: ['IaC', 'HCL', 'Providers', 'Modules', 'State', 'Workspaces'],
    featured: false,
    icon: 'terminal',
  },
  {
    id: 7,
    title: 'Project Management Professional (PMP)',
    provider: 'PMI',
    providerShort: 'PMI',
    category: 'Project Management',
    level: 'Professional',
    duration: '3-6 months',
    cost: '$$$',
    costValue: 555,
    description: 'Globally recognized certification for project managers covering predictive, agile, and hybrid approaches.',
    skills: ['Agile', 'Waterfall', 'Risk Mgmt', 'Stakeholders', 'Scheduling', 'Budgeting'],
    featured: false,
    icon: 'assignment',
  },
  {
    id: 8,
    title: 'AWS Certified Machine Learning – Specialty',
    provider: 'Amazon Web Services',
    providerShort: 'AWS',
    category: 'AI/ML',
    level: 'Expert',
    duration: '4-6 months',
    cost: '$$',
    costValue: 300,
    description: 'Design, implement, deploy, and maintain ML solutions on AWS using SageMaker and related services.',
    skills: ['SageMaker', 'Data Engineering', 'Modeling', 'MLOps', 'Deep Learning'],
    featured: false,
    icon: 'psychology',
  },
  {
    id: 9,
    title: 'Google TensorFlow Developer Certificate',
    provider: 'Google',
    providerShort: 'Google',
    category: 'AI/ML',
    level: 'Associate',
    duration: '2-3 months',
    cost: '$',
    costValue: 100,
    description: 'Demonstrate proficiency in building and training neural networks using TensorFlow for real-world problems.',
    skills: ['TensorFlow', 'CNNs', 'RNNs', 'NLP', 'Time Series', 'Transfer Learning'],
    featured: false,
    icon: 'model_training',
  },
  {
    id: 10,
    title: 'Certified Information Systems Security Professional (CISSP)',
    provider: 'ISC²',
    providerShort: 'ISC²',
    category: 'Security',
    level: 'Expert',
    duration: '4-6 months',
    cost: '$$$',
    costValue: 749,
    description: 'Advanced cybersecurity certification covering security architecture, engineering, and management.',
    skills: ['Security Ops', 'Architecture', 'Risk Mgmt', 'Cryptography', 'Network Security'],
    featured: false,
    icon: 'verified_user',
  },
  {
    id: 11,
    title: 'Databricks Certified Data Engineer Associate',
    provider: 'Databricks',
    providerShort: 'Databricks',
    category: 'Data',
    level: 'Associate',
    duration: '2-3 months',
    cost: '$$',
    costValue: 200,
    description: 'Validate skills in using the Databricks Lakehouse Platform for data engineering workloads.',
    skills: ['Spark', 'Delta Lake', 'ETL', 'SQL', 'Data Pipelines', 'Unity Catalog'],
    featured: false,
    icon: 'database',
  },
  {
    id: 12,
    title: 'Snowflake SnowPro Core Certification',
    provider: 'Snowflake',
    providerShort: 'Snowflake',
    category: 'Data',
    level: 'Associate',
    duration: '1-2 months',
    cost: '$$',
    costValue: 175,
    description: 'Demonstrate knowledge of Snowflake\'s cloud data platform features, architecture, and best practices.',
    skills: ['Warehouses', 'Data Sharing', 'Stages', 'Streams', 'Tasks', 'Security'],
    featured: false,
    icon: 'ac_unit',
  },
  {
    id: 13,
    title: 'Certified ScrumMaster (CSM)',
    provider: 'Scrum Alliance',
    providerShort: 'Scrum Alliance',
    category: 'Project Management',
    level: 'Associate',
    duration: '1-2 months',
    cost: '$$',
    costValue: 250,
    description: 'Master the Scrum framework and learn to facilitate Scrum events for agile teams effectively.',
    skills: ['Scrum', 'Sprint Planning', 'Retrospectives', 'Facilitation', 'Servant Leadership'],
    featured: false,
    icon: 'groups',
  },
  {
    id: 14,
    title: 'AWS Certified DevOps Engineer – Professional',
    provider: 'Amazon Web Services',
    providerShort: 'AWS',
    category: 'DevOps',
    level: 'Professional',
    duration: '4-6 months',
    cost: '$$',
    costValue: 300,
    description: 'Provision, operate, and manage distributed systems on the AWS platform with CI/CD best practices.',
    skills: ['CodePipeline', 'CloudFormation', 'ECS', 'Monitoring', 'Incident Response'],
    featured: false,
    icon: 'build_circle',
  },
  {
    id: 15,
    title: 'Microsoft Azure AI Engineer (AI-102)',
    provider: 'Microsoft',
    providerShort: 'Azure',
    category: 'AI/ML',
    level: 'Associate',
    duration: '2-4 months',
    cost: '$$',
    costValue: 165,
    description: 'Build, manage, and deploy AI solutions using Azure Cognitive Services, Azure AI, and Azure OpenAI.',
    skills: ['Cognitive Services', 'Azure OpenAI', 'Bot Service', 'Computer Vision', 'NLP'],
    featured: false,
    icon: 'smart_toy',
  },
];

const categories = ['All', 'Cloud', 'Data', 'Security', 'DevOps', 'AI/ML', 'Project Management'];

const categoryIcons = {
  All: 'apps',
  Cloud: 'cloud',
  Data: 'database',
  Security: 'shield',
  DevOps: 'terminal',
  'AI/ML': 'psychology',
  'Project Management': 'assignment',
};

const levelColors = {
  Associate: { bg: 'bg-sky-500/15', text: 'text-sky-400', border: 'border-sky-500/30' },
  Professional: { bg: 'bg-violet-500/15', text: 'text-violet-400', border: 'border-violet-500/30' },
  Expert: { bg: 'bg-amber-500/15', text: 'text-amber-400', border: 'border-amber-500/30' },
};

const costColors = {
  Free: 'text-emerald-400',
  '$': 'text-emerald-400',
  '$$': 'text-amber-400',
  '$$$': 'text-rose-400',
};

const initialTracked = [
  { certId: 1, status: 'In Progress', progress: 68 },
  { certId: 5, status: 'In Progress', progress: 35 },
  { certId: 4, status: 'Completed', progress: 100 },
  { certId: 6, status: 'Not Started', progress: 0 },
  { certId: 9, status: 'In Progress', progress: 52 },
];

export default function Certifications() {
  const { user } = useContext(AuthContext);
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [trackedCerts, setTrackedCerts] = useState(initialTracked);
  const [showMyOnly, setShowMyOnly] = useState(false);

  const getTracked = (certId) => trackedCerts.find((t) => t.certId === certId);

  const handleTrack = (certId) => {
    if (getTracked(certId)) return;
    setTrackedCerts((prev) => [...prev, { certId, status: 'Not Started', progress: 0 }]);
  };

  const filteredCerts = allCertifications.filter((cert) => {
    const matchesSearch =
      cert.title.toLowerCase().includes(search.toLowerCase()) ||
      cert.provider.toLowerCase().includes(search.toLowerCase()) ||
      cert.skills.some((s) => s.toLowerCase().includes(search.toLowerCase()));
    const matchesCategory = activeCategory === 'All' || cert.category === activeCategory;
    const matchesTracked = !showMyOnly || getTracked(cert.id);
    return matchesSearch && matchesCategory && matchesTracked;
  });

  const featuredCerts = allCertifications.filter((c) => c.featured);
  const nonFeaturedFiltered = filteredCerts.filter((c) => !c.featured || activeCategory !== 'All' || search);

  const statsInProgress = trackedCerts.filter((t) => t.status === 'In Progress').length;
  const statsCompleted = trackedCerts.filter((t) => t.status === 'Completed').length;
  const statsTotal = allCertifications.length;

  const statusIcon = { 'Not Started': 'radio_button_unchecked', 'In Progress': 'timelapse', Completed: 'check_circle' };
  const statusColor = {
    'Not Started': 'text-gray-400',
    'In Progress': 'text-amber-400',
    Completed: 'text-emerald-400',
  };

  return (
    <div className="space-y-xl animate-fade-in-up">
      {/* ─── Header ─── */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[var(--md-sys-color-primary-container)]/20 via-[var(--md-sys-color-primary)]/8 to-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/30 p-xl">
        <div className="absolute -top-24 -right-24 w-72 h-72 rounded-full bg-[var(--md-sys-color-primary)]/6 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-16 -left-16 w-56 h-56 rounded-full bg-violet-500/6 blur-3xl pointer-events-none" />

        <div className="relative flex flex-col lg:flex-row lg:items-end gap-lg">
          <div className="flex-1 space-y-sm">
            <div className="flex items-center gap-sm">
              <div className="w-12 h-12 rounded-xl bg-[var(--md-sys-color-primary)]/15 flex items-center justify-center">
                <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 28 }}>
                  workspace_premium
                </span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-[var(--md-sys-color-on-surface)] font-[Geist]">
                  Certifications
                </h1>
                <p className="text-sm text-[var(--md-sys-color-on-surface-variant)]">
                  Discover, track &amp; earn industry-recognized credentials
                </p>
              </div>
            </div>
          </div>

          {/* Search */}
          <div className="relative w-full lg:w-96">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[var(--md-sys-color-on-surface-variant)]/60" style={{ fontSize: 20 }}>
              search
            </span>
            <input
              type="text"
              placeholder="Search certifications, providers, skills…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/40 text-[var(--md-sys-color-on-surface)] text-sm placeholder:text-[var(--md-sys-color-on-surface-variant)]/50 focus:outline-none focus:ring-2 focus:ring-[var(--md-sys-color-primary)]/40 focus:border-[var(--md-sys-color-primary)]/60 transition-all"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--md-sys-color-on-surface-variant)]/60 hover:text-[var(--md-sys-color-on-surface)] transition-colors"
              >
                <span className="material-symbols-outlined" style={{ fontSize: 18 }}>close</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ─── Stats Bar ─── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-md">
        {[
          { label: 'Total Available', value: statsTotal, icon: 'library_books', color: 'text-[var(--md-sys-color-primary)]', bg: 'bg-[var(--md-sys-color-primary)]/12' },
          { label: 'In Progress', value: statsInProgress, icon: 'timelapse', color: 'text-amber-400', bg: 'bg-amber-500/12' },
          { label: 'Completed', value: statsCompleted, icon: 'emoji_events', color: 'text-emerald-400', bg: 'bg-emerald-500/12' },
        ].map((stat) => (
          <div
            key={stat.label}
            className="group relative overflow-hidden rounded-xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 p-lg flex items-center gap-md hover:border-[var(--md-sys-color-outline-variant)]/50 transition-all duration-300"
          >
            <div className={`w-12 h-12 rounded-xl ${stat.bg} flex items-center justify-center shrink-0`}>
              <span className={`material-symbols-outlined ${stat.color}`} style={{ fontSize: 24 }}>{stat.icon}</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--md-sys-color-on-surface)] font-[Geist]">{stat.value}</p>
              <p className="text-xs text-[var(--md-sys-color-on-surface-variant)] font-[Geist]">{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ─── Filter Bar ─── */}
      <div className="flex flex-wrap items-center gap-sm">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium font-[Geist] transition-all duration-300 border ${
              activeCategory === cat
                ? 'bg-[var(--md-sys-color-primary)] text-[var(--md-sys-color-on-primary)] border-[var(--md-sys-color-primary)] shadow-lg shadow-[var(--md-sys-color-primary)]/25'
                : 'bg-[var(--md-sys-color-surface-container)] text-[var(--md-sys-color-on-surface-variant)] border-[var(--md-sys-color-outline-variant)]/30 hover:border-[var(--md-sys-color-primary)]/40 hover:text-[var(--md-sys-color-on-surface)]'
            }`}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>{categoryIcons[cat]}</span>
            {cat}
          </button>
        ))}

        <div className="ml-auto">
          <button
            onClick={() => setShowMyOnly(!showMyOnly)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium font-[Geist] transition-all duration-300 border ${
              showMyOnly
                ? 'bg-violet-500/15 text-violet-400 border-violet-500/40'
                : 'bg-[var(--md-sys-color-surface-container)] text-[var(--md-sys-color-on-surface-variant)] border-[var(--md-sys-color-outline-variant)]/30 hover:border-violet-500/40'
            }`}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>bookmark</span>
            My Certs
          </button>
        </div>
      </div>

      {/* ─── Featured Certifications ─── */}
      {activeCategory === 'All' && !search && !showMyOnly && (
        <div className="space-y-md">
          <div className="flex items-center gap-sm">
            <span className="material-symbols-outlined text-amber-400" style={{ fontSize: 22 }}>star</span>
            <h2 className="text-lg font-semibold text-[var(--md-sys-color-on-surface)] font-[Geist]">Featured Certifications</h2>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-md">
            {featuredCerts.map((cert) => {
              const tracked = getTracked(cert.id);
              return (
                <div
                  key={cert.id}
                  className={`group relative overflow-hidden rounded-2xl bg-gradient-to-br ${cert.gradient} border border-[var(--md-sys-color-outline-variant)]/20 p-lg flex flex-col gap-md hover:border-[var(--md-sys-color-outline-variant)]/50 hover:shadow-xl hover:shadow-black/10 transition-all duration-500 hover:-translate-y-1`}
                >
                  {/* Glow */}
                  <div
                    className="absolute -top-20 -right-20 w-44 h-44 rounded-full blur-3xl opacity-30 pointer-events-none transition-opacity duration-500 group-hover:opacity-50"
                    style={{ background: cert.accent }}
                  />

                  {/* Provider & Level */}
                  <div className="relative flex items-center justify-between">
                    <div className="flex items-center gap-sm">
                      <div className="w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold font-[Geist]" style={{ background: cert.accent + '22', color: cert.accent }}>
                        {cert.providerShort.slice(0, 3)}
                      </div>
                      <span className="text-xs text-[var(--md-sys-color-on-surface-variant)] font-[Geist]">{cert.provider}</span>
                    </div>
                    <span className={`text-xs px-2.5 py-1 rounded-full font-medium font-[Geist] border ${levelColors[cert.level].bg} ${levelColors[cert.level].text} ${levelColors[cert.level].border}`}>
                      {cert.level}
                    </span>
                  </div>

                  {/* Title & Description */}
                  <div className="relative flex-1 space-y-xs">
                    <h3 className="text-base font-semibold text-[var(--md-sys-color-on-surface)] leading-snug line-clamp-2">
                      {cert.title}
                    </h3>
                    <p className="text-xs text-[var(--md-sys-color-on-surface-variant)] leading-relaxed line-clamp-2">
                      {cert.description}
                    </p>
                  </div>

                  {/* Meta */}
                  <div className="relative flex items-center gap-md text-xs text-[var(--md-sys-color-on-surface-variant)]">
                    <span className="flex items-center gap-1">
                      <span className="material-symbols-outlined" style={{ fontSize: 15 }}>schedule</span>
                      {cert.duration}
                    </span>
                    <span className={`flex items-center gap-1 font-semibold ${costColors[cert.cost]}`}>
                      <span className="material-symbols-outlined" style={{ fontSize: 15 }}>payments</span>
                      {cert.cost}
                    </span>
                  </div>

                  {/* Progress or Action */}
                  {tracked ? (
                    <div className="relative space-y-xs">
                      <div className="flex justify-between text-xs font-[Geist]">
                        <span className={statusColor[tracked.status]}>{tracked.status}</span>
                        <span className="text-[var(--md-sys-color-on-surface-variant)]">{tracked.progress}%</span>
                      </div>
                      <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-700 ease-out"
                          style={{
                            width: `${tracked.progress}%`,
                            background: tracked.status === 'Completed' ? '#34d399' : cert.accent,
                          }}
                        />
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleTrack(cert.id)}
                      className="relative w-full py-2.5 rounded-xl text-sm font-semibold font-[Geist] text-white transition-all duration-300 hover:shadow-lg"
                      style={{ background: cert.accent }}
                    >
                      Start Learning
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ─── My Certifications Progress ─── */}
      {trackedCerts.length > 0 && (showMyOnly || (!search && activeCategory === 'All')) && (
        <div className="space-y-md">
          <div className="flex items-center gap-sm">
            <span className="material-symbols-outlined text-violet-400" style={{ fontSize: 22 }}>bookmark</span>
            <h2 className="text-lg font-semibold text-[var(--md-sys-color-on-surface)] font-[Geist]">My Certifications</h2>
            <span className="ml-1 px-2 py-0.5 rounded-full text-xs font-medium bg-violet-500/15 text-violet-400 font-[Geist]">
              {trackedCerts.length}
            </span>
          </div>

          <div className="rounded-xl overflow-hidden border border-[var(--md-sys-color-outline-variant)]/25 bg-[var(--md-sys-color-surface-container)]">
            {trackedCerts.map((t, i) => {
              const cert = allCertifications.find((c) => c.id === t.certId);
              if (!cert) return null;
              return (
                <div
                  key={cert.id}
                  className={`flex items-center gap-md p-md hover:bg-white/[0.03] transition-colors ${
                    i !== trackedCerts.length - 1 ? 'border-b border-[var(--md-sys-color-outline-variant)]/15' : ''
                  }`}
                >
                  {/* Status Icon */}
                  <div className="w-10 h-10 rounded-lg bg-[var(--md-sys-color-surface-container-low)] flex items-center justify-center shrink-0">
                    <span className={`material-symbols-outlined ${statusColor[t.status]}`} style={{ fontSize: 22 }}>
                      {statusIcon[t.status]}
                    </span>
                  </div>

                  {/* Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-sm">
                      <h4 className="text-sm font-medium text-[var(--md-sys-color-on-surface)] truncate">{cert.title}</h4>
                      <span className={`shrink-0 text-[10px] px-2 py-0.5 rounded-full font-medium font-[Geist] border ${levelColors[cert.level].bg} ${levelColors[cert.level].text} ${levelColors[cert.level].border}`}>
                        {cert.level}
                      </span>
                    </div>
                    <p className="text-xs text-[var(--md-sys-color-on-surface-variant)] mt-0.5">{cert.provider}</p>
                  </div>

                  {/* Progress */}
                  <div className="w-36 shrink-0 hidden sm:block">
                    <div className="flex justify-between text-[10px] font-[Geist] mb-1">
                      <span className={statusColor[t.status]}>{t.status}</span>
                      <span className="text-[var(--md-sys-color-on-surface-variant)]">{t.progress}%</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-white/8 overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700 ease-out"
                        style={{
                          width: `${t.progress}%`,
                          background:
                            t.status === 'Completed'
                              ? '#34d399'
                              : t.status === 'In Progress'
                              ? '#fbbf24'
                              : '#6b7280',
                        }}
                      />
                    </div>
                  </div>

                  {/* Action */}
                  <button className="shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium font-[Geist] bg-[var(--md-sys-color-primary)]/12 text-[var(--md-sys-color-primary)] hover:bg-[var(--md-sys-color-primary)]/20 transition-colors">
                    {t.status === 'Completed' ? 'View' : t.status === 'In Progress' ? 'Continue' : 'Start'}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ─── Certification Grid ─── */}
      <div className="space-y-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-sm">
            <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 22 }}>grid_view</span>
            <h2 className="text-lg font-semibold text-[var(--md-sys-color-on-surface)] font-[Geist]">
              {activeCategory === 'All' ? 'All Certifications' : `${activeCategory} Certifications`}
            </h2>
            <span className="ml-1 px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--md-sys-color-primary)]/12 text-[var(--md-sys-color-primary)] font-[Geist]">
              {(activeCategory !== 'All' || search || showMyOnly ? filteredCerts : nonFeaturedFiltered).length}
            </span>
          </div>
        </div>

        {(activeCategory !== 'All' || search || showMyOnly ? filteredCerts : nonFeaturedFiltered).length === 0 ? (
          <div className="rounded-2xl border border-dashed border-[var(--md-sys-color-outline-variant)]/30 bg-[var(--md-sys-color-surface-container)]/50 py-16 flex flex-col items-center gap-md">
            <span className="material-symbols-outlined text-[var(--md-sys-color-on-surface-variant)]/30" style={{ fontSize: 48 }}>search_off</span>
            <p className="text-sm text-[var(--md-sys-color-on-surface-variant)]">No certifications match your filters</p>
            <button
              onClick={() => { setSearch(''); setActiveCategory('All'); setShowMyOnly(false); }}
              className="text-xs text-[var(--md-sys-color-primary)] hover:underline font-[Geist]"
            >
              Clear all filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-md">
            {(activeCategory !== 'All' || search || showMyOnly ? filteredCerts : nonFeaturedFiltered).map((cert, idx) => {
              const tracked = getTracked(cert.id);
              return (
                <div
                  key={cert.id}
                  className="group relative overflow-hidden rounded-xl bg-[var(--md-sys-color-surface-container)] border border-[var(--md-sys-color-outline-variant)]/25 flex flex-col hover:border-[var(--md-sys-color-outline-variant)]/50 hover:shadow-lg hover:shadow-black/8 transition-all duration-400 hover:-translate-y-0.5"
                  style={{ animationDelay: `${idx * 50}ms` }}
                >
                  {/* Card Header */}
                  <div className="p-md pb-sm space-y-sm">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-sm">
                        <div className="w-9 h-9 rounded-lg bg-[var(--md-sys-color-primary)]/10 flex items-center justify-center">
                          <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 20 }}>
                            {cert.icon}
                          </span>
                        </div>
                        <div>
                          <p className="text-[10px] uppercase tracking-wider text-[var(--md-sys-color-on-surface-variant)] font-[Geist] font-medium">
                            {cert.providerShort}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium font-[Geist] border ${levelColors[cert.level].bg} ${levelColors[cert.level].text} ${levelColors[cert.level].border}`}>
                          {cert.level}
                        </span>
                      </div>
                    </div>

                    <h3 className="text-sm font-semibold text-[var(--md-sys-color-on-surface)] leading-snug line-clamp-2 min-h-[2.5rem]">
                      {cert.title}
                    </h3>

                    <p className="text-xs text-[var(--md-sys-color-on-surface-variant)]/70 leading-relaxed line-clamp-2">
                      {cert.description}
                    </p>
                  </div>

                  {/* Skills */}
                  <div className="px-md pb-sm flex flex-wrap gap-1">
                    {cert.skills.slice(0, 4).map((skill) => (
                      <span
                        key={skill}
                        className="text-[10px] px-2 py-0.5 rounded-md bg-[var(--md-sys-color-surface-container-low)] text-[var(--md-sys-color-on-surface-variant)] font-[Geist]"
                      >
                        {skill}
                      </span>
                    ))}
                    {cert.skills.length > 4 && (
                      <span className="text-[10px] px-2 py-0.5 rounded-md bg-[var(--md-sys-color-surface-container-low)] text-[var(--md-sys-color-on-surface-variant)]/60 font-[Geist]">
                        +{cert.skills.length - 4}
                      </span>
                    )}
                  </div>

                  {/* Divider */}
                  <div className="mx-md border-t border-[var(--md-sys-color-outline-variant)]/15" />

                  {/* Footer */}
                  <div className="p-md pt-sm flex items-center justify-between mt-auto">
                    <div className="flex items-center gap-md text-xs text-[var(--md-sys-color-on-surface-variant)]">
                      <span className="flex items-center gap-1">
                        <span className="material-symbols-outlined" style={{ fontSize: 14 }}>schedule</span>
                        {cert.duration}
                      </span>
                      <span className={`flex items-center gap-1 font-semibold font-[Geist] ${costColors[cert.cost]}`}>
                        {cert.cost}
                      </span>
                    </div>

                    {tracked ? (
                      <div className="flex items-center gap-2">
                        {tracked.status === 'Completed' ? (
                          <span className="flex items-center gap-1 text-xs text-emerald-400 font-medium font-[Geist]">
                            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>check_circle</span>
                            Earned
                          </span>
                        ) : tracked.status === 'In Progress' ? (
                          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium font-[Geist] bg-amber-500/15 text-amber-400 border border-amber-500/25 hover:bg-amber-500/25 transition-colors">
                            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>play_arrow</span>
                            Continue · {tracked.progress}%
                          </button>
                        ) : (
                          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium font-[Geist] bg-[var(--md-sys-color-primary)]/12 text-[var(--md-sys-color-primary)] border border-[var(--md-sys-color-primary)]/25 hover:bg-[var(--md-sys-color-primary)]/20 transition-colors">
                            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>play_arrow</span>
                            Start
                          </button>
                        )}
                      </div>
                    ) : (
                      <button
                        onClick={() => handleTrack(cert.id)}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium font-[Geist] bg-[var(--md-sys-color-primary)]/12 text-[var(--md-sys-color-primary)] border border-[var(--md-sys-color-primary)]/25 hover:bg-[var(--md-sys-color-primary)]/20 transition-colors"
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 14 }}>add</span>
                        Start Learning
                      </button>
                    )}
                  </div>

                  {/* Tracked indicator */}
                  {tracked && (
                    <div
                      className="absolute top-0 left-0 w-full h-0.5"
                      style={{
                        background:
                          tracked.status === 'Completed'
                            ? 'linear-gradient(90deg, #34d399, #059669)'
                            : tracked.status === 'In Progress'
                            ? 'linear-gradient(90deg, #fbbf24, #f59e0b)'
                            : 'linear-gradient(90deg, #6b7280, #9ca3af)',
                      }}
                    />
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ─── Bottom Tip ─── */}
      <div className="rounded-xl bg-gradient-to-r from-[var(--md-sys-color-primary)]/8 to-violet-500/8 border border-[var(--md-sys-color-outline-variant)]/20 p-md flex items-center gap-md">
        <div className="w-10 h-10 rounded-lg bg-[var(--md-sys-color-primary)]/12 flex items-center justify-center shrink-0">
          <span className="material-symbols-outlined text-[var(--md-sys-color-primary)]" style={{ fontSize: 22 }}>lightbulb</span>
        </div>
        <div className="flex-1">
          <p className="text-sm text-[var(--md-sys-color-on-surface)]">
            <span className="font-semibold">Pro Tip:</span>{' '}
            <span className="text-[var(--md-sys-color-on-surface-variant)]">
              Stack certifications strategically — pair a cloud cert with a DevOps or security cert to maximize your market value by up to 35%.
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
