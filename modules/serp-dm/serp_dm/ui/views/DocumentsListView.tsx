'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
    Table,
    TableHeader,
    TableBody,
    TableRow,
    TableHead,
    TableCell,
    Badge,
    Button,
    Spinner,
    Empty,
    Input,
} from '@/components/ui';
import { FileText, Search, Upload, Eye } from 'lucide-react';

interface Document {
    id: string;
    title: string;
    document_number: string | null;
    document_type_code: string | null;
    document_type_name: string | null;
    stage_name: string | null;
    stage_color: string | null;
    current_version: string | null;
    status: string;
    updated_at: string;
}

interface DocumentsResponse {
    items: Document[];
    total: number;
    page: number;
    page_size: number;
    has_more: boolean;
}

export default function DocumentsListView() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [documents, setDocuments] = useState<Document[]>([]);
    const [total, setTotal] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(1);

    const projectId = searchParams.get('project');

    const fetchDocuments = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const params = new URLSearchParams({
                page: page.toString(),
                page_size: '50',
            });
            if (search) params.set('search', search);

            const url = projectId
                ? `/api/dm/projects/${projectId}/documents?${params}`
                : `/api/dm/documents?${params}`;

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Failed to fetch documents');
            }
            const data: DocumentsResponse = await response.json();
            setDocuments(data.items || []);
            setTotal(data.total);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchDocuments();
    }, [page, projectId]);

    const handleSearch = () => {
        setPage(1);
        fetchDocuments();
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

    const formatDate = (date: string) => {
        return new Date(date).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
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
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Documents</h1>
                    <p className="text-sm text-muted-foreground">
                        {total} document{total !== 1 ? 's' : ''}
                    </p>
                </div>
                <Button onClick={() => router.push('/dm/documents/new')}>
                    <FileText className="mr-2 h-4 w-4" />
                    Register Document
                </Button>
            </div>

            {/* Search */}
            <div className="flex gap-2">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                        placeholder="Search by title, number, or description..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                        className="pl-9"
                    />
                </div>
                <Button variant="outline" onClick={handleSearch}>
                    Search
                </Button>
            </div>

            {/* Table */}
            {documents.length === 0 ? (
                <Empty
                    icon={FileText}
                    title="No documents yet"
                    description="Register your first document to get started"
                    action={
                        <Button onClick={() => router.push('/dm/documents/new')}>
                            Register Document
                        </Button>
                    }
                />
            ) : (
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Document</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Stage</TableHead>
                            <TableHead>Version</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Updated</TableHead>
                            <TableHead className="w-[100px]">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {documents.map((doc) => (
                            <TableRow
                                key={doc.id}
                                className="cursor-pointer hover:bg-muted/50"
                                onClick={() => router.push(`/dm/documents/${doc.id}`)}
                            >
                                <TableCell>
                                    <div>
                                        <div className="font-medium">{doc.title}</div>
                                        {doc.document_number && (
                                            <div className="text-xs text-muted-foreground">
                                                {doc.document_number}
                                            </div>
                                        )}
                                    </div>
                                </TableCell>
                                <TableCell>
                                    {doc.document_type_code ? (
                                        <Badge variant="outline">
                                            {doc.document_type_code}
                                        </Badge>
                                    ) : (
                                        '-'
                                    )}
                                </TableCell>
                                <TableCell>
                                    {doc.stage_name ? (
                                        <Badge
                                            style={{
                                                backgroundColor: doc.stage_color || '#6B7280',
                                                color: '#fff',
                                            }}
                                        >
                                            {doc.stage_name}
                                        </Badge>
                                    ) : (
                                        '-'
                                    )}
                                </TableCell>
                                <TableCell>
                                    <code className="text-sm">
                                        {doc.current_version || '-'}
                                    </code>
                                </TableCell>
                                <TableCell>
                                    <Badge variant={getStatusBadgeVariant(doc.status)}>
                                        {doc.status.replace('_', ' ')}
                                    </Badge>
                                </TableCell>
                                <TableCell className="text-muted-foreground">
                                    {formatDate(doc.updated_at)}
                                </TableCell>
                                <TableCell>
                                    <div className="flex gap-1">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                router.push(`/dm/documents/${doc.id}`);
                                            }}
                                        >
                                            <Eye className="h-4 w-4" />
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                router.push(`/dm/documents/${doc.id}/upload`);
                                            }}
                                        >
                                            <Upload className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            )}

            {/* Pagination */}
            {total > 50 && (
                <div className="flex items-center justify-center gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        disabled={page === 1}
                        onClick={() => setPage((p) => p - 1)}
                    >
                        Previous
                    </Button>
                    <span className="text-sm text-muted-foreground">
                        Page {page} of {Math.ceil(total / 50)}
                    </span>
                    <Button
                        variant="outline"
                        size="sm"
                        disabled={page >= Math.ceil(total / 50)}
                        onClick={() => setPage((p) => p + 1)}
                    >
                        Next
                    </Button>
                </div>
            )}
        </div>
    );
}
