const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

class ApiError extends Error {
    constructor(message: string, public status: number, public data?: unknown) {
        super(message);
        this.name = 'ApiError';
    }
}

type CaseItem = {
    id: string;
    query_name?: string;
    query_age?: number;
    query_date?: string;
    query_location?: string;
    notes?: string;
    photo_path: string;
    face_embedding: number[];
    status: string;
    created_at: string;
    updated_at?: string;
    deleted_at?: string;
};

type SearchResult = {
    record_id: string;
    person_id: string;
    age: number;
    capture_year?: number;
    dataset: string;
    photo_path: string;
    face_similarity: number;
};

export type ReportCandidate = {
    rank: number;
    record_id: string;
    person_id: string;
    age: number;
    dataset: string;
    face_similarity: number;
    photo_path: string;
};

export type InvestigationReport = {
    case_id: string;
    query_name?: string;
    query_age?: number;
    query_location?: string;
    query_date?: string;
    generated_at: string;
    total_records: number;
    total_candidates: number;
    top_match_similarity: number;
    high_confidence: number;
    medium_confidence: number;
    low_confidence: number;
    summary: string;
    findings: string[];
    candidates: ReportCandidate[];
    recommendations: string[];
    next_steps: string[];
};

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = localStorage.getItem('access_token');
    const headers = new Headers(options.headers);

    if (options.body instanceof FormData) {
        headers.delete('Content-Type');
    } else if (!headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json');
    }

    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
    if (!response.ok) {
        const errorData = await response.text();
        let message = `HTTP ${response.status}`;
        try {
            const parsed = JSON.parse(errorData);
            if (typeof parsed?.detail === 'string') message = parsed.detail;
        } catch {
            // non-JSON error body; fall back to the status message
        }
        throw new ApiError(message, response.status, errorData);
    }
    if (response.status === 204) return undefined as T;
    return response.json();
}

export const authApi = {
    login: (credentials: { username: string; password: string }) =>
        request<{ access_token: string; token_type: string }>('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams(credentials).toString(),
        }),
    register: (data: { email: string; full_name: string; password: string }) =>
        request<{ access_token: string; token_type: string }>('/auth/register', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    me: () => request<{ id: string; email: string; full_name: string; created_at: string }>('/auth/me'),
};

export const casesApi = {
    list: (params?: { status?: string; limit?: number; offset?: number }) => {
        const q = new URLSearchParams();
        if (params?.status) q.set('status_filter', params.status);
        if (params?.limit) q.set('limit', String(params.limit));
        if (params?.offset) q.set('offset', String(params.offset));
        return request<CaseItem[]>(`/cases${q.toString() ? `?${q}` : ''}`);
    },
    get: (caseId: string) => request<CaseItem>(`/cases/${caseId}`),
    create: (data: {
        query_name: string;
        query_age?: number;
        query_date?: string;
        query_location?: string;
        notes?: string;
        face_embedding: number[];
        photo_path: string;
    }) => request<CaseItem>('/cases', { method: 'POST', body: JSON.stringify(data) }),
    update: (
        caseId: string,
        data: Partial<{
            query_name: string;
            query_age?: number;
            query_date?: string;
            query_location?: string;
            notes?: string;
            status: 'active' | 'archived';
        }>
    ) => request<CaseItem>(`/cases/${caseId}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (caseId: string) => request<void>(`/cases/${caseId}`, { method: 'DELETE' }),
    extractEmbedding: (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        return request<{ embedding: number[]; det_score: number; bbox: number[]; quality_pass: boolean; num_faces: number }>(
            '/cases/photo/embedding',
            { method: 'POST', headers: {}, body: formData }
        );
    },
    uploadPhoto: (file: File, options?: {
        create_case?: boolean;
        query_name?: string;
        query_age?: number;
        query_date?: string;
        query_location?: string;
        notes?: string;
    }) => {
        const formData = new FormData();
        formData.append('file', file);
        const q = new URLSearchParams();
        if (options?.create_case) q.set('create_case', 'true');
        if (options?.query_name) q.set('query_name', options.query_name);
        if (options?.query_age !== undefined) q.set('query_age', String(options.query_age));
        if (options?.query_date) q.set('query_date', options.query_date);
        if (options?.query_location) q.set('query_location', options.query_location);
        if (options?.notes) q.set('notes', options.notes);
        const qs = q.toString();
        return request<{ embedding: number[]; det_score: number; bbox: number[]; quality_pass: boolean; num_faces: number; case_id?: string }>(
            `/cases/photo/upload${qs ? `?${qs}` : ''}`,
            { method: 'POST', headers: {}, body: formData }
        );
    },
};

type SearchResponse = {
    query_id?: string;
    total_records: number;
    results: SearchResult[];
    quality_warning?: string;
};

export const searchApi = {
    search: (data: { face_embedding: number[]; top_k?: number; min_similarity?: number }) =>
        request<SearchResponse>('/search', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    searchByCase: (caseId: string, params?: { top_k?: number; min_similarity?: number }) => {
        const q = new URLSearchParams();
        if (params?.top_k) q.set('top_k', String(params.top_k));
        if (params?.min_similarity) q.set('min_similarity', String(params.min_similarity));
        return request<SearchResponse>(
            `/search/case/${caseId}${q.toString() ? `?${q}` : ''}`
        );
    },
    searchByPhoto: (file: File, params?: { top_k?: number; min_similarity?: number }) => {
        const formData = new FormData();
        formData.append('file', file);
        if (params?.top_k) formData.append('top_k', String(params.top_k));
        if (params?.min_similarity) formData.append('min_similarity', String(params.min_similarity));
        return request<SearchResponse>('/search/photo', {
            method: 'POST',
            headers: {},
            body: formData,
        });
    },
};

export const reportsApi = {
    generate: (caseId: string) =>
        request<InvestigationReport>(`/reports/${caseId}`),
};

export const healthApi = {
    check: () => request<{ status: string }>('/health'),
};

export { ApiError };
