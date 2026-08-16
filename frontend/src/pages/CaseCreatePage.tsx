import { CaseCreateForm } from '../components/cases/CaseCreateForm';

export function CaseCreatePage() {
    return (
        <div className="max-w-3xl mx-auto">
            <div className="mb-6">
                <h1 className="text-2xl lg:text-3xl font-display font-bold text-white tracking-tight">Create New Case</h1>
                <p className="mt-1 text-white/50 text-sm">
                    Upload a photo and provide case details to begin investigation
                </p>
            </div>
            <CaseCreateForm />
        </div>
    );
}
