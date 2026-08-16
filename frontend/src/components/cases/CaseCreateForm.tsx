import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import { Loader2, AlertCircle, CheckCircle2, UploadCloud, User } from 'lucide-react';
import { useUploadPhoto } from '../../hooks/useCases';
import { EASE } from '../motion/primitives';

interface FormData {
    query_name: string;
    query_age: string;
    query_date: string;
    query_location: string;
    notes: string;
    file: File | null;
}

interface FormErrors {
    query_name?: string;
    query_age?: string;
    file?: string;
    general?: string;
}

const inputClass =
    'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-brand-500/40 focus:border-brand-500/50 transition-all';

const labelClass = 'block text-sm font-medium text-white/70';

export function CaseCreateForm() {
    const navigate = useNavigate();
    const reducedMotion = useReducedMotion();
    const uploadMutation = useUploadPhoto();

    const [formData, setFormData] = useState<FormData>({
        query_name: '',
        query_age: '',
        query_date: '',
        query_location: '',
        notes: '',
        file: null,
    });
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);

    const [errors, setErrors] = useState<FormErrors>({});
    const [step, setStep] = useState<'upload' | 'details' | 'processing' | 'success'>('upload');

    const validateFile = useCallback((file: File | null): string | undefined => {
        if (!file) return 'Please upload an image';
        if (!file.type.startsWith('image/')) return 'File must be an image';
        if (file.size > 10 * 1024 * 1024) return 'File size must not exceed 10MB';
        return undefined;
    }, []);

    const handleFileChange = useCallback((file: File | null) => {
        setFormData((prev) => ({ ...prev, file }));
        if (file) {
            setPreviewUrl(URL.createObjectURL(file));
        } else {
            setPreviewUrl(null);
        }
        setErrors((prev) => ({ ...prev, file: validateFile(file) }));
    }, [validateFile]);

    const handleInputChange = useCallback((field: keyof FormData) => (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        const value = e.target.value;
        setFormData((prev) => ({ ...prev, [field]: value }));
        if (errors[field as keyof FormErrors]) {
            setErrors((prev) => ({ ...prev, [field]: undefined }));
        }
    }, [errors]);

    const handleFileSubmit = useCallback(async () => {
        const fileError = validateFile(formData.file);
        if (fileError) {
            setErrors((prev) => ({ ...prev, file: fileError }));
            return;
        }

        setStep('processing');
        setErrors({});

        try {
            const result = await uploadMutation.mutateAsync({
                file: formData.file!,
                options: {
                    create_case: false,
                },
            });

            if (!result.quality_pass) {
                setErrors({ file: 'Face quality check failed. Please upload a clearer image.' });
                setStep('upload');
                return;
            }

            if (result.num_faces !== 1) {
                setErrors({
                    file: result.num_faces === 0
                        ? 'No face detected. Please upload an image with a visible face.'
                        : 'Multiple faces detected. Please upload an image with only one face.',
                });
                setStep('upload');
                return;
            }

            setStep('details');
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to process image';
            setErrors({ general: message });
            setStep('upload');
        }
    }, [formData.file, uploadMutation, validateFile]);

    const handleFinalSubmit = useCallback(async () => {
        const newErrors: FormErrors = {};
        if (!formData.query_name.trim()) {
            newErrors.query_name = 'Name is required';
        }
        if (formData.query_age && (isNaN(Number(formData.query_age)) || Number(formData.query_age) < 0 || Number(formData.query_age) > 100)) {
            newErrors.query_age = 'Age must be between 0 and 100';
        }

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }

        setStep('processing');
        setErrors({});

        try {
            const result = await uploadMutation.mutateAsync({
                file: formData.file!,
                options: {
                    create_case: true,
                    query_name: formData.query_name.trim(),
                    query_age: formData.query_age ? Number(formData.query_age) : undefined,
                    query_date: formData.query_date || undefined,
                    query_location: formData.query_location.trim() || undefined,
                    notes: formData.notes.trim() || undefined,
                },
            });

            if (result.case_id) {
                setStep('success');
                setTimeout(() => {
                    navigate(`/cases/${result.case_id}`);
                }, 1500);
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to create case';
            setErrors({ general: message });
            setStep('details');
        }
    }, [formData, uploadMutation, navigate]);

    const handleReset = useCallback(() => {
        setFormData({
            query_name: '',
            query_age: '',
            query_date: '',
            query_location: '',
            notes: '',
            file: null,
        });
        setPreviewUrl(null);
        setErrors({});
        setStep('upload');
    }, []);

    const stepLabels = ['Photo Upload', 'Case Details', 'Review'];

    if (step === 'success') {
        return (
            <div className="card-glass rounded-2xl p-8">
                <div className="text-center py-8">
                    <motion.div
                        initial={reducedMotion ? false : { scale: 0.5, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                        className="inline-flex"
                    >
                        <CheckCircle2 className="h-16 w-16 text-emerald-400" />
                    </motion.div>
                    <motion.h2
                        className="mt-4 text-xl font-display font-semibold text-white"
                        initial={reducedMotion ? false : { opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2, duration: 0.4 }}
                    >
                        Case Created Successfully
                    </motion.h2>
                    <motion.p
                        className="mt-2 text-white/50 text-sm"
                        initial={reducedMotion ? false : { opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3, duration: 0.4 }}
                    >
                        Redirecting to case details...
                    </motion.p>
                </div>
            </div>
        );
    }

    return (
        <div className="card-glass rounded-2xl p-6 lg:p-8">
            <div className="flex items-center gap-2 mb-2">
                {stepLabels.map((label, i) => {
                    const currentIdx = step === 'upload' ? 0 : step === 'details' ? 1 : 2;
                    const isDone = i < currentIdx;
                    const isCurrent = i === currentIdx;
                    return (
                        <div key={label} className="flex items-center gap-2">
                            {i > 0 && <div className={`h-px w-8 ${isDone || isCurrent ? 'bg-brand-400' : 'bg-white/10'}`} />}
                            <span
                                className={`text-xs font-medium ${
                                    isCurrent ? 'text-brand-300' : isDone ? 'text-emerald-400' : 'text-white/30'
                                }`}
                            >
                                {label}
                            </span>
                        </div>
                    );
                })}
            </div>
            <p className="text-sm text-white/40 mb-6">
                {step === 'upload' && 'Upload a photo of the missing child to begin'}
                {step === 'details' && 'Add case details and information'}
                {step === 'processing' && 'Processing your request...'}
            </p>

            <div className="space-y-6">
                {errors.general && (
                    <div className="flex items-start gap-3 p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl" role="alert">
                        <AlertCircle className="h-5 w-5 text-rose-400 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-sm font-medium text-rose-300">Error</p>
                            <p className="text-sm text-rose-300/70">{errors.general}</p>
                        </div>
                    </div>
                )}

                <AnimatePresence mode="wait">
                    {step === 'upload' && (
                        <motion.div
                            key="upload"
                            className="space-y-6"
                            initial={reducedMotion ? false : { opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.3, ease: EASE }}
                        >
                            <label className="flex flex-col items-center justify-center border-2 border-dashed rounded-2xl p-10 cursor-pointer transition-colors hover:border-white/20 border-white/10">
                                <input
                                    type="file"
                                    accept="image/jpeg,image/png,image/webp"
                                    onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
                                    className="sr-only"
                                />
                                {previewUrl ? (
                                    <>
                                        <img src={previewUrl} alt="Upload preview" className="h-32 w-32 object-cover rounded-xl mb-4" />
                                        <p className="text-sm text-white/60 font-medium">Click to change photo</p>
                                    </>
                                ) : (
                                    <>
                                        <div className="h-14 w-14 rounded-2xl bg-white/5 flex items-center justify-center mb-4">
                                            <UploadCloud className="h-6 w-6 text-white/40" />
                                        </div>
                                        <p className="text-sm font-medium text-white/70">Drop an image here</p>
                                        <p className="text-xs text-white/40 mt-1">or click to browse</p>
                                        <p className="text-xs text-white/30 mt-3">JPG, PNG, WEBP · max 10MB</p>
                                    </>
                                )}
                            </label>
                            {errors.file && (
                                <p className="flex items-center gap-1.5 text-sm text-rose-400">
                                    <AlertCircle className="h-4 w-4" />
                                    {errors.file}
                                </p>
                            )}

                            <div className="flex justify-end">
                                <button
                                    onClick={handleFileSubmit}
                                    disabled={!formData.file || uploadMutation.isPending}
                                    className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-brand-500 to-violet-600 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-glow-brand hover:-translate-y-0.5 transition-all duration-200"
                                >
                                    {uploadMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                                    Continue
                                </button>
                            </div>
                        </motion.div>
                    )}

                    {step === 'details' && (
                        <motion.div
                            key="details"
                            className="space-y-5"
                            initial={reducedMotion ? false : { opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.3, ease: EASE }}
                        >
                            <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                                {previewUrl && (
                                    <img
                                        src={previewUrl}
                                        alt="Uploaded photo"
                                        className="h-16 w-16 object-cover rounded-lg"
                                    />
                                )}
                                <div>
                                    <p className="text-sm font-medium text-white/80">Photo uploaded</p>
                                    <button
                                        onClick={() => setStep('upload')}
                                        className="text-sm text-brand-400 hover:text-brand-300 mt-1 transition-colors"
                                    >
                                        Change photo
                                    </button>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label htmlFor="query_name" className={labelClass}>
                                    Child's Name *
                                </label>
                                <input
                                    id="query_name"
                                    type="text"
                                    value={formData.query_name}
                                    onChange={handleInputChange('query_name')}
                                    placeholder="Enter name or identifier"
                                    required
                                    className={inputClass}
                                />
                                {errors.query_name && (
                                    <p className="flex items-center gap-1.5 text-sm text-rose-400">
                                        <AlertCircle className="h-4 w-4" />
                                        {errors.query_name}
                                    </p>
                                )}
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label htmlFor="query_age" className={labelClass}>
                                        Age (at time of photo)
                                    </label>
                                    <input
                                        id="query_age"
                                        type="number"
                                        min={0}
                                        max={100}
                                        value={formData.query_age}
                                        onChange={handleInputChange('query_age')}
                                        placeholder="e.g., 12"
                                        className={inputClass}
                                    />
                                    {errors.query_age && (
                                        <p className="flex items-center gap-1.5 text-sm text-rose-400">
                                            <AlertCircle className="h-4 w-4" />
                                            {errors.query_age}
                                        </p>
                                    )}
                                </div>

                                <div className="space-y-2">
                                    <label htmlFor="query_date" className={labelClass}>
                                        Date of Photo
                                    </label>
                                    <input
                                        id="query_date"
                                        type="date"
                                        value={formData.query_date}
                                        onChange={handleInputChange('query_date')}
                                        className={`${inputClass} [color-scheme:dark]`}
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label htmlFor="query_location" className={labelClass}>
                                    Location
                                </label>
                                <input
                                    id="query_location"
                                    type="text"
                                    value={formData.query_location}
                                    onChange={handleInputChange('query_location')}
                                    placeholder="Where was the photo taken?"
                                    className={inputClass}
                                />
                            </div>

                            <div className="space-y-2">
                                <label htmlFor="notes" className={labelClass}>
                                    Notes
                                </label>
                                <textarea
                                    id="notes"
                                    value={formData.notes}
                                    onChange={handleInputChange('notes')}
                                    placeholder="Additional information about the case..."
                                    rows={3}
                                    className={`${inputClass} resize-none`}
                                />
                            </div>

                            <div className="flex items-center justify-between pt-4">
                                <button
                                    onClick={handleReset}
                                    className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white/70 text-sm font-medium hover:bg-white/10 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleFinalSubmit}
                                    disabled={!formData.query_name.trim() || uploadMutation.isPending}
                                    className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-brand-500 to-violet-600 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-glow-brand hover:-translate-y-0.5 transition-all duration-200"
                                >
                                    {uploadMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <User className="h-4 w-4" />}
                                    Create Case
                                </button>
                            </div>
                        </motion.div>
                    )}

                    {step === 'processing' && (
                        <motion.div
                            key="processing"
                            className="flex flex-col items-center justify-center py-12"
                            initial={reducedMotion ? false : { opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                        >
                            <div className="relative">
                                <Loader2 className="h-12 w-12 text-brand-400 animate-spin" />
                                <div className="absolute inset-0 h-12 w-12 rounded-full bg-brand-400/20 blur-xl animate-pulse" />
                            </div>
                            <p className="mt-6 text-white/60">
                                {uploadMutation.isPending
                                    ? 'Creating case and processing face data...'
                                    : 'Processing...'}
                            </p>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
