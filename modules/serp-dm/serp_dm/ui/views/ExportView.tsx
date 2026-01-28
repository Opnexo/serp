'use client';

import { useState, useEffect } from 'react';
import {
    Card,
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent,
    Button,
    Table,
    TableHeader,
    TableBody,
    TableRow,
    TableHead,
    TableCell,
    Spinner,
    Badge,
} from '@/components/ui';
import { Download, FileArchive } from 'lucide-react';

interface Project {
    id: string;
    name: string;
    project_type: string;
    status: string;
    updated_at: string;
}

export default function ExportView() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchProjects = async () => {
            setIsLoading(true);
            try {
                const response = await fetch('/api/pm/projects');
                if (!response.ok) throw new Error('Failed to fetch projects');
                const data = await response.json();
                setProjects(data.items || []);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load projects');
            } finally {
                setIsLoading(false);
            }
        };

        fetchProjects();
    }, []);

    const handleExport = (projectId: string) => {
        // Trigger download in new window
        window.open(`/api/dm/projects/${projectId}/export`, '_blank');
    };

    if (isLoading) {
        return (
            <div className="flex h-64 items-center justify-center">
                <Spinner size="lg" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold">Export Documents</h1>
                <p className="text-muted-foreground">Download all documents for a project as a ZIP archive.</p>
            </div>

            {error && (
                <div className="rounded-md bg-destructive/10 p-4 text-destructive">
                    {error}
                </div>
            )}

            <Card>
                <CardHeader>
                    <CardTitle>Select Project</CardTitle>
                    <CardDescription>Choose a project to export.</CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Project Name</TableHead>
                                <TableHead>Type</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Last Updated</TableHead>
                                <TableHead className="text-right">Action</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {projects.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center py-6 text-muted-foreground">
                                        No projects found.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                projects.map((project) => (
                                    <TableRow key={project.id}>
                                        <TableCell className="font-medium">
                                            <div className="flex items-center gap-2">
                                                <FileArchive className="h-4 w-4 text-muted-foreground" />
                                                {project.name}
                                            </div>
                                        </TableCell>
                                        <TableCell>{project.project_type}</TableCell>
                                        <TableCell>
                                            <Badge variant="outline">{project.status}</Badge>
                                        </TableCell>
                                        <TableCell>
                                            {new Date(project.updated_at).toLocaleDateString()}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                onClick={() => handleExport(project.id)}
                                            >
                                                <Download className="mr-2 h-4 w-4" />
                                                Export ZIP
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
