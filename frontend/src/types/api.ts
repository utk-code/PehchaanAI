/** API Type Definitions for PehchaanAI Frontend */

// Auth types
export interface User {
    id: string;
    email: string;
    full_name: string;
    created_at: string;
}

export interface Token {
    access_token: string;
    token_type: string;
}

export interface LoginCredentials {
    username: string;
    password: string;
}

export interface RegisterData {
    email: string;
    full_name: string;
    password: string;
}

// Case types
export interface CaseCreate {
    query_name: string;
    query_age?: number;
    query_date?: string; // ISO date string
    query_location?: string;
    notes?: string;
    face_embedding: number[];
    photo_path: string;
}

export interface CaseUpdate {
    query_name?: string;
    query_age?: number;
    query_date?: string;
    query_location?: string;
    notes?: string;
    status?: 'active' | 'archived';
}

export interface CaseListItem {
    id: string;
    query_name?: string;
    query_age?: number;
    query_date?: string;
    status: string;
    created_at: string;
}

export interface CaseRead extends CaseListItem {
    investigator_id: string;
    query_location?: string;
    notes?: string;
    photo_path: string;
    face_embedding: number[];
    updated_at: string;
    deleted_at?: string;
}

// Face embedding types
export interface EmbeddingResponse {
    embedding: number[];
    det_score: number;
    bbox: number[];
    quality_pass: boolean;
    num_faces: number;
}

export interface PhotoUploadResponse extends EmbeddingResponse {
    case_id?: string;
}

// Search types
export interface SearchResult {
    record_id: string;
    person_id: string;
    age: number;
    capture_year?: number;
    dataset: string;
    photo_path: string;
    face_similarity: number;
}

export interface SearchResponse {
    query_id?: string;
    total_records: number;
    results: SearchResult[];
}

export interface SearchRequest {
    face_embedding: number[];
    top_k?: number;
    min_similarity?: number;
}