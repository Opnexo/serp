'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
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
    Input,
    Card,
    CardContent,
    Tabs,
    TabsList,
    TabsTrigger,
    TabsContent,
} from '@/components/ui';
import {
    FileText,
    Search,
    Plus,
    Upload,
    Download,
    Grid,
    List as ListIcon,
    Folder,
    FolderOpen,
    MoreHorizontal,
    File,
    ChevronRight,
    ChevronDown
} from 'lucide-react';

// Types
interface Project {
    id: string;
    name: string;
    project_type: string;
    status: string;
}

interface Document {
    id: string;
    title: string;
    document_number: string | null;
    document_type_name: string | null;
    status: string;
    updated_at: string;
    current_version: string | null;
    folder_id: string | null;
}

interface FolderNode {
    id: string;
    name: string;
    path: string;
    children: FolderNode[];
    documents: Document[];
}

// Tree Item Component
const TreeItem = ({
    node,
    level = 0,
    onToggle,
    expanded,
    onDocClick
}: {
    node: FolderNode,
    level?: number,
    onToggle: (id: string) => void,
    expanded: Set<string>,
    onDocClick: (id: string) => void
}) => {
    const isExpanded = expanded.has(node.id);
    const hasChildren = node.children.length > 0 || node.documents.length > 0;

    return (
        <div className="select-none">
            <div
                className={`flex items-center py-1.5 px-2 hover:bg-muted/50 rounded-sm cursor-pointer text-sm`}
                style={{ paddingLeft: `${level * 1.5 + 0.5}rem` }}
                onClick={() => hasChildren && onToggle(node.id)}
            >
                <div className="mr-1 h-4 w-4 shrink-0 flex items-center justify-center text-muted-foreground">
                    {hasChildren && (
                        isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />
                    )}
                </div>
                {isExpanded ?
                    <FolderOpen className="mr-2 h-4 w-4 text-blue-500 fill-blue-500/20" /> :
                    <Folder className="mr-2 h-4 w-4 text-blue-500 fill-blue-500/20" />
                }
                <span className="font-medium truncate">{node.name}</span>
                <span className="ml-2 text-xs text-muted-foreground">
                    ({node.documents.length})
                </span>
            </div>

            {isExpanded && (
                <div>
                    {node.children.map(child => (
                        <TreeItem
                            key={child.id}
                            node={child}
                            level={level + 1}
                            onToggle={onToggle}
                            expanded={expanded}
                            onDocClick={onDocClick}
                        />
                    ))}
                    {node.documents.map(doc => (
                        <div
                            key={doc.id}
                            className="flex items-center py-1.5 px-2 hover:bg-muted/50 rounded-sm cursor-pointer text-sm group"
                            style={{ paddingLeft: `${(level + 1) * 1.5 + 2}rem` }}
                            onClick={() => onDocClick(doc.id)}
                        >
                            <FileText className="mr-2 h-4 w-4 text-muted-foreground" />
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                    <span className="truncate">{doc.title}</span>
                                    {doc.document_number && (
                                        <Badge variant="outline" className="text-[10px] h-4 px-1">
                                            {doc.document_number}
                                        </Badge>
                                    )}
                                </div>
                            </div>
                            <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1">
                                <Badge variant="secondary" className="text-[10px] h-4 px-1">
                                    {doc.status}
                                </Badge>
                                <Button variant="ghost" size="icon" className="h-6 w-6">
                                    <MoreHorizontal className="h-3 w-3" />
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default function DMProjectView() {
    // Correct way to get params in Next.js app router client components depends on version,
    // but standard useParams usually works if configured. 
    // If not, we might need to rely on props if passed by layout, but usually useParams found.
    const params = useParams();
    // Safety check for projectId
    const projectId = typeof params?.projectId === 'string' ? params.projectId : '';

    const router = useRouter();

    const [project, setProject] = useState<Project | null>(null);
    const [documents, setDocuments] = useState<Document[]>([]);
    const [folderTree, setFolderTree] = useState<FolderNode[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [viewMode, setViewMode] = useState<'list' | 'tree'>('list');
    const [searchTerm, setSearchTerm] = useState('');
    const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

    useEffect(() => {
        const fetchData = async () => {
            if (!projectId) return;

            setIsLoading(true);
            try {
                // Fetch Project Info (from PM module) - Assuming an endpoint exists or we fetch from list
                // Since there is no direct single project endpoint in PM routes shown (only list), 
                // we might filter from list or assume there's a detail, but let's try a direct fetch if feasible
                // or just use what we have. API routes.py showed document routes, existing PM view showed `/api/pm/projects`.
                // Let's assume we can fetch project details.
                // NOTE: If /api/pm/projects/:id doesn't exist, we fallback to finding in list.
                // But typically it should exist.

                // For now, let's try to fetch all projects and find ours, as we know that endpoint works.
                const projectsRes = await fetch('/api/pm/projects');
                if (projectsRes.ok) {
                    const data = await projectsRes.json();
                    const found = data.items?.find((p: any) => p.id === projectId);
                    if (found) setProject(found);
                }

                // Fetch Documents
                const docsRes = await fetch(`/api/dm/projects/${projectId}/documents?page_size=1000`);
                if (!docsRes.ok) throw new Error('Failed to fetch documents');
                const docsData = await docsRes.json();
                setDocuments(docsData.items || []);

                // Fetch Folders for Tree
                const foldersRes = await fetch(`/api/dm/projects/${projectId}/folders`);
                if (foldersRes.ok) {
                    const foldersData = await foldersRes.json();
                    // Build tree structure
                    // The API returns a tree response "FolderTreeResponse(items=folders)"
                    // but wait, routes.py says `FolderTreeResponse(items=folders)` where folders is list.
                    // We need to construct the tree if the API returns flat list or check if API returns tree.
                    // `FolderTreeResponse` typically implies tree, let's assume it has nested items or we build it.
                    // If flat, we build it.
                    // Let's assume the API returns a flat list for now or matches the `FolderDTO`.
                    // We'll create a simple builder client side just in case.
                    const folders = foldersData.items || [];
                    const tree = buildFolderTree(folders, docsData.items || []);
                    setFolderTree(tree);
                }

            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load project data');
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, [projectId]);

    // Helper to build tree from flat lists
    const buildFolderTree = (folders: any[], docs: any[]): FolderNode[] => {
        // Map folders by ID
        const folderMap: Record<string, FolderNode> = {};
        const rootNodes: FolderNode[] = [];

        // Initialize folder nodes
        folders.forEach(f => {
            folderMap[f.id] = {
                id: f.id,
                name: f.name,
                path: f.path,
                children: [],
                documents: []
            };
        });

        // Build hierarchy
        folders.forEach(f => {
            if (f.parent_id && folderMap[f.parent_id]) {
                folderMap[f.parent_id].children.push(folderMap[f.id]);
            } else {
                rootNodes.push(folderMap[f.id]);
            }
        });

        // Distribute documents
        const unfiledDocs: Document[] = [];
        docs.forEach(d => {
            if (d.folder_id && folderMap[d.folder_id]) {
                folderMap[d.folder_id].documents.push(d);
            } else {
                unfiledDocs.push(d);
            }
        });

        // Add "Unfiled" pseudofolder if there are unfiled docs in tree view?
        // Or just list them at root?
        // For now, let's add a virtual root for unfiled if needed, or just return them if we handled root docs.
        // Let's add them to a "Unfiled" node or just return rootNodes (and handle root docs separately).

        // Actually, let's verify if we want to show root documents in tree.
        if (unfiledDocs.length > 0) {
            rootNodes.unshift({
                id: 'root-unfiled',
                name: 'Unfiled Documents',
                path: '/',
                children: [],
                documents: unfiledDocs
            });
            // Expand unfiled by default
            setExpandedFolders(prev => new Set(prev).add('root-unfiled'));
        }

        return rootNodes;
    };

    const toggleFolder = (folderId: string) => {
        setExpandedFolders(prev => {
            const next = new Set(prev);
            if (next.has(folderId)) {
                next.delete(folderId);
            } else {
                next.add(folderId);
            }
            return next;
        });
    };

    const filteredDocuments = documents.filter(doc =>
        doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (doc.document_number && doc.document_number.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const getStatusVariant = (status: string) => {
        // Map status to badge variants
        const map: Record<string, "default" | "secondary" | "destructive" | "outline" | "success" | "warning"> = {
            'DRAFT': 'secondary',
            'IN_REVIEW': 'warning',
            'APPROVED': 'success',
            'PUBLISHED': 'default',
            'ARCHIVED': 'outline',
            'REJECTED': 'destructive'
        };
        return map[status] || 'secondary';
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
                {error}
            </div>
        );
    }

    if (!project) {
        return <div>Project not found</div>;
    }

    return (
        <div className="space-y-6 h-full flex flex-col">
            {/* Header */}
            <div className="flex flex-col gap-4 border-b pb-4">
                <div className="flex items-center justify-between">
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-2xl font-bold">{project.name}</h1>
                            <Badge variant="outline">{project.status}</Badge>
                        </div>
                        <p className="text-muted-foreground">{documents.length} documents</p>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button variant="outline" onClick={() => window.open(`/api/dm/projects/${projectId}/export`, '_blank')}>
                            <Download className="mr-2 h-4 w-4" />
                            Export
                        </Button>
                        <Button onClick={() => router.push(`/dm/documents/new?project=${projectId}`)}>
                            <Plus className="mr-2 h-4 w-4" />
                            Register Document
                        </Button>
                    </div>
                </div>

                <div className="flex items-center justify-between gap-4">
                    <div className="relative flex-1 max-w-sm">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search documents..."
                            className="pl-9"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div className="flex bg-muted rounded-lg p-1">
                        <Button
                            variant={viewMode === 'list' ? 'secondary' : 'ghost'}
                            size="sm"
                            className="h-8 px-3"
                            onClick={() => setViewMode('list')}
                        >
                            <ListIcon className="h-4 w-4 mr-2" />
                            List
                        </Button>
                        <Button
                            variant={viewMode === 'tree' ? 'secondary' : 'ghost'}
                            size="sm"
                            className="h-8 px-3"
                            onClick={() => setViewMode('tree')}
                        >
                            <Folder className="h-4 w-4 mr-2" />
                            Tree
                        </Button>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 min-h-0">
                {viewMode === 'list' ? (
                    <Card>
                        <CardContent className="p-0">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Title</TableHead>
                                        <TableHead>Number</TableHead>
                                        <TableHead>Type</TableHead>
                                        <TableHead>Status</TableHead>
                                        <TableHead>Version</TableHead>
                                        <TableHead>Updated</TableHead>
                                        <TableHead className="w-[100px]">Actions</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {filteredDocuments.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                                                No documents found
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        filteredDocuments.map((doc) => (
                                            <TableRow
                                                key={doc.id}
                                                className="cursor-pointer hover:bg-muted/50"
                                                onClick={() => router.push(`/dm/documents/${doc.id}`)}
                                            >
                                                <TableCell className="font-medium">
                                                    <div className="flex items-center gap-2">
                                                        <FileText className="h-4 w-4 text-muted-foreground" />
                                                        {doc.title}
                                                    </div>
                                                </TableCell>
                                                <TableCell>{doc.document_number || '-'}</TableCell>
                                                <TableCell>{doc.document_type_name || '-'}</TableCell>
                                                <TableCell>
                                                    <Badge variant={getStatusVariant(doc.status)}>
                                                        {doc.status}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell>{doc.current_version ? `v${doc.current_version}` : '-'}</TableCell>
                                                <TableCell>{new Date(doc.updated_at).toLocaleDateString()}</TableCell>
                                                <TableCell>
                                                    <Button variant="ghost" size="icon" onClick={(e) => {
                                                        e.stopPropagation();
                                                        // Open dropdown menu
                                                    }}>
                                                        <MoreHorizontal className="h-4 w-4" />
                                                    </Button>
                                                </TableCell>
                                            </TableRow>
                                        ))
                                    )}
                                </TableBody>
                            </Table>
                        </CardContent>
                    </Card>
                ) : (
                    <Card className="h-full">
                        <CardContent className="p-4 overflow-auto h-full">
                            {folderTree.length === 0 ? (
                                <div className="text-center py-8 text-muted-foreground">
                                    No folder structure defined
                                </div>
                            ) : (
                                <div className="space-y-1">
                                    {folderTree.map(node => (
                                        <TreeItem
                                            key={node.id}
                                            node={node}
                                            expanded={expandedFolders}
                                            onToggle={toggleFolder}
                                            onDocClick={(id) => router.push(`/dm/documents/${id}`)}
                                        />
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
