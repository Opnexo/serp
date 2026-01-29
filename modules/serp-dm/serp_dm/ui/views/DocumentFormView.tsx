'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    Button,
    Input,
    Label,
    Textarea,
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
    Spinner,
} from '@/components/ui';
import { Save, X } from 'lucide-react';

interface DocumentType {
    id: string;
    code: string;
    name: string;
    category: string;
}

interface Stage {
    id: string;
    name: string;
    color: string;
}

interface Folder {
    id: string;
    name: string;
    path: string;
}

export default function DocumentFormView() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [isLoading, setIsLoading] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Reference data
    const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
    const [stages, setStages] = useState<Stage[]>([]);
    const [folders, setFolders] = useState<Folder[]>([]);
    const [projects, setProjects] = useState<{ id: string, name: string }[]>([]);

    // Form state
    const [selectedProjectId, setSelectedProjectId] = useState('');
    const [title, setTitle] = useState('');
    const [documentTypeId, setDocumentTypeId] = useState('');
    const [stageId, setStageId] = useState('');
    const [folderId, setFolderId] = useState('');
    const [description, setDescription] = useState('');
    const [tags, setTags] = useState('');
    const [externalRefs, setExternalRefs] = useState('');

    // Get projectId from URL params
    const projectIdParam = searchParams?.get('project') || null;

    useEffect(() => {
        if (projectIdParam) {
            setSelectedProjectId(projectIdParam);
        } else {
            // Fetch all projects if none pre-selected
            const fetchProjects = async () => {
                try {
                    const res = await fetch('/api/pm/projects');
                    if (res.ok) {
                        const data = await res.json();
                        setProjects(data.items || []);
                    }
                } catch (e) {
                    console.error("Failed to fetch projects", e);
                }
            };
            fetchProjects();
        }
    }, [projectIdParam]);

    useEffect(() => {
        // Fetch document types globally (independent of project)
        const loadDocumentTypes = async () => {
            if (documentTypes.length === 0) {
                try {
                    const typesRes = await fetch('/api/dm/admin/document-types');
                    if (typesRes.ok) {
                        const types = await typesRes.json();
                        setDocumentTypes(types);
                    }
                } catch (err) {
                    console.error('Failed to load document types:', err);
                }
            }
        };
        loadDocumentTypes();
    }, []);

    useEffect(() => {
        const loadProjectData = async () => {
            if (!selectedProjectId) {
                setStages([]);
                setFolders([]);
                return;
            }

            setIsLoading(true);
            try {
                // Fetch stages and folders for selected project
                const [stagesRes, foldersRes] = await Promise.all([
                    fetch(`/api/dm/projects/${selectedProjectId}/stages`),
                    fetch(`/api/dm/projects/${selectedProjectId}/folders`),
                ]);

                if (stagesRes.ok) {
                    const stagesData = await stagesRes.json();
                    setStages(stagesData.items || []);
                }

                if (foldersRes.ok) {
                    const foldersData = await foldersRes.json();
                    setFolders(foldersData.items || []);
                }
            } catch (err) {
                console.error('Failed to load project reference data:', err);
            } finally {
                setIsLoading(false);
            }
        };

        loadProjectData();
    }, [selectedProjectId]);

    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    // ... (existing code)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!selectedProjectId) {
            setError('Please select a project');
            return;
        }

        if (!title.trim() || !documentTypeId) {
            setError('Title and document type are required');
            return;
        }

        setIsSaving(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('project_id', selectedProjectId);
            formData.append('title', title.trim());
            formData.append('document_type_id', documentTypeId);
            if (stageId) formData.append('stage_id', stageId);
            if (folderId) formData.append('folder_id', folderId);
            formData.append('description', description.trim());

            // Handle tags as list
            const tagList = tags.split(',').map(t => t.trim()).filter(Boolean);
            tagList.forEach(tag => formData.append('tags', tag));

            // Handle external refs as list
            const refList = externalRefs.split('\n').map(r => r.trim()).filter(Boolean);
            refList.forEach(ref => formData.append('external_references', ref));

            if (selectedFile) {
                formData.append('file', selectedFile);
            }

            // Note: Adjust endpoint if backend requires separate upload call
            // Assuming the create endpoint handles multipart/form-data
            const response = await fetch(`/api/dm/projects/${selectedProjectId}/documents`, {
                method: 'POST',
                // headers: { 'Content-Type': 'multipart/form-data' }, // Fetch sets this automatically with boundary
                body: formData,
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to register document');
            }

            const doc = await response.json();
            router.push(`/dm/documents/${doc.id}`);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading && !documentTypes.length) { // Only show full spinner on initial load
        return (
            <div className="flex h-64 items-center justify-center">
                <Spinner size="lg" />
            </div>
        );
    }

    return (
        <div className="mx-auto max-w-2xl space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Register New Document</h1>
                <Button variant="ghost" onClick={() => router.back()}>
                    <X className="mr-2 h-4 w-4" />
                    Cancel
                </Button>
            </div>

            {error && (
                <div className="rounded-md bg-destructive/10 p-4 text-destructive">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit}>
                <Card>
                    <CardHeader>
                        <CardTitle>Document Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {/* Project Selection (if not pre-selected) */}
                        {!projectIdParam && (
                            <div className="space-y-2">
                                <Label htmlFor="project">Project *</Label>
                                <Select
                                    value={selectedProjectId}
                                    onValueChange={(val) => setSelectedProjectId(val || '')}
                                >
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select project">
                                            {projects.find(p => p.id === selectedProjectId)?.name || "Select project"}
                                        </SelectValue>
                                    </SelectTrigger>
                                    <SelectContent>
                                        {projects.map((p) => (
                                            <SelectItem key={p.id} value={p.id}>
                                                {p.name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        )}

                        {/* Title */}
                        <div className="space-y-2">
                            <Label htmlFor="title">Title *</Label>
                            <Input
                                id="title"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                placeholder="Enter document title"
                                required
                            />
                        </div>

                        {/* Document Type */}
                        <div className="space-y-2">
                            <Label htmlFor="docType">Document Type *</Label>
                            <Select
                                value={documentTypeId}
                                onValueChange={setDocumentTypeId}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select document type" />
                                </SelectTrigger>
                                <SelectContent>
                                    {documentTypes.map((type) => (
                                        <SelectItem key={type.id} value={type.id}>
                                            <span className="font-mono">{type.code}</span>
                                            <span className="ml-2">{type.name}</span>
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Stage (Kanban column) */}
                        {stages.length > 0 && (
                            <div className="space-y-2">
                                <Label htmlFor="stage">Stage</Label>
                                <Select value={stageId} onValueChange={setStageId}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select stage (optional)" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {stages.map((stage) => (
                                            <SelectItem key={stage.id} value={stage.id}>
                                                <span
                                                    className="mr-2 inline-block h-3 w-3 rounded-full"
                                                    style={{ backgroundColor: stage.color }}
                                                />
                                                {stage.name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        )}

                        {/* Folder */}
                        {folders.length > 0 && (
                            <div className="space-y-2">
                                <Label htmlFor="folder">Folder</Label>
                                <Select value={folderId} onValueChange={setFolderId}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select folder (optional)" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {folders.map((folder) => (
                                            <SelectItem key={folder.id} value={folder.id}>
                                                {folder.path}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        )}

                        {/* File Upload */}
                        <div className="space-y-2">
                            <Label htmlFor="file">Document File</Label>
                            <div className="flex items-center gap-4">
                                <Input
                                    id="file"
                                    type="file"
                                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                                    className="cursor-pointer"
                                />
                            </div>
                            <p className="text-xs text-muted-foreground">
                                Upload the document file (PDF, DOCX, etc.)
                            </p>
                        </div>

                        {/* Description */}
                        <div className="space-y-2">
                            <Label htmlFor="description">Description</Label>
                            <Textarea
                                id="description"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder="Brief description of the document"
                                rows={3}
                            />
                        </div>

                        {/* Tags */}
                        <div className="space-y-2">
                            <Label htmlFor="tags">Tags</Label>
                            <Input
                                id="tags"
                                value={tags}
                                onChange={(e) => setTags(e.target.value)}
                                placeholder="Comma-separated tags (e.g., urgent, review, final)"
                            />
                        </div>

                        {/* External References */}
                        <div className="space-y-2">
                            <Label htmlFor="refs">External References</Label>
                            <Textarea
                                id="refs"
                                value={externalRefs}
                                onChange={(e) => setExternalRefs(e.target.value)}
                                placeholder="One reference per line (e.g., URLs, other document numbers)"
                                rows={2}
                            />
                        </div>
                    </CardContent>
                </Card>

                <div className="flex justify-end gap-2 pt-4">
                    <Button
                        type="button"
                        variant="outline"
                        onClick={() => router.back()}
                    >
                        Cancel
                    </Button>
                    <Button type="submit" disabled={isSaving}>
                        {isSaving ? (
                            <>
                                <Spinner className="mr-2" size="sm" />
                                Saving...
                            </>
                        ) : (
                            <>
                                <Save className="mr-2 h-4 w-4" />
                                Register Document
                            </>
                        )}
                    </Button>
                </div>
            </form>
        </div>
    );
}
