import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import './RAGInterface.css';

interface Source {
    content: string;
    source: string;
    score: number;
}

interface QueryResponse {
    answer: string;
    sources: Source[];
    tokens_used: number;
}

export const RAGInterface: React.FC = () => {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState<QueryResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [stats, setStats] = useState<{ total_documents: number; embedding_model: string } | null>(null);
    const [uploading, setUploading] = useState(false);

    // Fetch stats on mount
    React.useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const res = await axios.get('/api/v1/rag/stats');
            setStats(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleQuery = async () => {
        if (!query.trim()) return;
        setLoading(true);
        setError(null);
        setResponse(null);

        try {
            const res = await axios.post('/api/v1/rag/query', {
                query,
                top_k: 5,
                optimize_query: true
            });
            setResponse(res.data);
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || 'Something went wrong');
        }
        setLoading(false);
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') handleQuery();
    };

    const [isDragging, setIsDragging] = useState(false);

    const handleFileUpload = async (files: FileList | null) => {
        if (!files?.length) return;

        setUploading(true);
        setError(null);
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        try {
            await axios.post('/api/v1/rag/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            // Refresh stats after upload
            await fetchStats();
            setQuery(''); // Optional: clear query
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || 'Upload failed');
        }
        setUploading(false);
    };

    const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        handleFileUpload(e.target.files);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        handleFileUpload(e.dataTransfer.files);
    };

    return (
        <div className="rag-container">
            <motion.div
                className="rag-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <header className="rag-header">
                    <h1>AI Knowledge Base</h1>
                    <p>Supercharged RAG System</p>

                    {stats && (
                        <motion.div
                            className="stats-badge"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                        >
                            <span>📚 {stats.total_documents} Documents</span>
                            <span>⚡ {stats.embedding_model}</span>
                        </motion.div>
                    )}
                </header>

                <div className="upload-section">
                    <label
                        className={`upload-zone ${uploading ? 'uploading' : ''} ${isDragging ? 'dragging' : ''}`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        <input
                            type="file"
                            multiple
                            accept=".pdf,.txt"
                            onChange={onFileChange}
                            disabled={uploading}
                            style={{ display: 'none' }}
                        />
                        <div className="upload-content">
                            {uploading ? (
                                <span className="loader-small"></span>
                            ) : (
                                <>
                                    <span>{isDragging ? 'Drop Files Here' : 'Drag & Drop or Click to Upload'}</span>
                                    <small>PDF, TXT supported</small>
                                </>
                            )}
                        </div>
                    </label>
                </div>

                <div className="input-group">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={handleKeyPress}
                        placeholder="Ask anything..."
                        className="rag-input"
                        disabled={loading}
                    />
                    <button
                        onClick={handleQuery}
                        disabled={loading || !query.trim()}
                        className="rag-button"
                    >
                        {loading ? <span className="loader"></span> : 'Send'}
                    </button>
                </div>

                {error && (
                    <motion.div
                        className="error-message"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        {error}
                    </motion.div>
                )}

                <AnimatePresence>
                    {response && (
                        <motion.div
                            className="response-area"
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                        >
                            <div className="answer-box">
                                <div className="label">AI Answer</div>
                                <div className="content">{response.answer}</div>
                                <div className="meta">Tokens: {response.tokens_used}</div>
                            </div>

                            {response.sources.length > 0 && (
                                <div className="sources-list">
                                    <div className="label">Sources</div>
                                    <div className="scroll-row">
                                        {response.sources.map((src, i) => (
                                            <motion.div
                                                key={i}
                                                className="source-card"
                                                initial={{ opacity: 0, x: 20 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: i * 0.1 }}
                                            >
                                                <div className="source-header">
                                                    <span className="doc-name">{src.source}</span>
                                                    <span className="score">{(src.score * 100).toFixed(0)}% Match</span>
                                                </div>
                                                <p>{src.content}</p>
                                            </motion.div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </div>
    );
};
