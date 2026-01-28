'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    CardDescription,
    Badge,
    Button,
    Spinner,
    Table,
    TableHeader,
    TableBody,
    TableRow,
    TableHead,
    TableCell,
    Separator,
} from '@/components/ui';
import {
    FileText,
    Upload,
    Download,
    ChevronLeft,
    Clock,
    User,
    Tag,
    Folder,
    History,
    Trash2,
    Move,
    Edit,
} from 'lucide-react';
import UploadVersionDialog from '../components/UploadVersionDialog';
import MoveDocumentDialog from '../components/MoveDocumentDialog';

// ... (Types remain the same as existing file, can omit for brevity in replacement if I could, 
// but replace_file_content replaces block. I need to be careful to include everything or use multi_replace. 
// I'll provide the full file or strategic chunks. Given the file size, chunk replacement is safer/better 
// if I can target specific areas, but I need to add imports and state. 
// I'll use replace_file_content on the whole file or large chunks to be safe.)
// Wait, replace_file_content works on line ranges. I can do multiple chunks.
// Actually, I'll use multi_replace_file_content to insert imports and then update the component body.
// But first let me just check if I can assume imports are at the top.
// I will rewrite the component part to include the dialog state and dialogs in JSX.

// Due to tool limitations/preference, I'll use multi_replace_file_content.


interface Document {
    id: string;
    project_id: string;
    title: string;
    document_number: string | null;
    document_type_id: string;
    document_type_code: string | null;
    document_type_name: string | null;
    folder_id: string | null;
    folder_path: string | null;
    stage_id: string | null;
    stage_name: string | null;
    stage_color: string | null;
    version_scheme: string;
    current_version: string | null;
    status: string;
    description: string;
    tags: string[];
    metadata: Record<string, unknown>;
    external_references: string[];
    created_by: string | null;
    updated_by: string | null;
    is_archived: boolean;
    created_at: string;
    updated_at: string;
}

interface Version {
    id: string;
    document_id: string;
    version_string: string;
    original_filename: string;
    generated_filename: string;
    mime_type: string;
    size_bytes: number;
    checksum: string;
    change_note: string;
    uploaded_by: string;
    uploaded_at: string;
    download_url: string | null;
}

