'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    Badge,
    Button,
    Spinner,
} from '@/components/ui';
import {
    DndContext,
    DragOverlay,
    closestCorners,
    PointerSensor,
    useSensor,
    useSensors,
    DragStartEvent,
    DragEndEvent,
} from '@dnd-kit/core';
import {
    SortableContext,
    verticalListSortingStrategy,
    useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Plus, Settings, GripVertical, FileText } from 'lucide-react';
import CreateStageDialog from '../components/CreateStageDialog';

interface Stage {
    id: string;
    project_id: string;
    name: string;
    description: string;
    order: number;
    color: string;
    is_default: boolean;
    document_count: number;
}

interface Document {
    id: string;
    title: string;
    document_number: string | null;
    document_type_code: string | null;
    current_version: string | null;
    status: string;
    stage_id: string | null;
}

interface KanbanData {
    project_id: string;
    stages: Stage[];
    documents_by_stage: Record<string, Document[]>;
}

// Sortable document card component
function DocumentCard({ document }: { document: Document }) {
    const router = useRouter();
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: document.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            className="group cursor-pointer rounded-lg border bg-card p-3 shadow-sm hover:shadow-md"
            onClick={() => router.push(`/dm/documents/${document.id}`)}
        >
            <div className="flex items-start gap-2">
                <div
                    {...attributes}
                    {...listeners}
                    className="mt-1 cursor-grab opacity-0 group-hover:opacity-100"
                    onClick={(e) => e.stopPropagation()}
                >
                    <GripVertical className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">{document.title}</p>
                    {document.document_number && (
                        <p className="truncate font-mono text-xs text-muted-foreground">
                            {document.document_number}
                        </p>
                    )}
                    <div className="mt-2 flex items-center gap-2">
                        {document.document_type_code && (
                            <Badge variant="outline" className="text-xs">
                                {document.document_type_code}
                            </Badge>
                        )}
                        {document.current_version && (
                            <span className="text-xs text-muted-foreground">
                                v{document.current_version}
                            </span>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

// Kanban column component
function KanbanColumn({
    stage,
    documents,
    isOver,
}: {
    stage: Stage;
    documents: Document[];
    isOver: boolean;
}) {
    return (
        <div
            className={`flex min-h-[500px] w-80 flex-shrink-0 flex-col rounded-lg border bg-muted/30 ${isOver ? 'ring-2 ring-primary' : ''
                }`}
        >
            {/* Column header */}
            <div
                className="flex items-center justify-between rounded-t-lg p-3"
                style={{ backgroundColor: stage.color + '20' }}
            >
                <div className="flex items-center gap-2">
                    <div
                        className="h-3 w-3 rounded-full"
                        style={{ backgroundColor: stage.color }}
                    />
                    <h3 className="font-semibold">{stage.name}</h3>
                    <Badge variant="secondary" className="ml-1">
                        {documents.length}
                    </Badge>
                </div>
            </div>

            {/* Cards container */}
            <div className="flex-1 space-y-2 overflow-y-auto p-2">
                <SortableContext
                    items={documents.map((d) => d.id)}
                    strategy={verticalListSortingStrategy}
                >
                    {documents.map((doc) => (
                        <DocumentCard key={doc.id} document={doc} />
                    ))}
                </SortableContext>

                {documents.length === 0 && (
                    <div className="flex h-32 items-center justify-center rounded-lg border-2 border-dashed text-sm text-muted-foreground">
                        Drop documents here
                    </div>
                )}
            </div>
        </div>
    );
}

export default function KanbanBoardView() {
    const router = useRouter();
    const [kanbanData, setKanbanData] = useState<KanbanData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeDocument, setActiveDocument] = useState<Document | null>(null);
    const [overStageId, setOverStageId] = useState<string | null>(null);
    const [showCreateStageDialog, setShowCreateStageDialog] = useState(false);

    // TODO: Get from project context or route param
    const projectId = new URLSearchParams(window.location.search).get('project');

    // Check for action param to open dialogs
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        if (params.get('action') === 'new-stage') {
            setShowCreateStageDialog(true);
            // Clean URL
            // params.delete('action');
            // navigate(`?${params.toString()}`, { replace: true });
        }
    }, [location.search]);

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 8,
            },
        })
    );

    const fetchKanbanData = useCallback(async () => {
        if (!projectId) {
            setError('Please select a project');
            setIsLoading(false);
            return;
        }

        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(`/api/dm/projects/${projectId}/kanban`);
            if (!response.ok) throw new Error('Failed to fetch Kanban data');
            const data: KanbanData = await response.json();
            setKanbanData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    }, [projectId]);

    useEffect(() => {
        fetchKanbanData();
    }, [fetchKanbanData]);

    const handleDragStart = (event: DragStartEvent) => {
        const { active } = event;
        const draggedDoc = findDocument(active.id as string);
        setActiveDocument(draggedDoc || null);
    };

    const handleDragOver = (event: any) => {
        const { over } = event;
        if (over) {
            // Find which stage the document is over
            const stageId = findStageForDocument(over.id as string);
            setOverStageId(stageId);
        } else {
            setOverStageId(null);
        }
    };

    const handleDragEnd = async (event: DragEndEvent) => {
        const { active, over } = event;
        setActiveDocument(null);
        setOverStageId(null);

        if (!over || !kanbanData) return;

        const documentId = active.id as string;
        const targetStageId = findStageForDocument(over.id as string);

        if (!targetStageId) return;

        // Find current stage
        const currentStageId = findCurrentStage(documentId);
        if (currentStageId === targetStageId) return;

        // Optimistic update
        setKanbanData((prev) => {
            if (!prev) return prev;
            const newData = { ...prev };
            newData.documents_by_stage = { ...prev.documents_by_stage };

            // Remove from current stage
            if (currentStageId) {
                newData.documents_by_stage[currentStageId] =
                    newData.documents_by_stage[currentStageId]?.filter(
                        (d) => d.id !== documentId
                    ) || [];
            }

            // Add to new stage
            const movedDoc = findDocument(documentId);
            if (movedDoc) {
                newData.documents_by_stage[targetStageId] = [
                    ...(newData.documents_by_stage[targetStageId] || []),
                    { ...movedDoc, stage_id: targetStageId },
                ];
            }

            return newData;
        });

        // API call
        try {
            await fetch(`/api/dm/documents/${documentId}/move`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stage_id: targetStageId }),
            });
        } catch (err) {
            // Revert on error
            fetchKanbanData();
        }
    };

    const findDocument = (id: string): Document | undefined => {
        if (!kanbanData) return undefined;
        for (const docs of Object.values(kanbanData.documents_by_stage)) {
            const found = docs.find((d) => d.id === id);
            if (found) return found;
        }
        return undefined;
    };

    const findCurrentStage = (docId: string): string | null => {
        if (!kanbanData) return null;
        for (const [stageId, docs] of Object.entries(kanbanData.documents_by_stage)) {
            if (docs.some((d) => d.id === docId)) return stageId;
        }
        return null;
    };

    const findStageForDocument = (id: string): string | null => {
        if (!kanbanData) return null;
        // Check if the id is a stage id
        if (kanbanData.stages.some((s) => s.id === id)) return id;
        // Otherwise find which stage the document belongs to
        return findCurrentStage(id);
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

    if (!kanbanData || kanbanData.stages.length === 0) {
        return (
            <div className="space-y-4">
                <h1 className="text-2xl font-bold">Document Workflow</h1>
                <Card className="py-12 text-center">
                    <CardContent>
                        <FileText className="mx-auto mb-4 h-12 w-12 text-muted-foreground opacity-50" />
                        <h3 className="text-lg font-semibold">No stages configured</h3>
                        <p className="mt-1 text-muted-foreground">
                            Create stages to organize your document workflow
                        </p>
                        <Button className="mt-4" onClick={() => setShowCreateStageDialog(true)}>
                            <Plus className="mr-2 h-4 w-4" />
                            Create Stages
                        </Button>
                    </CardContent>
                </Card>

                {projectId && (
                    <CreateStageDialog
                        open={showCreateStageDialog}
                        onOpenChange={setShowCreateStageDialog}
                        projectId={projectId}
                        onSuccess={fetchKanbanData}
                    />
                )}
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Document Workflow</h1>
                <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                        <Settings className="mr-2 h-4 w-4" />
                        Manage Stages
                    </Button>
                    <Button onClick={() => setShowCreateStageDialog(true)}>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Stage
                    </Button>
                    <Button onClick={() => router.push('/dm/documents/new')}>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Document
                    </Button>
                </div>
            </div>

            {/* Kanban board */}
            <DndContext
                sensors={sensors}
                collisionDetection={closestCorners}
                onDragStart={handleDragStart}
                onDragOver={handleDragOver}
                onDragEnd={handleDragEnd}
            >
                <div className="flex gap-4 overflow-x-auto pb-4">
                    {kanbanData.stages.map((stage) => (
                        <KanbanColumn
                            key={stage.id}
                            stage={stage}
                            documents={kanbanData.documents_by_stage[stage.id] || []}
                            isOver={overStageId === stage.id}
                        />
                    ))}
                </div>

                <DragOverlay>
                    {activeDocument && (
                        <div className="w-72 rounded-lg border bg-card p-3 shadow-lg">
                            <p className="font-medium">{activeDocument.title}</p>
                            {activeDocument.document_number && (
                                <p className="font-mono text-xs text-muted-foreground">
                                    {activeDocument.document_number}
                                </p>
                            )}
                        </div>
                    )}
                </DragOverlay>
            </DndContext>

            {projectId && (
                <CreateStageDialog
                    open={showCreateStageDialog}
                    onOpenChange={setShowCreateStageDialog}
                    projectId={projectId}
                    onSuccess={fetchKanbanData}
                />
            )}
        </div>
    );
}
