/** Case management hooks for PehchaanAI Frontend */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { casesApi } from '../services/api';

export function useCases(params?: { status?: string; limit?: number; offset?: number }) {
    return useQuery({
        queryKey: ['cases', params],
        queryFn: () => casesApi.list(params),
        staleTime: 30 * 1000, // 30 seconds
    });
}

export function useCase(caseId: string) {
    return useQuery({
        queryKey: ['case', caseId],
        queryFn: () => casesApi.get(caseId),
        enabled: !!caseId,
        staleTime: 30 * 1000,
    });
}

export function useCreateCase() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: casesApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['cases'] });
        },
    });
}

export function useUpdateCase() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ caseId, data }: { caseId: string; data: Parameters<typeof casesApi.update>[1] }) =>
            casesApi.update(caseId, data),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['cases'] });
            queryClient.invalidateQueries({ queryKey: ['case', variables.caseId] });
        },
    });
}

export function useDeleteCase() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: casesApi.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['cases'] });
        },
    });
}

export function useExtractEmbedding() {
    return useMutation({
        mutationFn: casesApi.extractEmbedding,
    });
}

export function useUploadPhoto() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ file, options }: { file: File; options?: Parameters<typeof casesApi.uploadPhoto>[1] }) =>
            casesApi.uploadPhoto(file, options),
        onSuccess: (data) => {
            if (data.case_id) {
                queryClient.invalidateQueries({ queryKey: ['cases'] });
            }
        },
    });
}