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
    Button,
    Input,
    Card,
    CardContent,
} from '@/components/ui';
import { FolderOpen, FileText, LayoutTemplate, Search, ArrowRight } from 'lucide-react';

interface Project {
    id: string;
    name: string;
    project_type: string;
    status: string;
    updated_at: string;
}

interface ProjectStats {
    total_documents: number;
    total_versions: number;
    by_status: Record<string, number>;
}

export default function DMProjectsListView() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [stats, setStats] = useState<Record<string, ProjectStats>>({});
    const [isLoading, setIsLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState<string | null>(null);

    const fetchProjects = async () => {
        setIsLoading(true);
        setError(null);
        try {
            // Fetch projects from PM module
            const response = await fetch('/api/pm/projects');
            if (!response.ok) {
                throw new Error('Failed to fetch projects');
            }
            const data = await response.json();
            const items = data.items || [];
            setProjects(items);

            // Fetch stats for each project (could be optimized with a batch endpoint later)
            const statsMap: Record<string, ProjectStats> = {};
            await Promise.all(
                items.map(async (p: Project) => {
                    try {
                        const statsRes = await fetch(`/api/dm/projects/${p.id}/stats`);
                        if (statsRes.ok) {
                            statsMap[p.id] = await statsRes.json();
                        }
                    } catch (e) {
                        console.error(`Failed to fetch stats for project ${p.id}`, e);
                    }
                })
            );
            setStats(statsMap);

        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchProjects();
    }, []);

    const filteredProjects = projects.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.project_type.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getStatusBadgeVariant = (status: string) => {
        switch (status.toLowerCase()) {
            case 'active': return 'default';
            case 'completed': return 'success';
            case 'on_hold': return 'warning';
            case 'cancelled': return 'destructive';
            default: return 'secondary';
        }
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

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Document Projects</h1>
                    <p className="text-muted-foreground">
                        Select a project to manage its documents
                    </p>
                </div>
            </div>

            <div className="flex items-center gap-4">
                <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search projects..."
                        className="pl-9"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {filteredProjects.length === 0 ? (
                <Empty
                    title={searchTerm ? "No matching projects" : "No projects found"}
                    description={searchTerm ? "Try adjusting your search criteria" : "Projects created in the Project Management module will appear here"}
                    icon={<FolderOpen className="h-10 w-10 text-muted-foreground" />}
                />
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredProjects.map((project) => {
                        const projectStats = stats[project.id];
                        return (
                            <Card
                                key={project.id}
                                className="group hover:border-primary/50 transition-colors cursor-pointer"
                                onClick={() => window.location.href = `/dm/projects/${project.id}`}
                            >
                                <CardContent className="p-6">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="space-y-1">
                                            <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
                                                {project.name}
                                            </h3>
                                            <div className="flex gap-2">
                                                <Badge variant="outline" className="text-xs">
                                                    {project.project_type}
                                                </Badge>
                                                <Badge variant={getStatusBadgeVariant(project.status)} className="text-xs">
                                                    {project.status.replace('_', ' ')}
                                                </Badge>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4 py-4 border-t border-b mb-4">
                                        <div className="text-center">
                                            <div className="text-2xl font-bold text-primary">
                                                {projectStats?.total_documents || 0}
                                            </div>
                                            <div className="text-xs text-muted-foreground flex items-center justify-center gap-1">
                                                <FileText className="h-3 w-3" />
                                                Documents
                                            </div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-2xl font-bold text-secondary-foreground">
                                                {projectStats?.total_versions || 0}
                                            </div>
                                            <div className="text-xs text-muted-foreground flex items-center justify-center gap-1">
                                                <LayoutTemplate className="h-3 w-3" />
                                                Versions
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                                        <span>Last updated {new Date(project.updated_at).toLocaleDateString()}</span>
                                        <Button variant="ghost" size="sm" className="group-hover:translate-x-1 transition-transform p-0 h-auto font-medium text-primary">
                                            View Documents <ArrowRight className="ml-1 h-3 w-3" />
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
