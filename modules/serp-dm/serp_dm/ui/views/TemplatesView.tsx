'use client';

import { useState, useEffect } from 'react';
import {
    Card,
    CardContent,
    Badge,
    Button,
    Input,
    Label,
    Spinner,
    Table,
    TableHeader,
    TableBody,
    TableRow,
    TableHead,
    TableCell,
    Modal,
    ModalContent,
    ModalHeader,
    ModalTitle,
    ModalFooter,
} from '@/components/ui';
import { Plus, Edit, LayoutTemplate, Trash2, Folder } from 'lucide-react';

interface TemplateFolder {
    id: string; // temp id for UI if new
    name: string;
    path: string;
    description: string;
    order: number;
}

interface Template {
    id: string;
    name: string;
    description: string;
    is_default: boolean;
    is_active: boolean;
    folder_count: number;
    created_at: string;
    updated_at: string;
}

export default function TemplatesView() {
    const [templates, setTemplates] = useState<Template[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCreateDialog, setShowCreateDialog] = useState(false);

    // Form state
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [isDefault, setIsDefault] = useState(false);
    const [templateFolders, setTemplateFolders] = useState<TemplateFolder[]>([]);
    const [isSaving, setIsSaving] = useState(false);

    // Edit mode
    const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);

    const fetchTemplates = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('/api/dm/admin/templates');
            if (!response.ok) throw new Error('Failed to fetch templates');
            const data = await response.json();
            setTemplates(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchTemplates();
    }, []);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        try {
            const payload = {
                name: name.trim(),
                description: description.trim(),
                is_default: isDefault,
                folders: templateFolders.map(f => ({
                    name: f.name,
                    path: f.path,
                    description: f.description
                })),
            };

            const url = editingTemplate
                ? `/api/dm/admin/templates/${editingTemplate.id}`
                : '/api/dm/admin/templates';

            const method = editingTemplate ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!response.ok) throw new Error('Failed to save template');

            closeDialog();
            fetchTemplates();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsSaving(false);
        }
    };

    const openCreateDialog = () => {
        setEditingTemplate(null);
        setName('');
        setDescription('');
        setIsDefault(false);
        setTemplateFolders([
            { id: '1', name: '01_Management', path: '/01_Management', description: 'Project management files', order: 0 },
            { id: '2', name: '02_Design', path: '/02_Design', description: 'Design specifications', order: 1 },
            { id: '3', name: '03_Engineering', path: '/03_Engineering', description: 'Technical documentation', order: 2 },
        ]);
        setShowCreateDialog(true);
    };

    const openEditDialog = async (template: Template) => {
        setEditingTemplate(template);
        setName(template.name);
        setDescription(template.description);
        setIsDefault(template.is_default);

        // Fetch folders
        try {
            const response = await fetch(`/api/dm/admin/templates/${template.id}/folders`);
            if (response.ok) {
                const folders = await response.json();
                setTemplateFolders(folders.map((f: any) => ({ ...f, id: f.id || crypto.randomUUID() })));
            } else {
                setTemplateFolders([]);
            }
        } catch (e) {
            console.error(e);
            setTemplateFolders([]);
        }

        setShowCreateDialog(true);
    };

    const closeDialog = () => {
        setShowCreateDialog(false);
        setEditingTemplate(null);
    };

    const addFolder = () => {
        setTemplateFolders([
            ...templateFolders,
            {
                id: crypto.randomUUID(),
                name: 'New Folder',
                path: '/New Folder',
                description: '',
                order: templateFolders.length
            }
        ]);
    };

    const updateFolder = (id: string, field: keyof TemplateFolder, value: any) => {
        setTemplateFolders(templateFolders.map(f => f.id === id ? { ...f, [field]: value } : f));
    }

    const removeFolder = (id: string) => {
        setTemplateFolders(templateFolders.filter(f => f.id !== id));
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
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Storage Templates</h1>
                    <p className="text-muted-foreground">
                        Define folder structures to apply to new projects
                    </p>
                </div>
                <Button onClick={openCreateDialog}>
                    <Plus className="mr-2 h-4 w-4" />
                    New Template
                </Button>
                <Modal open={showCreateDialog} onClose={closeDialog}>
                    <ModalContent size="full">
                        <ModalHeader>
                            <ModalTitle>{editingTemplate ? 'Edit Storage Template' : 'Create Storage Template'}</ModalTitle>
                        </ModalHeader>
                        <form onSubmit={handleCreate} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="name">Name</Label>
                                <Input
                                    id="name"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="e.g., Engineering Project"
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="description">Description</Label>
                                <Input
                                    id="description"
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    placeholder="Brief description"
                                />
                            </div>
                            <div className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    id="isDefault"
                                    checked={isDefault}
                                    onChange={(e) => setIsDefault(e.target.checked)}
                                />
                                <Label htmlFor="isDefault">Set as default template</Label>
                            </div>

                            <div className="space-y-4 pt-4 border-t">
                                <div className="flex justify-between items-center">
                                    <h4 className="font-semibold">Folder Structure</h4>
                                    <Button type="button" size="sm" variant="outline" onClick={addFolder}>
                                        <Plus className="mr-2 h-4 w-4" /> Add Folder
                                    </Button>
                                </div>
                                <div className="border rounded-md">
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead>Name</TableHead>
                                                <TableHead>Path</TableHead>
                                                <TableHead>Description</TableHead>
                                                <TableHead className="w-[50px]"></TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {templateFolders.map((folder) => (
                                                <TableRow key={folder.id}>
                                                    <TableCell>
                                                        <Input
                                                            value={folder.name}
                                                            onChange={(e) => updateFolder(folder.id, 'name', e.target.value)}
                                                            className="h-8"
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Input
                                                            value={folder.path}
                                                            onChange={(e) => updateFolder(folder.id, 'path', e.target.value)}
                                                            className="h-8"
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Input
                                                            value={folder.description}
                                                            onChange={(e) => updateFolder(folder.id, 'description', e.target.value)}
                                                            className="h-8"
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Button type="button" variant="ghost" size="icon" className="h-8 w-8 text-destructive" onClick={() => removeFolder(folder.id)}>
                                                            <Trash2 className="h-4 w-4" />
                                                        </Button>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                            {templateFolders.length === 0 && (
                                                <TableRow>
                                                    <TableCell colSpan={4} className="text-center text-muted-foreground h-24">
                                                        No folders defined.
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </div>
                            </div>
                            <ModalFooter>
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={closeDialog}
                                >
                                    Cancel
                                </Button>
                                <Button type="submit" disabled={isSaving}>
                                    {isSaving ? 'Saving...' : 'Save Template'}
                                </Button>
                            </ModalFooter>
                        </form>
                    </ModalContent>
                </Modal>
            </div>

            {error && (
                <div className="rounded-md bg-destructive/10 p-4 text-destructive">
                    {error}
                </div>
            )}

            {templates.length === 0 ? (
                <Card className="py-12 text-center">
                    <CardContent>
                        <LayoutTemplate className="mx-auto mb-4 h-12 w-12 text-muted-foreground opacity-50" />
                        <h3 className="text-lg font-semibold">No templates yet</h3>
                        <p className="mt-1 text-muted-foreground">
                            Create a template to define folder structures for projects
                        </p>
                    </CardContent>
                </Card>
            ) : (
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Name</TableHead>
                            <TableHead>Description</TableHead>
                            <TableHead>Folders</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead className="w-[100px]">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {templates.map((template) => (
                            <TableRow key={template.id}>
                                <TableCell className="font-medium">
                                    {template.name}
                                    {template.is_default && (
                                        <Badge variant="secondary" className="ml-2">
                                            Default
                                        </Badge>
                                    )}
                                </TableCell>
                                <TableCell className="text-muted-foreground">
                                    {template.description || '-'}
                                </TableCell>
                                <TableCell>{template.folder_count}</TableCell>
                                <TableCell>
                                    <Badge
                                        variant={template.is_active ? 'default' : 'outline'}
                                    >
                                        {template.is_active ? 'Active' : 'Inactive'}
                                    </Badge>
                                </TableCell>
                                <TableCell>
                                    <Button variant="ghost" size="sm" onClick={() => openEditDialog(template)}>
                                        <Edit className="h-4 w-4" />
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            )}
        </div>
    );
}
