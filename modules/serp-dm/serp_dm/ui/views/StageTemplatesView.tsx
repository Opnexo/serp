
import React, { useState, useEffect } from 'react';
import {
    Button,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
    Input,
    Modal,
    ModalContent,
    ModalHeader,
    ModalTitle,
    ModalFooter,
    Label,
    Checkbox,
} from '@/components/ui';
import { Plus, Edit, Trash2, ArrowUp, ArrowDown, Save, GitPullRequest } from 'lucide-react';


interface StageTemplateItem {
    id: string; // temporary ID for new items
    name: string;
    description: string;
    order: number;
    color: string;
}

interface StageTemplate {
    id: string;
    name: string;
    description: string;
    is_default: boolean;
    is_active: boolean;
    stage_count: number;
    created_at: string;
}

const COLORS = [
    '#6B7280', // Gray
    '#EF4444', // Red
    '#F59E0B', // Yellow
    '#10B981', // Green
    '#3B82F6', // Blue
    '#6366F1', // Indigo
    '#8B5CF6', // Purple
    '#EC4899', // Pink
];

export const StageTemplatesView: React.FC = () => {

    const [templates, setTemplates] = useState<StageTemplate[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [editingTemplate, setEditingTemplate] = useState<StageTemplate | null>(null);

    // Form state
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        is_default: false,
    });
    const [stages, setStages] = useState<StageTemplateItem[]>([]);

    useEffect(() => {
        loadTemplates();
    }, []);

    const loadTemplates = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('/api/dm/admin/stage-templates');
            if (response.ok) {
                const data = await response.json();
                setTemplates(data);
            }
        } catch (error) {
            console.error('Failed to load templates:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreate = () => {
        setEditingTemplate(null);
        setFormData({ name: '', description: '', is_default: false });
        setStages([
            { id: '1', name: 'Draft', description: 'Initial draft', order: 0, color: '#6B7280' },
            { id: '2', name: 'In Review', description: 'Under review', order: 1, color: '#F59E0B' },
            { id: '3', name: 'Approved', description: 'Approved for use', order: 2, color: '#10B981' },
            { id: '4', name: 'Archived', description: 'No longer active', order: 3, color: '#6B7280' },
        ]);
        setIsDialogOpen(true);
    };

    const handleEdit = async (template: StageTemplate) => {
        setEditingTemplate(template);
        setFormData({
            name: template.name,
            description: template.description || '',
            is_default: template.is_default,
        });

        // Fetch stages for this template
        try {
            const response = await fetch(`/api/dm/admin/stage-templates/${template.id}/items`);
            if (response.ok) {
                const data = await response.json();
                setStages(data.map((item: any) => ({
                    id: item.id, // Or generate temp ID if backend doesn't return
                    name: item.name,
                    description: item.description,
                    order: item.order,
                    color: item.color,
                })));
                setIsDialogOpen(true);
            }
        } catch (error) {
            console.error('Failed to load template stages', error);
        }
    };

    const handleSave = async () => {
        try {
            const payload = {
                ...formData,
                stages: stages.map(s => ({
                    name: s.name,
                    description: s.description,
                    order: s.order,
                    color: s.color,
                })),
            };

            let response;
            if (editingTemplate) {
                // TODO: Update endpoint not implemented yet on backend?
                // response = await fetch(`/api/dm/admin/stage-templates/${editingTemplate.id}`, {
                //     method: 'PUT',
                //     headers: { 'Content-Type': 'application/json' },
                //     body: JSON.stringify(payload)
                // });
            } else {
                response = await fetch('/api/dm/admin/stage-templates', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            }

            if (response && response.ok) {
                setIsDialogOpen(false);
                loadTemplates();
            }
        } catch (error) {
            console.error('Failed to save template', error);
        }
    };

    const addStage = () => {
        const newStage: StageTemplateItem = {
            id: crypto.randomUUID(),
            name: 'New Stage',
            description: '',
            order: stages.length,
            color: '#6B7280',
        };
        setStages([...stages, newStage]);
    };

    const updateStage = (id: string, field: keyof StageTemplateItem, value: any) => {
        setStages(stages.map(s => s.id === id ? { ...s, [field]: value } : s));
    };

    const removeStage = (id: string) => {
        setStages(stages.filter(s => s.id !== id));
    };

    const moveStage = (index: number, direction: 'up' | 'down') => {
        if (direction === 'up' && index === 0) return;
        if (direction === 'down' && index === stages.length - 1) return;

        const newStages = [...stages];
        const swapIndex = direction === 'up' ? index - 1 : index + 1;
        [newStages[index], newStages[swapIndex]] = [newStages[swapIndex], newStages[index]];

        // Re-assign order
        newStages.forEach((s, idx) => s.order = idx);
        setStages(newStages);
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Workflow Templates</h2>
                    <p className="text-muted-foreground">Manage Kanban workflow templates for projects.</p>
                </div>
                <Button onClick={handleCreate}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Template
                </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {templates.map(template => (
                    <Card key={template.id} className="hover:bg-accent/5 transition-colors">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-lg font-medium">
                                {template.name}
                            </CardTitle>
                            <GitPullRequest className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-sm text-muted-foreground mb-4 h-10 line-clamp-2">
                                {template.description || "No description"}
                            </div>
                            <div className="flex justify-between items-center">
                                <div className="text-sm font-medium">
                                    {template.stage_count} stages
                                </div>
                                <div className="space-x-2">
                                    <Button variant="ghost" size="sm" onClick={() => handleEdit(template)}>
                                        <Edit className="h-4 w-4" />
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <Modal open={isDialogOpen} onClose={() => setIsDialogOpen(false)}>
                <ModalContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                    <ModalHeader>
                        <ModalTitle>{editingTemplate ? 'Edit Template' : 'Create Workflow Template'}</ModalTitle>
                    </ModalHeader>

                    <div className="grid gap-6 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="name">Template Name</Label>
                            <Input
                                id="name"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                placeholder="e.g. Software Development Workflow"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="desc">Description</Label>
                            <Input
                                id="desc"
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                placeholder="Brief description of when to use this workflow"
                            />
                        </div>
                        <div className="flex items-center space-x-2">
                            <Checkbox
                                id="default"
                                checked={formData.is_default}
                                onChange={(c) => setFormData({ ...formData, is_default: c })}
                            />
                            <Label htmlFor="default">Set as default workflow for new projects</Label>
                        </div>

                        <div className="space-y-4">
                            <div className="flex justify-between items-center">
                                <h4 className="font-semibold">Workflow Stages</h4>
                                <Button size="sm" variant="outline" onClick={addStage}>
                                    <Plus className="mr-2 h-4 w-4" /> Add Stage
                                </Button>
                            </div>

                            <div className="border rounded-md">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead className="w-12">#</TableHead>
                                            <TableHead>Stage Name</TableHead>
                                            <TableHead>Color</TableHead>
                                            <TableHead className="w-[100px]">Actions</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {stages.map((stage, index) => (
                                            <TableRow key={stage.id}>
                                                <TableCell>{index + 1}</TableCell>
                                                <TableCell>
                                                    <Input
                                                        value={stage.name}
                                                        onChange={(e) => updateStage(stage.id, 'name', e.target.value)}
                                                        className="h-8"
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <div className="flex gap-1">
                                                        {COLORS.map(c => (
                                                            <div
                                                                key={c}
                                                                className={`w-6 h-6 rounded-full cursor-pointer border-2 ${stage.color === c ? 'border-primary' : 'border-transparent'}`}
                                                                style={{ backgroundColor: c }}
                                                                onClick={() => updateStage(stage.id, 'color', c)}
                                                            />
                                                        ))}
                                                    </div>
                                                </TableCell>
                                                <TableCell>
                                                    <div className="flex gap-1">
                                                        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => moveStage(index, 'up')} disabled={index === 0}>
                                                            <ArrowUp className="h-4 w-4" />
                                                        </Button>
                                                        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => moveStage(index, 'down')} disabled={index === stages.length - 1}>
                                                            <ArrowDown className="h-4 w-4" />
                                                        </Button>
                                                        <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive" onClick={() => removeStage(stage.id)}>
                                                            <Trash2 className="h-4 w-4" />
                                                        </Button>
                                                    </div>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </div>
                        </div>
                    </div>

                    <ModalFooter>
                        <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                        <Button onClick={handleSave}>
                            <Save className="mr-2 h-4 w-4" />
                            Save Template
                        </Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </div>
    );
};

export default StageTemplatesView;
