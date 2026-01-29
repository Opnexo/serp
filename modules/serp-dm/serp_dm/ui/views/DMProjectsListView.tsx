'use client';

import { useState, useEffect } from 'react';
import {
    Badge,
    Spinner,
    Empty,
    Button,
    Input,
    Card,
    CardContent,
    Modal,
    ModalContent,
    ModalHeader,
    ModalTitle,
    ModalFooter,
    Label,
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui';
import { FolderOpen, FileText, LayoutTemplate, Search, ArrowRight, Settings } from 'lucide-react';

interface Project {
    id: string;
    name: string;
    project_type: string;
    status: string;
    updated_at: string;
}

interface DMProjectConfig {
    id: string;
    pm_project_id: string;
    name: string;
    status: string; // Document project status
    template_id: string | null;
    stage_template_id: string | null;
    is_active: boolean;
    created_at: string;
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
    const [projectConfigs, setProjectConfigs] = useState<Record<string, DMProjectConfig>>({});

    // Configuration Dialog State
    const [configProject, setConfigProject] = useState<Project | null>(null);
    const [storageTemplates, setStorageTemplates] = useState<any[]>([]);
    const [stageTemplates, setStageTemplates] = useState<any[]>([]);
    const [selectedStorageTemplate, setSelectedStorageTemplate] = useState<string>('');
    const [selectedStageTemplate, setSelectedStageTemplate] = useState<string>('');
    const [isConfiguring, setIsConfiguring] = useState(false);

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

            // Fetch stats and config for each project
            const statsMap: Record<string, ProjectStats> = {};
            const configsMap: Record<string, DMProjectConfig> = {};

            await Promise.all(
                items.map(async (p: Project) => {
                    try {
                        // Check if project is already configured in DM
                        const configRes = await fetch(`/api/dm/projects/${p.id}/config`);
                        if (configRes.ok) {
                            const config = await configRes.json();

                            // Only store and fetch stats if config exists (not null)
                            if (config) {
                                configsMap[p.id] = config;

                                // Fetch stats for configured project
                                const statsRes = await fetch(`/api/dm/projects/${p.id}/stats`);
                                if (statsRes.ok) {
                                    statsMap[p.id] = await statsRes.json();
                                }
                            }
                        }
                    } catch (e) {
                        console.error(`Failed to fetch stats for project ${p.id}`, e);
                    }
                })
            );
            setStats(statsMap);
            setProjectConfigs(configsMap);

        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    const fetchTemplates = async () => {
        try {
            console.log('Fetching templates...');
            const [storageRes, stageRes] = await Promise.all([
                fetch('/api/dm/admin/templates'),
                fetch('/api/dm/admin/stage-templates')
            ]);

            console.log('Storage templates response:', storageRes.status);
            console.log('Stage templates response:', stageRes.status);

            if (storageRes.ok) {
                const data = await storageRes.json();
                console.log('Storage templates data:', data);
                setStorageTemplates(data);
            }
            if (stageRes.ok) {
                const data = await stageRes.json();
                console.log('Stage templates data:', data);
                setStageTemplates(data);
            }
        } catch (e) {
            console.error("Failed to fetch templates", e);
        }
    };

    useEffect(() => {
        fetchProjects();
    }, []);

    const handleConfigureClick = (project: Project, e: React.MouseEvent) => {
        e.stopPropagation();
        setConfigProject(project);
        fetchTemplates();
    };

    const handleApplyConfiguration = async () => {
        if (!configProject || !selectedStorageTemplate || !selectedStageTemplate) return;

        setIsConfiguring(true);
        try {
            const payload = {
                template_id: selectedStorageTemplate,
                stage_template_id: selectedStageTemplate,
                name: configProject.name,
            };
            console.log('Sending configuration payload:', payload);

            const response = await fetch(`/api/dm/projects/${configProject.id}/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Configuration failed:', errorData);
                throw new Error(`Failed to configure project: ${JSON.stringify(errorData)}`);
            }

            // Refresh
            const updatedConfig = await response.json();
            setProjectConfigs(prev => ({ ...prev, [configProject.id]: updatedConfig }));

            setConfigProject(null);
            // Optionally show toast success here
        } catch (e) {
            console.error(e);
            // Show error toast
        } finally {
            setIsConfiguring(false);
        }
    };

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
                        const config = projectConfigs[project.id];
                        // Config is present if we got a response, but it's only truly "configured" 
                        // if it has a template_id (meaning a template was applied).
                        // content of default response has template_id = null.
                        const isConfigured = !!config && !!config.template_id;

                        return (
                            <Card
                                key={project.id}
                                className={`group transition-all ${isConfigured ? 'hover:border-primary/50 cursor-pointer' : 'opacity-80'}`}
                                onClick={() => isConfigured ? window.location.href = `/dm/projects/${project.id}` : null}
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
                                        {!isConfigured && (
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                onClick={(e) => handleConfigureClick(project, e)}
                                            >
                                                <Settings className="mr-2 h-3 w-3" />
                                                Configure
                                            </Button>
                                        )}
                                    </div>
                                    <div className="flex items-center justify-between text-sm text-muted-foreground mt-4">
                                        <span>Last updated {new Date(project.updated_at).toLocaleDateString()}</span>
                                        {isConfigured ? (
                                            <Button variant="ghost" size="sm" className="group-hover:translate-x-1 transition-transform p-0 h-auto font-medium text-primary">
                                                View Documents <ArrowRight className="ml-1 h-3 w-3" />
                                            </Button>
                                        ) : (
                                            <span className="text-xs text-amber-500 font-medium">Needs Configuration</span>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            )}

            <Modal open={!!configProject} onClose={() => setConfigProject(null)}>
                <ModalContent size="lg">
                    <ModalHeader>
                        <ModalTitle>Configure Project: {configProject?.name}</ModalTitle>
                    </ModalHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="storage-template">Folder Structure Template</Label>
                            <Select onValueChange={(val) => setSelectedStorageTemplate(val || '')} value={selectedStorageTemplate}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a folder structure" />
                                </SelectTrigger>
                                <SelectContent>
                                    {storageTemplates.map((t) => (
                                        <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <p className="text-xs text-muted-foreground">This will create the initial folder structure for the project.</p>
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="stage-template">Workflow Template</Label>
                            <Select onValueChange={(val) => setSelectedStageTemplate(val || '')} value={selectedStageTemplate}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a workflow" />
                                </SelectTrigger>
                                <SelectContent>
                                    {stageTemplates.map((t) => (
                                        <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <p className="text-xs text-muted-foreground">This defines the Kanban stages (e.g. Draft, Review, Approved).</p>
                        </div>
                    </div>
                    <ModalFooter>
                        <Button variant="outline" onClick={() => setConfigProject(null)}>Cancel</Button>
                        <Button onClick={handleApplyConfiguration} disabled={isConfiguring || !selectedStorageTemplate || !selectedStageTemplate}>
                            {isConfiguring ? <Spinner size="sm" className="mr-2" /> : null}
                            Apply Configuration
                        </Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </div>
    );
}
