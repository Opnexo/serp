'use client';

import { useState, useEffect } from 'react';
import {
    Table,
    TableHeader,
    TableBody,
    TableRow,
    TableHead,
    TableCell,
    Badge,
    Spinner,
    Empty,
} from '@/components/ui';

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
                <TableHeader>
                    <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Start Date</TableHead>
                        <TableHead>End Date</TableHead>
                        <TableHead>Created</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {projects.map((project) => (
                        <TableRow key={project.id}>
                            <TableCell className="font-medium">{project.name}</TableCell>
                            <TableCell className="capitalize">{project.project_type}</TableCell>
                            <TableCell>
                                <Badge variant={getStatusBadgeVariant(project.status)}>
                                    {project.status.replace('_', ' ')}
                                </Badge>
                            </TableCell>
                            <TableCell>{formatDate(project.start_date)}</TableCell>
                            <TableCell>{formatDate(project.end_date)}</TableCell>
                            <TableCell>{formatDate(project.created_at)}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}
