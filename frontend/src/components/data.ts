export interface Node {
    id: string;
    label: string;
    size: number;
    color: string;
  }
  
  export interface Edge {
    source: string;
    target: string;
    id: string;
    label: string;
    color: string;
  }
  
  export interface GraphData {
    nodes: Node[];
    edges: Edge[];
  }

export const graphData: GraphData = {
  nodes: [
    { id: '1', label: 'AI', size: 15, color: '#3b82f6' },
    { id: '2', label: 'Machine Learning', size: 12, color: '#6366f1' },
    { id: '3', label: 'Deep Learning', size: 12, color: '#8b5cf6' },
    { id: '4', label: 'Neural Networks', size: 10, color: '#a78bfa' },
    { id: '5', label: 'Computer Vision', size: 10, color: '#ec4899' },
    { id: '6', label: 'Natural Language Processing', size: 10, color: '#f43f5e' },
    { id: '7', label: 'Reinforcement Learning', size: 10, color: '#10b981' }
  ],
  edges: [
    { source: '1', target: '2', id: 'e1', label: 'includes', color: '#64748b' },
    { source: '1', target: '3', id: 'e2', label: 'encompasses', color: '#64748b' },
    { source: '2', target: '4', id: 'e3', label: 'utilizes', color: '#64748b' },
    { source: '2', target: '5', id: 'e4', label: 'applies to', color: '#64748b' },
    { source: '3', target: '4', id: 'e5', label: 'based on', color: '#64748b' },
    { source: '2', target: '6', id: 'e6', label: 'enables', color: '#64748b' },
    { source: '2', target: '7', id: 'e7', label: 'incorporates', color: '#64748b' }
  ]
};