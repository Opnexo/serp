'use client';

import { useState } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
    Button,
    Label,
    Input,
    Textarea,
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
    Spinner,
} from '@/components/ui';
import { Upload, FileText } from 'lucide-react';

interface UploadVersionDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    documentId: string;
    onSuccess: () => void;
}

export default function UploadVersionDialog({
    open,
    onOpenChange,
    documentId,
    onSuccess,
}: UploadVersionDialogProps) {
    const [file, setFile] = useState<File | null>(null);
    const [changeNote, setChangeNote] = useState('');
    const [bumpType, setBumpType] = useState('patch');
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setError(null);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a file');
            return;
        }

        setIsUploading(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('file', file);

            // Append other fields as query params to the URL or formData depending on API
            // API routes.py: 
            // @router.post("/documents/{document_id}/versions")
            // file: UploadFile = File(...), change_note: str = "", bump_type: str = Query(...)
            // So change_note is form field, bump_type is query param (or form if supported)
            // But FastAPI handles mixed form/query. Let's try appending to URL for query params.

            const url = new URL(`/api/dm/documents/${documentId}/versions`, window.location.origin);
            url.searchParams.append('bump_type', bumpType);
            url.searchParams.append('change_note', changeNote); // Wait, API signature implies query or form?
            // "change_note: str = """ (default), not Query via default.
            // Actually it's likely Form if not specified as Query explicitly in FastAPI combined with File.
            // Let's create proper multipart request.
            // Wait, looking at routes.py:
            // change_note: str = "" (param)
            // bump_type: str = Query(...)
            // If they are regular params with File, FastAPI treats simple types as Form fields usually.
            // But let's check routes.py again:
            // async def upload_version(..., file: UploadFile = File(...), change_note: str = "", bump_type: str = Query(...))
            // So `change_note` is likely expected as a query param too since it's default value constitutes a query param unless `Form` is used.
            // However, with File upload, usually non-path params are Form.
            // Let's try putting change_note in URL too to be safe, or just FormData.

            // Re-reading routes.py snippet:
            // bump_type: str = Query("patch", ...)
            // change_note: str = "" -> This defaults to Query param in FastAPI if not `Form()`.

            url.searchParams.append('change_note', changeNote);

            const response = await fetch(url.toString(), {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to upload version');
            }

            // Success
            onSuccess();
            onOpenChange(false);
            setFile(null);
            setChangeNote('');
            setBumpType('patch');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Upload New Version</DialogTitle>
                    <DialogDescription>
                        Upload a new file to update this document. Previous versions will be kept in history.
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                            {error}
                        </div>
                    )}

                    <div className="grid w-full max-w-sm items-center gap-1.5">
                        <Label htmlFor="file">File</Label>
                        <Input id="file" type="file" onChange={handleFileChange} />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="bumpType">Version Increment</Label>
                        <Select value={bumpType} onValueChange={setBumpType}>
                            <SelectTrigger>
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="patch">Patch (x.x.X) - Minor fix</SelectItem>
                                <SelectItem value="minor">Minor (x.X.x) - Feature update</SelectItem>
                                <SelectItem value="major">Major (X.x.x) - Breaking change</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="note">Change Note</Label>
                        <Textarea
                            id="note"
                            placeholder="Describe what changed in this version..."
                            value={changeNote}
                            onChange={(e) => setChangeNote(e.target.value)}
                            rows={3}
                        />
                    </div>

                    <DialogFooter>
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => onOpenChange(false)}
                        >
                            Cancel
                        </Button>
                        <Button type="submit" disabled={isUploading || !file}>
                            {isUploading ? (
                                <>
                                    <Spinner size="sm" className="mr-2" />
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <Upload className="mr-2 h-4 w-4" />
                                    Upload
                                </>
                            )}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
