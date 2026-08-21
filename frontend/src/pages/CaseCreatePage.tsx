import { CaseCreateForm } from '../components/cases/CaseCreateForm';

export function CaseCreatePage() {
    return (
        <div className="max-w-3xl mx-auto">
            <div className="mb-6">
                <div className="flex items-center gap-2 mb-1">
                    <span className="mono-label">New Intake / Dossier</span>
                </div>
                <h1 className="text-3xl lg:text-4xl font-display font-bold text-white tracking-tight leading-none">Create New Case</h1>
                <p className="mt-2 text-white/50 text-sm">
                    Upload a photo and provide case details to begin investigation
                </p>
            </div>
            <CaseCreateForm />
        </div>
    );
}
