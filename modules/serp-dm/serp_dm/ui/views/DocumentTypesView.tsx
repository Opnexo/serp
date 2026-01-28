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
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui';
import { Plus, Edit, Tag } from 'lucide-react';

interface DocumentType {
    id: string;
    code: string;
    name: string;
    description: string;
    category: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

const CATEGORIES = [
    { value: 'general', label: 'General' },
    { value: 'engineering', label: 'Engineering' },
    { value: 'finance', label: 'Finance' },
    { value: 'logistics', label: 'Logistics' },
    { value: 'contracts', label: 'Contracts' },
    { value: 'legal', label: 'Legal' },
    { value: 'hr', label: 'Human Resources' },
];

export default function DocumentTypesView() {
    const [docTypes, setDocTypes] = useState<DocumentType[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCreateDialog, setShowCreateDialog] = useState(false);

    // Form state
    const [code, setCode] = useState('');
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [category, setCategory] = useState('general');
    const [isSaving, setIsSaving] = useState(false);

    const fetchDocTypes = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('/api/dm/admin/document-types?include_inactive=true');
            if (!response.ok) throw new Error('Failed to fetch document types');
            const data = await response.json();
            setDocTypes(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchDocTypes();
    }, []);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        try {
            const response = await fetch('/api/dm/admin/document-types', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code: code.trim().toUpperCase(),
                    name: name.trim(),
                    description: description.trim(),
                    category,
                }),
            });
            if (!response.ok) throw new Error('Failed to create document type');
            setShowCreateDialog(false);
            setCode('');
            setName('');
            setDescription('');
            setCategory('general');
            fetchDocTypes();
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
                    <h1 className="text-2xl font-bold">Document Types</h1>
                    <p className="text-muted-foreground">
                        Configure document classification codes
                    </p>
                </div>
                <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" />
                            New Type
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Create Document Type</DialogTitle>
                        </DialogHeader>
                        <form onSubmit={handleCreate} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="code">Code</Label>
                                    <Input
                                        id="code"
                                        value={code}
                                        onChange={(e) => setCode(e.target.value)}
                                        placeholder="e.g., DRAW"
                                        maxLength={10}
                                        className="font-mono uppercase"
                                        required
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="category">Category</Label>
                                    <Select value={category} onValueChange={setCategory}>
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {CATEGORIES.map((cat) => (
                                                <SelectItem key={cat.value} value={cat.value}>
                                                    {cat.label}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="name">Name</Label>
                                <Input
                                    id="name"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="e.g., Technical Drawing"
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
                            <div className="flex justify-end gap-2">
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={() => setShowCreateDialog(false)}
                                >
                                    Cancel
                                </Button>
                                <Button type="submit" disabled={isSaving}>
                                    {isSaving ? 'Creating...' : 'Create Type'}
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

            {docTypes.length === 0 ? (
                <Card className="py-12 text-center">
                    <CardContent>
                        <Tag className="mx-auto mb-4 h-12 w-12 text-muted-foreground opacity-50" />
                        <h3 className="text-lg font-semibold">No document types yet</h3>
                        <p className="mt-1 text-muted-foreground">
                            Create document types to classify your documents
                        </p>
                    </CardContent>
                </Card>
            ) : (
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead className="w-[100px]">Code</TableHead>
                            <TableHead>Name</TableHead>
                            <TableHead>Category</TableHead>
                            <TableHead>Description</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead className="w-[100px]">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {docTypes.map((dt) => (
                            <TableRow key={dt.id}>
                                <TableCell>
                                    <code className="rounded bg-muted px-2 py-1 font-semibold">
                                        {dt.code}
                                    </code>
                                </TableCell>
                                <TableCell className="font-medium">{dt.name}</TableCell>
                                <TableCell className="capitalize">{dt.category}</TableCell>
                                <TableCell className="text-muted-foreground">
                                    {dt.description || '-'}
                                </TableCell>
                                <TableCell>
                                    <Badge variant={dt.is_active ? 'default' : 'outline'}>
                                        {dt.is_active ? 'Active' : 'Inactive'}
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
