import React from 'react';
import { Card, CardContent, CardHeader, Box, Typography, Chip, Skeleton, Button, Divider, Stack, List, ListItem, ListItemText, ListItemIcon, LinearProgress } from '@mui/material';
import { Description as DocumentIcon, Download as DownloadIcon, FolderOpen as FolderIcon, TrendingUp, Error as ErrorIcon } from '@mui/icons-material';

interface DocumentStatsProps {
    projectId: string;
}

interface StatsData {
    project_id: string;
    total_documents: number;
    by_status: Record<string, number>;
    by_type: Record<string, number>;
    total_versions: number;
}

interface RecentDocument {
    id: string;
    title: string;
    document_number: string | null;
    status: string;
    updated_at: string;
}

const statusColors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'> = {
    DRAFT: 'default',
    IN_REVIEW: 'info',
    APPROVED: 'success',
    PUBLISHED: 'primary',
    ARCHIVED: 'warning',
    REJECTED: 'error',
};

/**
 * Document Manager widget for PM Project Dashboard.
 * Shows document stats and recent documents for quick access.
 */
export const ProjectDocumentsWidget: React.FC<DocumentStatsProps> = ({ projectId }) => {
    const [stats, setStats] = React.useState<StatsData | null>(null);
    const [recentDocs, setRecentDocs] = React.useState<RecentDocument[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);

    React.useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);

                // Fetch stats
                const statsRes = await fetch(`/api/dm/projects/${projectId}/stats`);
                if (statsRes.ok) {
                    setStats(await statsRes.json());
                }

                // Fetch recent documents
                const recentRes = await fetch(`/api/dm/projects/${projectId}/recent?limit=5`);
                if (recentRes.ok) {
                    const data = await recentRes.json();
                    setRecentDocs(data.documents || []);
                }

                setError(null);
            } catch (err) {
                setError('Failed to load document data');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        if (projectId) {
            fetchData();
        }
    }, [projectId]);

    const handleExport = async () => {
        window.open(`/api/dm/projects/${projectId}/export`, '_blank');
    };

    if (loading) {
        return (
            <Card>
                <CardHeader title="Documents" />
                <CardContent>
                    <Skeleton variant="rectangular" height={150} />
                </CardContent>
            </Card>
        );
    }

    if (error) {
        return (
            <Card>
                <CardHeader title="Documents" />
                <CardContent>
                    <Box display="flex" alignItems="center" gap={1} color="error.main">
                        <ErrorIcon />
                        <Typography>{error}</Typography>
                    </Box>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader
                title="Documents"
                action={
                    <Button
                        size="small"
                        startIcon={<DownloadIcon />}
                        onClick={handleExport}
                        disabled={!stats || stats.total_documents === 0}
                    >
                        Export ZIP
                    </Button>
                }
            />
            <CardContent>
                {/* Stats Overview */}
                {stats && (
                    <Box mb={2}>
                        <Stack direction="row" spacing={2} mb={2}>
                            <Box textAlign="center" flex={1}>
                                <Typography variant="h4" color="primary">
                                    {stats.total_documents}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Documents
                                </Typography>
                            </Box>
                            <Box textAlign="center" flex={1}>
                                <Typography variant="h4" color="secondary">
                                    {stats.total_versions}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Versions
                                </Typography>
                            </Box>
                        </Stack>

                        {/* Status breakdown */}
                        {Object.entries(stats.by_status).length > 0 && (
                            <Box>
                                <Typography variant="caption" color="text.secondary" gutterBottom>
                                    By Status
                                </Typography>
                                <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                                    {Object.entries(stats.by_status).map(([status, count]) => (
                                        <Chip
                                            key={status}
                                            label={`${status}: ${count}`}
                                            size="small"
                                            color={statusColors[status] || 'default'}
                                            variant="outlined"
                                        />
                                    ))}
                                </Stack>
                            </Box>
                        )}
                    </Box>
                )}

                <Divider sx={{ my: 2 }} />

                {/* Recent Documents */}
                <Typography variant="subtitle2" gutterBottom>
                    Recent Documents
                </Typography>

                {recentDocs.length === 0 ? (
                    <Box textAlign="center" py={2} color="text.secondary">
                        <FolderIcon sx={{ fontSize: 40, opacity: 0.5 }} />
                        <Typography variant="body2">No documents yet</Typography>
                    </Box>
                ) : (
                    <List dense disablePadding>
                        {recentDocs.map((doc) => (
                            <ListItem
                                key={doc.id}
                                sx={{ px: 0, cursor: 'pointer' }}
                                onClick={() => window.location.href = `/dm/documents/${doc.id}`}
                            >
                                <ListItemIcon sx={{ minWidth: 32 }}>
                                    <DocumentIcon fontSize="small" />
                                </ListItemIcon>
                                <ListItemText
                                    primary={doc.title}
                                    secondary={doc.document_number}
                                    primaryTypographyProps={{ variant: 'body2', noWrap: true }}
                                    secondaryTypographyProps={{ variant: 'caption' }}
                                />
                                <Chip
                                    label={doc.status}
                                    size="small"
                                    color={statusColors[doc.status] || 'default'}
                                    sx={{ ml: 1 }}
                                />
                            </ListItem>
                        ))}
                    </List>
                )}

                {recentDocs.length > 0 && (
                    <Box textAlign="center" mt={1}>
                        <Button
                            size="small"
                            href={`/dm/documents?project=${projectId}`}
                        >
                            View All Documents
                        </Button>
                    </Box>
                )}
            </CardContent>
        </Card>
    );
};

export default ProjectDocumentsWidget;
