'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button, Input, Label, Select, Textarea, Card, Spinner } from '@/components/ui';

interface ProjectType {
    type_id: string;
    display_name: string;
    description: string;
}

interface FormData {
    name: string;
    project_type: string;
    description: string;
    start_date: string;
    end_date: string;
}

interface FormErrors {
    name?: string;
    project_type?: string;
    start_date?: string;
    end_date?: string;
    general?: string;
}

export default function ProjectFormView() {
    const router = useRouter();
    const [projectTypes, setProjectTypes] = useState<ProjectType[]>([]);
    const [isLoadingTypes, setIsLoadingTypes] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errors, setErrors] = useState<FormErrors>({});
    const [formData, setFormData] = useState<FormData>({
        name: '',
        project_type: 'generic',
        description: '',
        start_date: '',
        end_date: '',
    });

    // Fetch project types on mount
    useEffect(() => {
        const fetchProjectTypes = async () => {
            try {
                const response = await fetch('/api/pm/project-types');
                if (response.ok) {
                    const data = await response.json();
                    setProjectTypes(data.project_types || []);
                    // Set default type if available
                    if (data.project_types?.length > 0) {
                        setFormData(prev => ({
                            ...prev,
                            project_type: data.project_types[0].type_id
                        }));
                    }
                }
            } catch (err) {
                console.error('Failed to fetch project types:', err);
            } finally {
                setIsLoadingTypes(false);
            }
        };

        fetchProjectTypes();
    }, []);

    const validateForm = (): boolean => {
        const newErrors: FormErrors = {};

        if (!formData.name.trim()) {
            newErrors.name = 'Project name is required';
        } else if (formData.name.length > 255) {
            newErrors.name = 'Project name must be 255 characters or less';
        }

        if (!formData.project_type) {
            newErrors.project_type = 'Please select a project type';
        }

        if (formData.start_date && formData.end_date) {
            const startDate = new Date(formData.start_date);
            const endDate = new Date(formData.end_date);
            if (endDate < startDate) {
                newErrors.end_date = 'End date must be after start date';
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleChange = (field: keyof FormData, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        // Clear error for this field when user types
        if (errors[field as keyof FormErrors]) {
            setErrors(prev => ({ ...prev, [field]: undefined }));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);
        setErrors({});

        try {
            const payload = {
                name: formData.name.trim(),
                project_type: formData.project_type,
                description: formData.description.trim(),
                start_date: formData.start_date || null,
                end_date: formData.end_date || null,
            };

            const response = await fetch('/api/pm/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Failed to create project');
            }

            // Success - navigate to projects list (client-side)
            router.push('/pm/projects');
        } catch (err) {
            setErrors({
                general: err instanceof Error ? err.message : 'An unexpected error occurred',
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleCancel = () => {
        router.push('/pm/projects');
    };

    const selectedType = projectTypes.find(t => t.type_id === formData.project_type);

    return (
        <div className="mx-auto max-w-2xl space-y-6 p-6">
            <div>
                <h1 className="text-2xl font-bold">Create New Project</h1>
                <p className="text-muted-foreground">
                    Fill in the details below to create a new project.
                </p>
            </div>

            {errors.general && (
                <div className="rounded-md bg-destructive/10 p-4 text-destructive">
                    {errors.general}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
                <Card className="p-6">
                    <div className="space-y-4">
                        {/* Project Name */}
                        <div className="space-y-2">
                            <Label htmlFor="name">
                                Project Name <span className="text-destructive">*</span>
                            </Label>
                            <Input
                                id="name"
                                placeholder="Enter project name"
                                value={formData.name}
                                onChange={(e) => handleChange('name', e.target.value)}
                                error={errors.name}
                                disabled={isSubmitting}
                            />
                        </div>

                        {/* Project Type */}
                        <div className="space-y-2">
                            <Label htmlFor="project_type">
                                Project Type <span className="text-destructive">*</span>
                            </Label>
                            {isLoadingTypes ? (
                                <div className="flex h-10 items-center">
                                    <Spinner size="sm" />
                                    <span className="ml-2 text-sm text-muted-foreground">
                                        Loading project types...
                                    </span>
                                </div>
                            ) : (
                                <>
                                    <Select
                                        id="project_type"
                                        value={formData.project_type}
                                        onChange={(value) => handleChange('project_type', value)}
                                        options={projectTypes.map(type => ({
                                            value: type.type_id,
                                            label: type.display_name,
                                        }))}
                                        error={errors.project_type}
                                        disabled={isSubmitting}
                                    />
                                    {selectedType && (
                                        <p className="text-sm text-muted-foreground">
                                            {selectedType.description}
                                        </p>
                                    )}
                                </>
                            )}
                        </div>

                        {/* Description */}
                        <div className="space-y-2">
                            <Label htmlFor="description">Description</Label>
                            <Textarea
                                id="description"
                                placeholder="Describe your project..."
                                value={formData.description}
                                onChange={(e) => handleChange('description', e.target.value)}
                                rows={4}
                                disabled={isSubmitting}
                            />
                        </div>
                    </div>
                </Card>

                <Card className="p-6">
                    <h2 className="mb-4 text-lg font-semibold">Timeline</h2>
                    <div className="grid gap-4 sm:grid-cols-2">
                        {/* Start Date */}
                        <div className="space-y-2">
                            <Label htmlFor="start_date">Start Date</Label>
                            <Input
                                id="start_date"
                                type="date"
                                value={formData.start_date}
                                onChange={(e) => handleChange('start_date', e.target.value)}
                                error={errors.start_date}
                                disabled={isSubmitting}
                            />
                        </div>

                        {/* End Date */}
                        <div className="space-y-2">
                            <Label htmlFor="end_date">End Date</Label>
                            <Input
                                id="end_date"
                                type="date"
                                value={formData.end_date}
                                onChange={(e) => handleChange('end_date', e.target.value)}
                                error={errors.end_date}
                                disabled={isSubmitting}
                            />
                        </div>
                    </div>
                </Card>

                {/* Actions */}
                <div className="flex justify-end gap-3">
                    <Button
                        type="button"
                        variant="outline"
                        onClick={handleCancel}
                        disabled={isSubmitting}
                    >
                        Cancel
                    </Button>
                    <Button type="submit" disabled={isSubmitting || isLoadingTypes}>
                        {isSubmitting ? (
                            <>
                                <Spinner size="sm" className="mr-2" />
                                Creating...
                            </>
                        ) : (
                            'Create Project'
                        )}
                    </Button>
                </div>
            </form>
        </div>
    );
}
