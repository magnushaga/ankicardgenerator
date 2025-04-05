import React, { useState, useEffect, useRef } from 'react';
import { Box, Divider, Typography, Paper, Tabs, Tab, IconButton, Tooltip } from '@mui/material';
import { useTheme } from '../lib/ThemeContext';
import { TipTapEditor } from './index';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';

/**
 * HierarchicalEditor - A component that combines a section navigator with TipTap editor
 * 
 * @param {Object[]} sections - Array of section objects with hierarchical info
 * @param {string} content - HTML content for the editor
 * @param {function} onChange - Callback when content changes
 */
const HierarchicalEditor = ({ sections = [], content = '', onChange }) => {
  const [currentSection, setCurrentSection] = useState(null);
  const [activePath, setActivePath] = useState({ partId: '', chapterId: '', sectionId: '' });
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const editorRef = useRef(null);
  const { isDarkMode } = useTheme();
  
  // Group sections by parts and chapters for navigation
  const hierarchy = sections.reduce((acc, section) => {
    // Initialize part if not exists
    if (!acc[section.partId]) {
      acc[section.partId] = {
        id: section.partId,
        name: section.partName,
        chapters: {}
      };
    }
    
    // Initialize chapter if not exists
    if (!acc[section.partId].chapters[section.chapterId]) {
      acc[section.partId].chapters[section.chapterId] = {
        id: section.chapterId,
        name: section.chapterName,
        sections: []
      };
    }
    
    // Add section to chapter
    acc[section.partId].chapters[section.chapterId].sections.push({
      id: section.id,
      name: section.name
    });
    
    return acc;
  }, {});
  
  // Convert hierarchy object to array for rendering
  const parts = Object.values(hierarchy);
  
  // Initialize with first section if available
  useEffect(() => {
    if (sections.length > 0 && !currentSection) {
      const firstSection = sections[0];
      setCurrentSection(firstSection);
      setActivePath({
        partId: firstSection.partId,
        chapterId: firstSection.chapterId,
        sectionId: firstSection.id
      });
    }
  }, [sections, currentSection]);
  
  // Handle selection of a section
  const handleSectionSelect = (section) => {
    setCurrentSection(section);
    setActivePath({
      partId: section.partId,
      chapterId: section.chapterId,
      sectionId: section.id
    });
    
    // Scroll to the section header in the editor
    if (editorRef.current) {
      const sectionHeader = editorRef.current.querySelector(`h3:contains("${section.name}")`);
      if (sectionHeader) {
        sectionHeader.scrollIntoView({ behavior: 'smooth' });
      } else {
        // Use a more flexible approach with textContent comparison
        const h3Elements = editorRef.current.querySelectorAll('h3');
        for (const h3 of h3Elements) {
          if (h3.textContent.trim() === section.name.trim()) {
            h3.scrollIntoView({ behavior: 'smooth' });
            break;
          }
        }
      }
    }
  };
  
  // Track scroll position to update active section
  const handleEditorScroll = (e) => {
    const editorElement = e.target;
    const headings = editorElement.querySelectorAll('h1, h2, h3');
    
    // Find which heading is currently at the top of the viewport
    let activeHeading = null;
    let minDistance = Infinity;
    
    headings.forEach(heading => {
      const rect = heading.getBoundingClientRect();
      const distance = Math.abs(rect.top);
      
      if (distance < minDistance) {
        minDistance = distance;
        activeHeading = heading;
      }
    });
    
    if (activeHeading) {
      // Determine the level and text of the heading
      const level = activeHeading.tagName.charAt(1);
      const text = activeHeading.textContent;
      
      // Update active path based on heading level
      if (level === '1') { // Part level
        const part = parts.find(p => p.name === text);
        if (part) {
          setActivePath(prev => ({ ...prev, partId: part.id }));
        }
      } else if (level === '2') { // Chapter level
        let foundChapter = null;
        let foundPart = null;
        
        parts.forEach(part => {
          Object.values(part.chapters).forEach(chapter => {
            if (chapter.name === text) {
              foundChapter = chapter;
              foundPart = part;
            }
          });
        });
        
        if (foundChapter && foundPart) {
          setActivePath(prev => ({ 
            ...prev, 
            partId: foundPart.id, 
            chapterId: foundChapter.id 
          }));
        }
      } else if (level === '3') { // Section level
        // Find the section that matches this heading
        for (const part of parts) {
          for (const chapter of Object.values(part.chapters)) {
            const section = chapter.sections.find(s => s.name === text);
            if (section) {
              setActivePath({
                partId: part.id,
                chapterId: chapter.id,
                sectionId: section.id
              });
              
              // Also update current section for the editor context
              const fullSection = sections.find(s => s.id === section.id);
              if (fullSection) {
                setCurrentSection(fullSection);
              }
              
              return; // Exit once found
            }
          }
        }
      }
    }
  };
  
  // Create click handlers for headings inside the editor
  const handleEditorHeadingClick = (event) => {
    // Make sure it's a heading element
    const heading = event.target.closest('h1, h2, h3');
    if (!heading) return;
    
    const level = heading.tagName.charAt(1);
    const text = heading.textContent;
    
    if (level === '3') {
      // Find the section that matches this heading
      for (const part of parts) {
        for (const chapter of Object.values(part.chapters)) {
          const section = chapter.sections.find(s => s.name === text);
          if (section) {
            // Update UI to reflect the section
            setActivePath({
              partId: part.id,
              chapterId: chapter.id,
              sectionId: section.id
            });
            
            // Also update current section for the editor context
            const fullSection = sections.find(s => s.id === section.id);
            if (fullSection) {
              setCurrentSection(fullSection);
            }
            
            // Show sidebar if it's not already visible
            if (!sidebarOpen) {
              setSidebarOpen(true);
            }
            
            return;
          }
        }
      }
    }
  };

  // Add click event listener to the editor when mounted or when sections change
  useEffect(() => {
    const editorElement = editorRef.current;
    if (editorElement) {
      editorElement.addEventListener('click', handleEditorHeadingClick);
      
      return () => {
        editorElement.removeEventListener('click', handleEditorHeadingClick);
      };
    }
  }, [sections, parts]);
  
  const nodeInfo = currentSection ? {
    path: [
      parts.find(p => p.id === activePath.partId)?.name || '',
      Object.values(hierarchy[activePath.partId]?.chapters || {}).find(c => c.id === activePath.chapterId)?.name || '',
      currentSection.name
    ],
    section: currentSection
  } : null;
  
  return (
    <Box sx={{ 
      display: 'flex', 
      height: '100%',
      bgcolor: isDarkMode ? 'background.paper' : '#fff',
      color: isDarkMode ? 'text.primary' : 'text.primary',
      position: 'relative'
    }}>
      {/* Toggle Button for closed sidebar */}
      {!sidebarOpen && (
        <Box sx={{ 
          position: 'absolute', 
          top: 10, 
          left: 10, 
          zIndex: 10 
        }}>
          <Tooltip title="Show table of contents">
            <IconButton 
              onClick={() => setSidebarOpen(true)}
              sx={{ 
                bgcolor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)',
                '&:hover': {
                  bgcolor: isDarkMode ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.08)'
                }
              }}
            >
              <MenuIcon />
            </IconButton>
          </Tooltip>
        </Box>
      )}
      
      {/* Navigation sidebar */}
      <Box sx={{ 
        width: sidebarOpen ? 280 : 0,
        borderRight: '1px solid', 
        borderColor: 'divider',
        overflowY: 'auto',
        overflowX: 'hidden',
        p: sidebarOpen ? 2 : 0,
        transition: 'width 0.2s, padding 0.2s',
        position: 'relative',
        flexShrink: 0
      }}>
        {sidebarOpen && (
          <>
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              mb: 2
            }}>
              <Typography variant="subtitle1" fontWeight="bold">
                Table of Contents
              </Typography>
              <Tooltip title="Hide sidebar">
                <IconButton 
                  size="small" 
                  onClick={() => setSidebarOpen(false)}
                  sx={{ 
                    color: 'text.secondary',
                    '&:hover': {
                      color: 'text.primary'
                    }
                  }}
                >
                  <ChevronLeftIcon />
                </IconButton>
              </Tooltip>
            </Box>
            
            {parts.map(part => (
              <Box key={part.id} sx={{ mb: 3 }}>
                <Typography 
                  variant="subtitle1" 
                  sx={{ 
                    fontWeight: 600,
                    mb: 1.5,
                    color: activePath.partId === part.id ? 'primary.main' : 'inherit'
                  }}
                >
                  {part.name}
                </Typography>
                
                {Object.values(part.chapters).map(chapter => (
                  <Box key={chapter.id} sx={{ ml: 1, mb: 2 }}>
                    <Typography 
                      variant="subtitle2" 
                      sx={{ 
                        fontWeight: 500,
                        mb: 1,
                        color: activePath.chapterId === chapter.id ? 'primary.main' : 'inherit'
                      }}
                    >
                      {chapter.name}
                    </Typography>
                    
                    {chapter.sections.map(section => (
                      <Typography
                        key={section.id}
                        variant="body2"
                        sx={{
                          ml: 1.5,
                          mb: 0.75,
                          py: 0.5,
                          pl: 1,
                          borderRadius: 1,
                          cursor: 'pointer',
                          bgcolor: activePath.sectionId === section.id ? 
                            (isDarkMode ? 'action.selected' : 'rgba(25, 118, 210, 0.08)') : 
                            'transparent',
                          color: activePath.sectionId === section.id ? 'primary.main' : 'inherit',
                          '&:hover': {
                            bgcolor: isDarkMode ? 'action.hover' : 'rgba(0, 0, 0, 0.04)'
                          }
                        }}
                        onClick={() => {
                          const fullSection = sections.find(s => s.id === section.id);
                          if (fullSection) {
                            handleSectionSelect(fullSection);
                          }
                        }}
                      >
                        {section.name}
                      </Typography>
                    ))}
                  </Box>
                ))}
                <Divider sx={{ my: 2 }} />
              </Box>
            ))}
          </>
        )}
      </Box>
      
      {/* Editor area */}
      <Box 
        sx={{ 
          flex: 1, 
          overflow: 'auto', 
          p: 2,
          pb: 20, // Add padding at bottom for comfortable editing
        }}
        onScroll={handleEditorScroll}
        ref={editorRef}
      >
        <TipTapEditor 
          content={content}
          onChange={onChange}
          nodeInfo={nodeInfo}
        />
      </Box>
    </Box>
  );
};

export default HierarchicalEditor; 