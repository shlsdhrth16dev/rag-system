import { RAGInterface } from './components/RAGInterface';

function App() {
    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '100vh',
            padding: '2rem',
            background: 'radial-gradient(circle at top center, #1e293b, #0f172a)'
        }}>
            <RAGInterface />
        </div>
    );
}

export default App;
