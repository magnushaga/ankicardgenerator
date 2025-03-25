import React, { useState } from 'react';
import {
  Box,
  List,
  ListItem,
  Typography,
  Paper,
  Collapse,
  Button,
  ButtonGroup
} from '@mui/material';

interface TreeNode {
  id: number;
  title: string;
  children?: TreeNode[];
  type: 'part' | 'chapter' | 'topic';
}

interface DeckTreeProps {
  data: TreeNode[];
}

const TreeItem: React.FC<{ node: TreeNode; depth: number }> = ({ node, depth }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const hasChildren = node.children && node.children.length > 0;

  const getIndentation = () => `${depth * 20}px`;
  
  const getBackgroundColor = () => {
    switch (node.type) {
      case 'part': return '#f5f5f5';
      case 'chapter': return '#fafafa';
      case 'topic': return 'white';
      default: return 'white';
    }
  };

  return (
    <>
      <ListItem 
        sx={{
          pl: getIndentation(),
          py: 1,
          borderLeft: '1px solid #eee',
          cursor: hasChildren ? 'pointer' : 'default',
          bgcolor: getBackgroundColor(),
          '&:hover': {
            bgcolor: hasChildren ? '#eeeef0' : getBackgroundColor(),
          },
          borderBottom: '1px solid #eee',
          minHeight: '48px'
        }}
        onClick={() => hasChildren && setIsExpanded(!isExpanded)}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
          {hasChildren && (
            <Typography sx={{ mr: 1, color: '#666' }}>
              {isExpanded ? '▼' : '►'}
            </Typography>
          )}
          <Typography 
            variant={depth === 0 ? 'subtitle1' : 'body1'}
            sx={{ 
              fontWeight: depth === 2 ? 'normal' : 'medium',
              color: node.type === 'topic' ? '#666' : 'inherit'
            }}
          >
            {node.title}
          </Typography>
        </Box>
      </ListItem>
      
      {hasChildren && (
        <Collapse in={isExpanded}>
          <List disablePadding>
            {node.children.map((child) => (
              <TreeItem 
                key={child.id} 
                node={child} 
                depth={depth + 1} 
              />
            ))}
          </List>
        </Collapse>
      )}
    </>
  );
};

const DeckTree: React.FC<DeckTreeProps> = ({ data }) => {
  const [allExpanded, setAllExpanded] = useState(false);

  const handleExpandAll = () => {
    setAllExpanded(!allExpanded);
  };

  return (
    <Paper elevation={0} sx={{ maxWidth: 800, mx: 'auto', mt: 2 }}>
      <Box sx={{ p: 2, borderBottom: '1px solid #eee' }}>
        <ButtonGroup size="small" sx={{ mb: 2 }}>
          <Button 
            onClick={handleExpandAll}
            sx={{ 
              bgcolor: '#f5f5f5',
              '&:hover': { bgcolor: '#e0e0e0' }
            }}
          >
            {allExpanded ? 'Collapse All' : 'Expand All'}
          </Button>
        </ButtonGroup>
      </Box>
      <List disablePadding>
        {data.map((node) => (
          <TreeItem key={node.id} node={node} depth={0} />
        ))}
      </List>
    </Paper>
  );
};

export default DeckTree; 