export default function DocumentDetailView() {
    const params = useParams<{ id: string }>();
    const id = params?.id;
    const router = useRouter();
    const [document, setDocument] = useState<Document | null>(null);
    const [versions, setVersions] = useState<Version[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Dialog states
    const [showUploadDialog, setShowUploadDialog] = useState(false);
    const [showMoveDialog, setShowMoveDialog] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    const fetchDocument = async () => {
        setIsLoading(true);
        setError(null);
        try {
            // Fetch document
            const docRes = await fetch(`/api/dm/documents/${id}`);
            if (!docRes.ok) throw new Error('Document not found');
            const doc = await docRes.json();
            setDocument(doc);

            // Fetch versions
            const versionsRes = await fetch(`/api/dm/documents/${id}/versions`);
            if (versionsRes.ok) {
                const versionsData = await versionsRes.json();
                setVersions(versionsData);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (id) fetchDocument();
    }, [id]);

    const handleDelete = async () => {
        if (!window.confirm('Are you sure you want to move this document to trash?')) {
            return;
        }

        setIsDeleting(true);
        try {
            const response = await fetch(`/api/dm/documents/${id}`, {
                method: 'DELETE',
            });

            if (!response.ok) throw new Error('Failed to delete document');

            router.push('/dm/projects');
        } catch (err) {
            alert('Failed to delete document');
            setIsDeleting(false);
        }
    };

    const formatDate = (date: string) => {
        return new Date(date).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const formatBytes = (bytes: number) => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    const getStatusBadgeVariant = (status: string) => {
        switch (status.toLowerCase()) {
            case 'draft':
                return 'secondary';
            case 'active':
                return 'default';
            case 'under_review':
                return 'warning';
            case 'approved':
                return 'success';
            case 'rejected':
                return 'destructive';
            case 'archived':
                return 'outline';
            default:
                return 'secondary';
        }
    };

    if (isLoading) {
        return (
            <div className="flex h-64 items-center justify-center">
                <Spinner size="lg" />
            </div>
        );
    }

    if (error || !document) {
        return (
            <div className="space-y-4">
                <Button variant="ghost" onClick={() => router.back()}>
                    <ChevronLeft className="mr-2 h-4 w-4" />
                    Back
                </Button>
                <div className="rounded-md bg-destructive/10 p-4 text-destructive">
                    {error || 'Document not found'}
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div className="space-y-1">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => router.back()}
                        className="-ml-2"
                    >
                        <ChevronLeft className="mr-1 h-4 w-4" />
                        Back
                    </Button>
                    <h1 className="text-2xl font-bold">{document.title}</h1>
                    {document.document_number && (
                        <p className="font-mono text-sm text-muted-foreground">
                            {document.document_number}
                        </p>
                    )}
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={() => setShowMoveDialog(true)}>
                        <Move className="mr-2 h-4 w-4" />
                        Move
                    </Button>
                    <Button variant="outline" onClick={() => setShowUploadDialog(true)}>
                        <Upload className="mr-2 h-4 w-4" />
                        Upload Version
                    </Button>
                    <Button
                        variant="destructive"
                        size="icon"
                        onClick={handleDelete}
                        disabled={isDeleting}
                        title="Delete Document"
                    >
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </div>
            </div>

            {/* Status badges row */}
            <div className="flex flex-wrap gap-2">
                <Badge variant={getStatusBadgeVariant(document.status)}>
                    {document.status.replace('_', ' ')}
                </Badge>
                {document.document_type_code && (
                    <Badge variant="outline">
                        <Tag className="mr-1 h-3 w-3" />
                        {document.document_type_code}
                    </Badge>
                )}
                {document.stage_name && (
                    <Badge
                        style={{
                            backgroundColor: document.stage_color || '#6B7280',
                            color: '#fff',
                        }}
                    >
                        {document.stage_name}
                    </Badge>
                )}
                {document.current_version && (
                    <Badge variant="secondary">
                        v{document.current_version}
                    </Badge>
                )}
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Main content */}
                <div className="space-y-6 lg:col-span-2">
                    {/* Description */}
                    {document.description && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">Description</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-muted-foreground">
                                    {document.description}
                                </p>
                            </CardContent>
                        </Card>
                    )}

                    {/* Version History */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-lg">
                                <History className="h-5 w-5" />
                                Version History
                            </CardTitle>
                            <CardDescription>
                                {versions.length} version
                                {versions.length !== 1 ? 's' : ''}
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            {versions.length === 0 ? (
                                <div className="py-8 text-center text-muted-foreground">
                                    <FileText className="mx-auto mb-2 h-8 w-8 opacity-50" />
                                    <p>No versions uploaded yet</p>
                                    <Button variant="outline" className="mt-4">
                                        <Upload className="mr-2 h-4 w-4" />
                                        Upload First Version
                                    </Button>
                                </div>
                            ) : (
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Version</TableHead>
                                            <TableHead>Filename</TableHead>
                                            <TableHead>Size</TableHead>
                                            <TableHead>Uploaded</TableHead>
                                            <TableHead className="w-[80px]"></TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {versions.map((version, index) => (
                                            <TableRow key={version.id}>
                                                <TableCell>
                                                    <code className="font-semibold">
                                                        {version.version_string}
                                                    </code>
                                                    {index === 0 && (
                                                        <Badge
                                                            variant="secondary"
                                                            className="ml-2"
                                                        >
                                                            Latest
                                                        </Badge>
                                                    )}
                                                </TableCell>
                                                <TableCell className="max-w-[200px] truncate">
                                                    {version.original_filename}
                                                </TableCell>
                                                <TableCell>
                                                    {formatBytes(version.size_bytes)}
                                                </TableCell>
                                                <TableCell>
                                                    {formatDate(version.uploaded_at)}
                                                </TableCell>
                                                <TableCell>
                                                    {version.download_url && (
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            asChild
                                                        >
                                                            <a
                                                                href={version.download_url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                            >
                                                                <Download className="h-4 w-4" />
                                                            </a>
                                                        </Button>
                                                    )}
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            )}
                        </CardContent>
                    </Card>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    {/* Details */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Details</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center gap-2 text-sm">
                                <Tag className="h-4 w-4 text-muted-foreground" />
                                <span className="text-muted-foreground">Type:</span>
                                <span>{document.document_type_name || '-'}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <Folder className="h-4 w-4 text-muted-foreground" />
                                <span className="text-muted-foreground">Folder:</span>
                                <span>{document.folder_path || 'Root'}</span>
                            </div>
                            <Separator />
                            <div className="flex items-center gap-2 text-sm">
                                <Clock className="h-4 w-4 text-muted-foreground" />
                                <span className="text-muted-foreground">Created:</span>
                                <span>{formatDate(document.created_at)}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <Clock className="h-4 w-4 text-muted-foreground" />
                                <span className="text-muted-foreground">Updated:</span>
                                <span>{formatDate(document.updated_at)}</span>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Tags */}
                    {document.tags.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">Tags</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="flex flex-wrap gap-1">
                                    {document.tags.map((tag) => (
                                        <Badge key={tag} variant="secondary">
                                            {tag}
                                        </Badge>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* External References */}
                    {document.external_references.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">References</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ul className="space-y-1 text-sm">
                                    {document.external_references.map((ref, i) => (
                                        <li key={i} className="text-muted-foreground">
                                            {ref}
                                        </li>
                                    ))}
                                </ul>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
}
