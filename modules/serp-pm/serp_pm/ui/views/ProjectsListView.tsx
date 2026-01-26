'use client';

import { useState, useEffect } from 'react';
import { Table, Badge, Spinner, Empty } from '@/components/ui';

interface Project {
    id: string;
    name: string;
    project_type: string;
    description: string;
    status: string;
    start_date: string | null;
    end_date: string | null;
    created_at: string;
    is_archived: boolean;
}

export default function ProjectsListView() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchProjects = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch('/api/pm/projects');
            if (!response.ok) {
                throw new Error('Failed to fetch projects');
            }
            const data = await response.json();
            setProjects(data.items || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchProjects();
    }, []);

    const getStatusBadgeVariant = (status: string) => {
        switch (status.toLowerCase()) {
            case 'active':
                return 'default';
            case 'completed':
                return 'success';
            case 'on_hold':
                return 'warning';
            case 'cancelled':
                return 'destructive';
            default:
                return 'secondary';
        }
    };

    const formatDate = (date: string | null) => {
        if (!date) return '-';
        return new Date(date).toLocaleDateString();
    };

    if (isLoading) {
        return (
            <div className="flex h-64 items-center justify-center">
                <Spinner size="lg" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="rounded-md bg-destructive/10 p-4 text-destructive">
                Error: {error}
            </div>
        );
    }

    if (projects.length === 0) {
        return (
            <Empty
                title="No projects yet"
                description="Create your first project to get started"
            />
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Projects</h1>
                <div className="text-sm text-muted-foreground">
                    {projects.length} {projects.length === 1 ? 'project' : 'projects'}
                </div>
            </div>

            <Table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Start Date</th>
                        <th>End Date</th>
                        <th>Created</th>
                    </tr>
                </thead>
                <tbody>
                    {projects.map((project) => (
                        <tr key={project.id}>
                            <td className="font-medium">{project.name}</td>
                            <td className="capitalize">{project.project_type}</td>
                            <td>
                                <Badge variant={getStatusBadgeVariant(project.status)}>
                                    {project.status.replace('_', ' ')}
                                </Badge>
                            </td>
                            <td>{formatDate(project.start_date)}</td>
                            <td>{formatDate(project.end_date)}</td>
                            <td>{formatDate(project.created_at)}</td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </div>
    );
}
