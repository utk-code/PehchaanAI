/** Search hooks for PehchaanAI Frontend */

import { useMutation, useQuery } from '@tanstack/react-query';
import { searchApi } from '../services/api';

export function useSearch() {
    return useMutation({
        mutationFn: searchApi.search,
    });
}

export function useSearchByCase(caseId: string, params?: { top_k?: number; min_similarity?: number }) {
    return useQuery({
        queryKey: ['search', 'case', caseId, params],
        queryFn: () => searchApi.searchByCase(caseId, params),
        enabled: !!caseId,
        staleTime: 60 * 1000, // 1 minute
    });
}

export function useSearchByPhoto() {
    return useMutation({
        mutationFn: ({ file, params }: { file: File; params?: { top_k?: number; min_similarity?: number } }) =>
            searchApi.searchByPhoto(file, params),
    });
}