// CareerLens AI — Frontend API Client
// Connects to FastAPI backend at /api/*

const API_BASE = (import.meta.env.VITE_API_URL || 'https://careerlens-api-f74a.onrender.com').replace(/\/$/, '');

if (!import.meta.env.VITE_API_URL) {
  console.log("VITE_API_URL environment variable is not set. Defaulting to production backend:", API_BASE);
}

// ── Token Management ──────────────────────────────────────────
function getToken() {
  return localStorage.getItem('careerlens_token');
}

function setToken(token) {
  localStorage.setItem('careerlens_token', token);
}

export function clearToken() {
  localStorage.removeItem('careerlens_token');
  // Always flush the full cache on logout/token-clear so that
  // stale data from the previous user is NEVER served to the next user.
  _cache.clear();
}

// ── In-Memory Cache (5 min TTL for GET requests) ──────────────
const _cache = new Map()
const CACHE_TTL_MS = 5 * 60 * 1000 // 5 minutes

function getCached(key) {
  const entry = _cache.get(key)
  if (!entry) return null
  if (Date.now() - entry.ts > CACHE_TTL_MS) {
    _cache.delete(key)
    return null
  }
  return entry.data
}

function setCached(key, data) {
  _cache.set(key, { data, ts: Date.now() })
}

export function invalidateCache(prefix) {
  for (const key of _cache.keys()) {
    if (!prefix || key.startsWith(prefix)) _cache.delete(key)
  }
}

// ── Request Helper ────────────────────────────────────────────
async function request(path, options = {}) {
  const token = getToken()
  const headers = { ...(options.headers || {}) }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Don't set Content-Type for FormData (browser sets boundary automatically)
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const isGet = !options.method || options.method === 'GET'

  // Return cached response for GET requests
  if (isGet) {
    const cached = getCached(path)
    if (cached) return cached
  }

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 15000)

  let res
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
      signal: options.signal || controller.signal,
    })
  } finally {
    clearTimeout(timeoutId)
  }

  if (res.status === 401) {
    const hadToken = !!getToken()
    clearToken()
    if (hadToken) {
      window.dispatchEvent(new Event('auth:unauthorized'))
    }
    throw new Error('Session expired. Please log in again.')
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }

  const data = await res.json()

  // Cache successful GET responses
  if (isGet) setCached(path, data)

  return data
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

export async function forgotPassword(email) {
  return request('/api/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
}

export async function resetPassword(token, new_password) {
  return request('/api/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify({ token, new_password }),
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
  // Flush all cached data from any previous session before storing the new token.
  // This ensures no stale data from a previous logged-in user ever appears.
  _cache.clear();
  setToken(data.access_token);
  return data;
}

export async function loginWithGoogle({ credential, access_token, email, name } = {}) {
  const res = await fetch(`${API_BASE}/api/auth/google`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ credential, access_token, email, name }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Google sign-in failed');
  }

  const data = await res.json();
  _cache.clear();
  setToken(data.access_token);
  return data;
}

export function logoutUser() {
  clearToken(); // clearToken already clears the cache
}

export async function getCurrentUser() {
  const token = getToken();
  if (!token) {
    return null;
  }
  return request('/api/users/me');
}

export async function updateUserProfile(data) {
  invalidateCache('/api/users/me');
  return request('/api/users/me', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function changeUserPassword(current_password, new_password) {
  return request('/api/users/change-password', {
    method: 'POST',
    body: JSON.stringify({ current_password, new_password }),
  });
}

export async function deleteUserAccount() {
  clearToken();
  invalidateCache();
  return request('/api/users/me', {
    method: 'DELETE',
  });
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

// ── Certifications ────────────────────────────────────────────
export async function getCertifications() {
  return request('/api/certifications');
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

// ── Feedback API ──────────────────────────────────────────────

export async function submitFeedback(data) {
  invalidateCache('/api/feedback');
  return request('/api/feedback', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function getMyFeedback() {
  return request('/api/feedback/me');
}

export async function getFeedbackStats() {
  return request('/api/feedback/stats');
}

// ── Admin Command Center APIs ────────────────────────────────
export async function adminGetSummary() {
  return request('/api/admin/summary');
}

export async function adminGetUsers({ q, role, verified, limit = 50, offset = 0 } = {}) {
  const params = new URLSearchParams();
  if (q) params.append('q', q);
  if (role) params.append('role', role);
  if (verified !== undefined && verified !== null && verified !== '') params.append('verified', verified);
  params.append('limit', limit);
  params.append('offset', offset);
  return request(`/api/admin/users?${params.toString()}`);
}

export async function adminGetUserStats() {
  return request('/api/admin/users/stats');
}

export async function adminUpdateUserRole(userId, role) {
  invalidateCache('/api/admin/users');
  return request(`/api/admin/users/${userId}/role`, {
    method: 'PUT',
    body: JSON.stringify({ role })
  });
}

export async function adminDeleteUser(userId) {
  invalidateCache('/api/admin/users');
  return request(`/api/admin/users/${userId}`, {
    method: 'DELETE'
  });
}

export async function adminChangePassword({ current_password, new_password }) {
  return request('/api/admin/change-password', {
    method: 'POST',
    body: JSON.stringify({ current_password, new_password })
  });
}

export async function adminGetCollectorStats() {
  return request('/api/admin/collector/stats');
}

export async function adminTriggerCollector() {
  invalidateCache('/api/admin/collector');
  return request('/api/admin/collector/trigger', {
    method: 'POST'
  });
}

export async function adminGetOpportunitiesAudit({
  status_filter = 'active',
  q = '',
  source = '',
  time_range = 'all',
  limit = 50,
  offset = 0
} = {}) {
  const params = new URLSearchParams();
  if (status_filter) params.append('status_filter', status_filter);
  if (q) params.append('q', q);
  if (source) params.append('source', source);
  if (time_range) params.append('time_range', time_range);
  params.append('limit', limit);
  params.append('offset', offset);
  return request(`/api/admin/opportunities/audit?${params.toString()}`);
}

export async function adminUpdateOpportunityStatus(oppId, payload) {
  invalidateCache('/api/admin/opportunities');
  return request(`/api/admin/opportunities/${oppId}/status`, {
    method: 'PUT',
    body: JSON.stringify(payload)
  });
}

export async function adminGetPageAnalytics(days = 30) {
  return request(`/api/admin/analytics/pages?days=${days}`);
}

export async function recordPageView(path, pageName = '') {
  try {
    return await request('/api/analytics/pageview', {
      method: 'POST',
      body: JSON.stringify({ path, page_name: pageName })
    });
  } catch (_) {
    // Non-blocking telemetry
    return null;
  }
}

export async function adminGetFeedback({ status, category, limit = 100, offset = 0 } = {}) {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (category) params.append('category', category);
  params.append('limit', limit);
  params.append('offset', offset);
  return request(`/api/admin/feedback?${params.toString()}`);
}

export async function adminUpdateFeedback(feedbackId, data) {
  invalidateCache('/api/feedback');
  return request(`/api/admin/feedback/${feedbackId}`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  });
}

export async function adminGetCollectorsHealth() {
  return request('/api/admin/collectors/health');
}

// ── Programmatic SEO API ──────────────────────────────────────
export async function getCategorySeoData(categoryType = 'role', slug = 'software-engineer') {
  return request(`/api/seo/${categoryType}/${slug}`);
}

export async function getRoleSeoData(slug) {
  return request(`/api/seo/role/${slug}`);
}

// ── Utility Exports ───────────────────────────────────────────
export { getToken, setToken, API_BASE };

