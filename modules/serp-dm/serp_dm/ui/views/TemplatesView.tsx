'use client';

import { useState, useEffect } from 'react';
import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    CardDescription,
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
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui';
import { Plus, Edit, LayoutTemplate } from 'lucide-react';

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
    const [isSaving, setIsSaving] = useState(false);

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
            const response = await fetch('/api/dm/admin/templates', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name.trim(),
                    description: description.trim(),
                    is_default: isDefault,
                    folders: [],
                }),
            });
            if (!response.ok) throw new Error('Failed to create template');
            setShowCreateDialog(false);
            setName('');
            setDescription('');
            setIsDefault(false);
            fetchTemplates();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsSaving(false);
        }
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
                <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" />
                            New Template
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Create Storage Template</DialogTitle>
                        </DialogHeader>
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
                            <div className="flex justify-end gap-2">
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={() => setShowCreateDialog(false)}
                                >
                                    Cancel
                                </Button>
                                <Button type="submit" disabled={isSaving}>
                                    {isSaving ? 'Creating...' : 'Create Template'}
                                </Button>
                            </div>
                        </form>
                    </DialogContent>
                </Dialog>
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
                                    <Button variant="ghost" size="sm">
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
