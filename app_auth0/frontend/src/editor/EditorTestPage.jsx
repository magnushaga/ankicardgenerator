import React, { useState } from 'react';
import { Box, Container, Typography, Button, Paper, Alert, Stack } from '@mui/material';
import { HierarchicalEditor } from './index';

// Sample hierarchical data - in a real app this would come from your API
const sampleSections = [
  {
    id: 'section1',
    name: 'Introduction to Algorithms',
    chapterId: 'chapter1',
    chapterName: 'Fundamentals',
    partId: 'part1',
    partName: 'Computer Science Basics',
  },
  {
    id: 'section2',
    name: 'Big O Notation',
    chapterId: 'chapter1',
    chapterName: 'Fundamentals',
    partId: 'part1',
    partName: 'Computer Science Basics',
  },
  {
    id: 'section3',
    name: 'Algorithm Analysis',
    chapterId: 'chapter1',
    chapterName: 'Fundamentals',
    partId: 'part1',
    partName: 'Computer Science Basics',
  },
  {
    id: 'section4',
    name: 'Sorting Algorithms',
    chapterId: 'chapter2',
    chapterName: 'Algorithm Design',
    partId: 'part1',
    partName: 'Computer Science Basics',
  },
  {
    id: 'section5',
    name: 'Merge Sort',
    chapterId: 'chapter2',
    chapterName: 'Algorithm Design',
    partId: 'part1',
    partName: 'Computer Science Basics',
  },
  {
    id: 'section6',
    name: 'Quick Sort',
    chapterId: 'chapter2',
    chapterName: 'Algorithm Design',
    partId: 'part1',
    partName: 'Computer Science Basics',
  },
  {
    id: 'section7',
    name: 'Data Structures Overview',
    chapterId: 'chapter3',
    chapterName: 'Data Structures',
    partId: 'part2',
    partName: 'Advanced Topics',
  },
  {
    id: 'section8',
    name: 'Linked Lists',
    chapterId: 'chapter3',
    chapterName: 'Data Structures',
    partId: 'part2',
    partName: 'Advanced Topics',
  },
  {
    id: 'section9',
    name: 'Trees and Graphs',
    chapterId: 'chapter3',
    chapterName: 'Data Structures',
    partId: 'part2',
    partName: 'Advanced Topics',
  },
];

// Sample initial content for the editor
const sampleContent = `
<h1>Computer Science Basics</h1>
<p>This textbook covers fundamental concepts in computer science.</p>

<h2>Fundamentals</h2>
<p>The foundation of computer science begins with understanding algorithms and their analysis.</p>

<h3>Introduction to Algorithms</h3>
<p>An algorithm is a step-by-step procedure for solving a problem. Algorithms are the building blocks of computer programs.</p>

<h3>Big O Notation</h3>
<p>Big O notation is used to classify algorithms according to how their run time or space requirements grow as the input size grows.</p>

<h3>Algorithm Analysis</h3>
<p>Algorithm analysis involves determining the resources (such as time and storage) necessary to execute it.</p>

<h2>Algorithm Design</h2>
<p>Techniques for designing efficient algorithms that solve complex problems.</p>

<h3>Sorting Algorithms</h3>
<p>Sorting algorithms arrange elements in a specific order, usually numerical or lexicographical.</p>

<h3>Merge Sort</h3>
<p>Merge sort is an efficient, stable, comparison-based, divide-and-conquer sorting algorithm.</p>

<h3>Quick Sort</h3>
<p>Quick sort is a highly efficient sorting algorithm that uses a divide-and-conquer strategy.</p>

<h1>Advanced Topics</h1>
<p>Once you understand the basics, we can move on to more complex topics.</p>

<h2>Data Structures</h2>
<p>Data structures are ways of organizing and storing data so that they can be accessed and modified efficiently.</p>

<h3>Data Structures Overview</h3>
<p>Understanding the different types of data structures and when to use them.</p>

<h3>Linked Lists</h3>
<p>A linked list is a linear data structure where each element points to the next.</p>

<h3>Trees and Graphs</h3>
<p>Trees and graphs are non-linear data structures that represent hierarchical relationships.</p>
`;

const EditorTestPage = () => {
  const [content, setContent] = useState(sampleContent);
  
  // Handler for content changes
  const handleContentChange = (html) => {
    setContent(html);
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 2 }}>
        Hierarchical Editor Demo
      </Typography>
      
      <Stack spacing={2} sx={{ mb: 3 }}>
        <Alert severity="info">
          <strong>New Features:</strong>
          <ul>
            <li>Click the toggle button to hide/show the table of contents sidebar</li>
            <li>Click on any section heading (h3) in the editor to highlight it in the sidebar</li>
            <li>Dark/light theme support based on your application theme</li>
            <li>Auto-tracking of your position while scrolling through content</li>
          </ul>
        </Alert>
      </Stack>
      
      <Paper sx={{ p: 0, height: 'calc(100vh - 230px)', overflow: 'hidden' }}>
        <HierarchicalEditor 
          sections={sampleSections}
          content={content}
          onChange={handleContentChange}
        />
      </Paper>
      
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button 
          variant="contained" 
          onClick={() => console.log('Content saved:', content)}
        >
          Save Content
        </Button>
      </Box>
    </Container>
  );
};

export default EditorTestPage; 