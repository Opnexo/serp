'use client';

import { useState, useEffect } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
    Button,
    Label,
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
    Spinner,
} from '@/components/ui';

interface MoveDocumentDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    documentId: string;
    projectId: string;
    currentFolderId?: string | null;
    currentStageId?: string | null;
    onSuccess: () => void;
}

interface Stage {
    id: string;
    name: string;
}

interface Folder {
    id: string;
    path: string;
}

export default function MoveDocumentDialog({
    open,
    onOpenChange,
    documentId,
    projectId,
    currentFolderId,
    currentStageId,
    onSuccess,
}: MoveDocumentDialogProps) {
    const [stages, setStages] = useState<Stage[]>([]);
    const [folders, setFolders] = useState<Folder[]>([]);
    const [selectedStageId, setSelectedStageId] = useState<string>(currentStageId || 'none');
    const [selectedFolderId, setSelectedFolderId] = useState<string>(currentFolderId || 'none');
    const [isLoading, setIsLoading] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Reset selection when dialog opens with new props
    useEffect(() => {
        if (open) {
            setSelectedStageId(currentStageId || 'none');
            setSelectedFolderId(currentFolderId || 'none');
            fetchData();
        }
    }, [open, currentStageId, currentFolderId, projectId]);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            const [stagesRes, foldersRes] = await Promise.all([
                fetch(`/api/dm/projects/${projectId}/stages`),
                fetch(`/api/dm/projects/${projectId}/folders`)
            ]);

            if (stagesRes.ok) {
                const data = await stagesRes.json();
                setStages(data.items || []);
            }
            if (foldersRes.ok) {
                const data = await foldersRes.json();
                setFolders(data.items || []);
            }
        } catch (err) {
            console.error('Failed to load move options', err);
            setError('Failed to load options');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setError(null);

        try {
            const response = await fetch(`/api/dm/documents/${documentId}/move`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    stage_id: selectedStageId === 'none' ? null : selectedStageId,
                    folder_id: selectedFolderId === 'none' ? null : selectedFolderId,
                }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to move document');
            }

            onSuccess();
            onOpenChange(false);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Move Document</DialogTitle>
                    <DialogDescription>
                        Change the location or workflow stage of this document.
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                            {error}
                        </div>
                    )}

                    {isLoading ? (
                        <div className="flex justify-center p-4">
                            <Spinner />
                        </div>
                    ) : (
                        <>
                            <div className="space-y-2">
                                <Label htmlFor="stage">Workflow Stage</Label>
                                <Select value={selectedStageId} onValueChange={setSelectedStageId}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select stage" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="none">No Stage</SelectItem>
                                        {stages.map((stage) => (
                                            <SelectItem key={stage.id} value={stage.id}>
                                                {stage.name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="folder">Folder</Label>
                                <Select value={selectedFolderId} onValueChange={setSelectedFolderId}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select folder" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="none">Root Directory</SelectItem>
                                        {folders.map((folder) => (
                                            <SelectItem key={folder.id} value={folder.id}>
                                                {folder.path}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </>
                    )}

                    <DialogFooter>
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => onOpenChange(false)}
                        >
                            Cancel
                        </Button>
                        <Button type="submit" disabled={isSaving || isLoading}>
                            {isSaving ? (
                                <>
                                    <Spinner size="sm" className="mr-2" />
                                    Moving...
                                </>
                            ) : (
                                'Move Document'
                            )}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
