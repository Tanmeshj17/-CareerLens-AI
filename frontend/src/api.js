// CareerLens AI — Frontend API Client
// Connects to FastAPI backend at /api/*

const API_BASE = import.meta.env.VITE_API_URL;

if (!API_BASE) {
  console.error("VITE_API_URL environment variable is not set!");
}

// ── Token Management ──────────────────────────────────────────
function getToken() {
  return localStorage.getItem('careerlens_token');
}

function setToken(token) {
  localStorage.setItem('careerlens_token', token);
}

function clearToken() {
  localStorage.removeItem('careerlens_token');
}

// ── Request Helper ────────────────────────────────────────────
async function request(path, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData (browser sets boundary automatically)
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    const hadToken = !!getToken();
    clearToken();
    if (hadToken) {
      window.dispatchEvent(new Event('auth:unauthorized'));
    }
    throw new Error('Session expired. Please log in again.');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────
export async function registerUser(email, full_name, password) {
  return request('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, full_name, password }),
  });
}

export async function verifyEmail(token) {
  return request('/api/auth/verify', {
    method: 'POST',
    body: JSON.stringify({ token }),
  });
}

export async function resendVerificationEmail(email) {
  return request('/api/auth/resend-verification', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
}

export async function loginUser(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const res = await fetch(`${API_BASE}/api/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString(),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Login failed');
  }

  const data = await res.json();
  setToken(data.access_token);
  return data;
}

export function logoutUser() {
  clearToken();
}

export async function getCurrentUser() {
  const token = getToken();
  if (!token) {
    return null;
  }
  return request('/api/users/me');
}

// ── Opportunities ─────────────────────────────────────────────
export async function getOpportunities(params = {}) {
  const q = new URLSearchParams()
  for (const [key, val] of Object.entries(params)) {
    if (val !== undefined && val !== null) q.append(key, val)
  }
  return request(`/api/opportunities?${q.toString()}`)
}

export async function createOpportunity(data) {
  return request('/api/opportunities', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getAutocomplete(query) {
  return request(`/api/search/suggestions?q=${encodeURIComponent(query)}`)
}

export async function getOpportunityDetails(id) {
  return request(`/api/opportunities/${id}`)
}

export async function getOpportunitySources(id) {
  return request(`/api/opportunities/${id}/sources`)
}

export async function getLearningRecommendations(role) {
  return request(`/api/learning/recommendations?role=${encodeURIComponent(role)}`)
}

export async function getCoverageReport() {
  return request(`/api/coverage/report`)
}

// ── Applications ──────────────────────────────────────────────
export async function getApplications() {
  return request('/api/applications');
}

export async function createApplication(data) {
  return request('/api/applications', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateApplication(appId, data) {
  return request(`/api/applications/${appId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// ── Resumes ───────────────────────────────────────────────────
export async function analyzeResume(file) {
  const formData = new FormData();
  formData.append('file', file);
  return request('/api/resumes/analyze', {
    method: 'POST',
    body: formData,
  });
}

export async function getResumes() {
  return request('/api/resumes');
}

export async function getResumeProfile(resumeId) {
  return request(`/api/resumes/${resumeId}/profile`);
}

export async function getResumeGapAnalysis(resumeId) {
  return request(`/api/resumes/${resumeId}/gap-analysis`);
}

export async function getResumeReadiness(resumeId) {
  return request(`/api/resumes/${resumeId}/readiness`);
}

// ── Match Scores ──────────────────────────────────────────────
export async function createMatchScore(opportunityId) {
  return request(`/api/match/${opportunityId}`, { method: 'POST' });
}

export async function getMatchScores() {
  return request('/api/match/scores');
}

// ── Insights & Analytics ──────────────────────────────────────
export async function getInsightsStats() {
  return request('/api/insights/stats');
}

export async function getInsightsSkills() {
  return request('/api/insights/skills');
}

export async function getInsightsCompanies() {
  return request('/api/insights/companies');
}

export async function getInsightsLocations() {
  return request('/api/insights/locations');
}

export async function getInsightsTrends() {
  return request('/api/insights/trends');
}

export async function getInsightsSalary() {
  return request('/api/insights/salary');
}

export async function getFastGrowingCareers() {
  return request('/api/insights/fast-growing');
}

// ── Dashboard ─────────────────────────────────────────────────
export async function getDashboardStats() {
  return request('/api/dashboard/stats');
}

// ── Phase 3: Pipelines ────────────────────────────────────────
export async function getPipelineStatus() {
  return request('/api/pipeline/status');
}

export async function getPipelineHistory(skip = 0, limit = 20) {
  return request(`/api/pipeline/history?skip=${skip}&limit=${limit}`);
}

export async function triggerPipeline(pipelineName) {
  return request(`/api/pipeline/run/${pipelineName}`, { method: 'POST' });
}

export async function getPipelineStats() {
  return request('/api/pipeline/stats');
}

// ── Phase 3: Learning Resources ───────────────────────────────
export async function getFreeResources() {
  return request('/api/learning/free');
}

export async function getResources({ q, category, difficulty, is_free, skip, limit } = {}) {
  const params = new URLSearchParams();
  if (q) params.append('q', q);
  if (category && category !== 'All') params.append('category', category);
  if (difficulty && difficulty !== 'All') params.append('difficulty', difficulty);
  if (is_free !== undefined && is_free !== null) params.append('is_free', is_free);
  if (skip != null) params.append('skip', skip);
  if (limit != null) params.append('limit', limit);
  return request(`/api/resources?${params.toString()}`);
}

export async function getResourceCategories() {
  return request('/api/resources/categories');
}

// ── Health ────────────────────────────────────────────────────
export async function healthCheck() {
  return request('/api/health');
}

// ── Phase 4: Career Intelligence & Roadmaps ───────────────────
export async function getCareerRoadmap(role) {
  return request(`/api/roadmaps/${encodeURIComponent(role)}`);
}

export async function getResourceRecommendations(missingSkills) {
  return request(`/api/resources/recommendations?missing_skills=${encodeURIComponent(missingSkills)}`);
}

export async function getInterviewPrep(role) {
  return request(`/api/interview-prep/${encodeURIComponent(role)}`);
}

// ── Phase 8.5: Personalization & Matching ──────────────────────
export async function getRecommendedOpportunities(params = {}) {
  const q = new URLSearchParams()
  for (const [key, val] of Object.entries(params)) {
    if (val !== undefined && val !== null) q.append(key, val)
  }
  return request(`/api/opportunities/recommended?${q.toString()}`)
}

export async function getJobMatch(opportunityId) {
  return request(`/api/match/job/${opportunityId}`);
}

export async function getGapAnalysis(targetRole) {
  return request(`/api/skills/gap-analysis?target_role=${encodeURIComponent(targetRole)}`);
}

export async function getReadiness() {
  return request(`/api/readiness`);
}

export async function getProfileCompleteness() {
  return request(`/api/profile/completeness`);
}

export async function getCareerProfile() {
  return request(`/api/profile/career`);
}

export async function createCareerProfile(data) {
  return request(`/api/profile/career`, {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function updateCareerProfile(data) {
  return request(`/api/profile/career`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

export async function getSkillProfile() {
  return request(`/api/profile/skills`);
}

export async function addSkill(data) {
  return request(`/api/profile/skills`, {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function updateSkill(skillId, data) {
  return request(`/api/profile/skills/${skillId}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

export async function deleteSkill(skillId) {
  return request(`/api/profile/skills/${skillId}`, {
    method: 'DELETE'
  });
}

export async function updatePreferences(data) {
  return request(`/api/profile/preferences`, {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

// ── Utility Exports ───────────────────────────────────────────
export { getToken, setToken, clearToken, API_BASE };
