import React, { useState, useRef, useEffect } from 'react';
import { useEditor, EditorContent, Extension } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Highlight from '@tiptap/extension-highlight';
import Typography from '@tiptap/extension-typography';
import Image from '@tiptap/extension-image';
import Link from '@tiptap/extension-link';
import Placeholder from '@tiptap/extension-placeholder';
import { 
  Box, 
  Button, 
  ButtonGroup, 
  Divider, 
  IconButton, 
  Tooltip, 
  Menu, 
  MenuItem, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  TextField,
  Typography as MuiTypography,
  alpha
} from '@mui/material';
import { useTheme as useCustomTheme } from '../lib/ThemeContext';

// Icons
import FormatBoldIcon from '@mui/icons-material/FormatBold';
import FormatItalicIcon from '@mui/icons-material/FormatItalic';
import FormatUnderlinedIcon from '@mui/icons-material/FormatUnderlined';
import FormatStrikethroughIcon from '@mui/icons-material/FormatStrikethrough';
import FormatQuoteIcon from '@mui/icons-material/FormatQuote';
import CodeIcon from '@mui/icons-material/Code';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered';
import ImageIcon from '@mui/icons-material/Image';
import AddLinkIcon from '@mui/icons-material/AddLink';
import UndoIcon from '@mui/icons-material/Undo';
import RedoIcon from '@mui/icons-material/Redo';
import TextFieldsIcon from '@mui/icons-material/TextFields';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import CheckIcon from '@mui/icons-material/Check';
import AddIcon from '@mui/icons-material/Add';

// Custom extension to hold textbook node information
const TextbookNodeExtension = Extension.create({
  name: 'textbookNode',
  
  addOptions() {
    return {
      nodeInfo: null
    };
  },
  
  addStorage() {
    return {
      nodeInfo: this.options.nodeInfo
    };
  }
});

// Notion-style Menu Bar component
const NotionMenuBar = ({ editor, nodeInfo }) => {
  const [imageUrl, setImageUrl] = useState('');
  const [imageDialogOpen, setImageDialogOpen] = useState(false);
  const [linkUrl, setLinkUrl] = useState('');
  const [linkDialogOpen, setLinkDialogOpen] = useState(false);
  const [headingMenuAnchor, setHeadingMenuAnchor] = useState(null);
  const [addMenuAnchor, setAddMenuAnchor] = useState(null);
  const { isDarkMode } = useCustomTheme();
  
  if (!editor) {
    return null;
  }
  
  const handleImageSubmit = () => {
    if (imageUrl) {
      editor.chain().focus().setImage({ src: imageUrl }).run();
      setImageUrl('');
      setImageDialogOpen(false);
    }
  };
  
  const handleLinkSubmit = () => {
    if (linkUrl) {
      editor.chain().focus().setLink({ href: linkUrl }).run();
      setLinkUrl('');
      setLinkDialogOpen(false);
    }
  };
  
  const headingOptions = [
    { title: 'Normal text', value: 0 },
    { title: 'Heading 1', value: 1 },
    { title: 'Heading 2', value: 2 },
    { title: 'Heading 3', value: 3 }
  ];
  
  const getCurrentHeadingOption = () => {
    if (editor.isActive('heading', { level: 1 })) return headingOptions[1];
    if (editor.isActive('heading', { level: 2 })) return headingOptions[2];
    if (editor.isActive('heading', { level: 3 })) return headingOptions[3];
    return headingOptions[0];
  };
  
  const currentHeading = getCurrentHeadingOption();
  
  return (
    <React.Fragment>
      {/* Floating menu that appears on selection - Notion style */}
      <Box
        sx={{
          display: editor.isActive('paragraph') || editor.isActive('heading') ? 'flex' : 'none',
          alignItems: 'center',
          position: 'fixed',
          top: -9999, // Positioned by JS
          left: -9999, // Positioned by JS
          zIndex: 50,
          borderRadius: 1,
          boxShadow: '0 0 0 1px rgba(15, 15, 15, 0.05), 0 3px 6px rgba(15, 15, 15, 0.1), 0 9px 24px rgba(15, 15, 15, 0.2)',
          bgcolor: isDarkMode ? 'background.default' : 'background.paper',
          py: 0.5,
          px: 0.5,
          opacity: 0, // Hidden by default, shown on selection
          transform: 'scale(0.95)',
          transition: 'opacity 150ms ease, transform 150ms ease',
          '&.is-active': {
            opacity: 1,
            transform: 'scale(1)'
          }
        }}
        className="floating-menu"
        ref={(element) => {
          if (!element || !editor.view || !editor.view.dom) return;
          
          // This updates the position of the floating menu based on text selection
          const updateMenuPosition = () => {
            const { from, to } = editor.view.state.selection;
            if (from === to) {
              element.style.opacity = 0;
              element.classList.remove('is-active');
              return;
            }
            
            const view = editor.view;
            const { top, left, height } = view.coordsAtPos(from);
            
            element.style.top = `${top - height - element.offsetHeight - 10}px`;
            element.style.left = `${left}px`;
            element.style.opacity = 1;
            element.classList.add('is-active');
          };
          
          editor.on('selectionUpdate', updateMenuPosition);
          updateMenuPosition();
        }}
      >
        <ButtonGroup variant="text" size="small">
          <IconButton 
            size="small" 
            onClick={() => editor.chain().focus().toggleBold().run()}
            sx={{ 
              color: editor.isActive('bold') ? 'primary.main' : 'text.primary',
              p: 0.5
            }}
          >
            <FormatBoldIcon fontSize="small" />
          </IconButton>
          <IconButton 
            size="small" 
            onClick={() => editor.chain().focus().toggleItalic().run()}
            sx={{ 
              color: editor.isActive('italic') ? 'primary.main' : 'text.primary',
              p: 0.5
            }}
          >
            <FormatItalicIcon fontSize="small" />
          </IconButton>
          <IconButton 
            size="small" 
            onClick={() => editor.chain().focus().toggleStrike().run()}
            sx={{ 
              color: editor.isActive('strike') ? 'primary.main' : 'text.primary',
              p: 0.5
            }}
          >
            <FormatStrikethroughIcon fontSize="small" />
          </IconButton>
          <IconButton 
            size="small" 
            onClick={() => editor.chain().focus().toggleCode().run()}
            sx={{ 
              color: editor.isActive('code') ? 'primary.main' : 'text.primary',
              p: 0.5
            }}
          >
            <CodeIcon fontSize="small" />
          </IconButton>
          <IconButton 
            size="small" 
            onClick={() => editor.chain().focus().toggleCodeBlock().run()}
            sx={{ 
              color: editor.isActive('codeBlock') ? 'primary.main' : 'text.primary',
              p: 0.5
            }}
          >
            <CodeIcon fontSize="small" />
          </IconButton>
          <IconButton 
            size="small" 
            onClick={() => setLinkDialogOpen(true)}
            sx={{ p: 0.5 }}
          >
            <AddLinkIcon fontSize="small" />
          </IconButton>
        </ButtonGroup>
      </Box>
      
      {/* Main toolbar - Notion style */}
      <Box 
        sx={{ 
          mb: 1.5, 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: 0.5,
          position: 'sticky',
          top: 0,
          bgcolor: isDarkMode ? 'background.paper' : 'background.default',
          zIndex: 1,
          pt: 2,
          pb: 1
        }}
      >
        {/* Text formatting section */}
        <ButtonGroup 
          variant="text" 
          size="small"
          sx={{ 
            mr: 1,
            '& .MuiButtonGroup-grouped': {
              borderColor: 'transparent'
            }
          }}
        >
          <Button
            onClick={(e) => setHeadingMenuAnchor(e.currentTarget)}
            size="small"
            startIcon={<TextFieldsIcon fontSize="small" />}
            endIcon={<KeyboardArrowDownIcon fontSize="small" />}
            sx={{ 
              textTransform: 'none', 
              color: 'text.secondary',
              fontWeight: 'normal',
              px: 1,
              py: 0.5,
              minWidth: 0
            }}
          >
            {currentHeading.title}
          </Button>
          <Menu
            anchorEl={headingMenuAnchor}
            open={Boolean(headingMenuAnchor)}
            onClose={() => setHeadingMenuAnchor(null)}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'left',
            }}
          >
            {headingOptions.map((option) => (
              <MenuItem 
                key={option.value}
                onClick={() => {
                  if (option.value === 0) {
                    editor.chain().focus().setParagraph().run();
                  } else {
                    editor.chain().focus().toggleHeading({ level: option.value }).run();
                  }
                  setHeadingMenuAnchor(null);
                }}
                sx={{ 
                  px: 2, 
                  py: 1,
                  display: 'flex',
                  alignItems: 'center',
                  fontSize: option.value === 0 ? 14 : option.value === 1 ? 18 : option.value === 2 ? 16 : 14,
                  fontWeight: option.value === 0 ? 'normal' : 'bold',
                  color: 'text.primary',
                  '&:hover': {
                    bgcolor: alpha('#000', 0.04)
                  }
                }}
              >
                <Box sx={{ width: 24, display: 'flex', alignItems: 'center' }}>
                  {editor.isActive('heading', { level: option.value }) && (
                    <CheckIcon fontSize="small" sx={{ color: 'primary.main' }} />
                  )}
                </Box>
                {option.title}
              </MenuItem>
            ))}
          </Menu>
        </ButtonGroup>
        
        <ButtonGroup 
          variant="text" 
          size="small"
          sx={{ 
            mr: 1,
            '& .MuiButtonGroup-grouped': {
              borderColor: 'transparent'
            }
          }}
        >
          <Tooltip title="Bold">
            <IconButton
              onClick={() => editor.chain().focus().toggleBold().run()}
              sx={{ 
                color: editor.isActive('bold') ? 'primary.main' : 'text.secondary',
                p: 0.5
              }}
            >
              <FormatBoldIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Italic">
            <IconButton
              onClick={() => editor.chain().focus().toggleItalic().run()}
              sx={{ 
                color: editor.isActive('italic') ? 'primary.main' : 'text.secondary',
                p: 0.5
              }}
            >
              <FormatItalicIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Underline">
            <IconButton
              // Note: Underline is not included in StarterKit
              // This is just a placeholder - you'd need to add the extension
              onClick={() => {}}
              sx={{ 
                color: 'text.secondary',
                p: 0.5
              }}
            >
              <FormatUnderlinedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Strikethrough">
            <IconButton
              onClick={() => editor.chain().focus().toggleStrike().run()}
              sx={{ 
                color: editor.isActive('strike') ? 'primary.main' : 'text.secondary',
                p: 0.5
              }}
            >
              <FormatStrikethroughIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </ButtonGroup>
        
        <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        
        <ButtonGroup 
          variant="text" 
          size="small"
          sx={{ 
            mr: 1,
            '& .MuiButtonGroup-grouped': {
              borderColor: 'transparent'
            }
          }}
        >
          <Tooltip title="Bullet List">
            <IconButton
              onClick={() => editor.chain().focus().toggleBulletList().run()}
              sx={{ 
                color: editor.isActive('bulletList') ? 'primary.main' : 'text.secondary',
                p: 0.5
              }}
            >
              <FormatListBulletedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Numbered List">
            <IconButton
              onClick={() => editor.chain().focus().toggleOrderedList().run()}
              sx={{ 
                color: editor.isActive('orderedList') ? 'primary.main' : 'text.secondary',
                p: 0.5
              }}
            >
              <FormatListNumberedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Quote">
            <IconButton
              onClick={() => editor.chain().focus().toggleBlockquote().run()}
              sx={{ 
                color: editor.isActive('blockquote') ? 'primary.main' : 'text.secondary',
                p: 0.5
              }}
            >
              <FormatQuoteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Code Block">
            <IconButton
              onClick={() => editor.chain().focus().toggleCodeBlock().run()}
              sx={{ 
                color: editor.isActive('codeBlock') ? 'primary.main' : 'text.secondary',
                p: 0.5
              }}
            >
              <CodeIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </ButtonGroup>
        
        <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        
        <ButtonGroup 
          variant="text" 
          size="small"
          sx={{ 
            mr: 1,
            '& .MuiButtonGroup-grouped': {
              borderColor: 'transparent'
            }
          }}
        >
          <Button
            onClick={(e) => setAddMenuAnchor(e.currentTarget)}
            size="small"
            startIcon={<AddIcon fontSize="small" />}
            endIcon={<KeyboardArrowDownIcon fontSize="small" />}
            sx={{ 
              textTransform: 'none', 
              color: 'text.secondary',
              fontWeight: 'normal',
              px: 1,
              py: 0.5
            }}
          >
            Add
          </Button>
          <Menu
            anchorEl={addMenuAnchor}
            open={Boolean(addMenuAnchor)}
            onClose={() => setAddMenuAnchor(null)}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'left',
            }}
          >
            <MenuItem 
              onClick={() => {
                setAddMenuAnchor(null);
                setImageDialogOpen(true);
              }}
              sx={{ px: 2, py: 1 }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <ImageIcon fontSize="small" sx={{ mr: 1.5, color: 'text.secondary' }} />
                <span>Image</span>
              </Box>
            </MenuItem>
            <MenuItem 
              onClick={() => {
                setAddMenuAnchor(null);
                setLinkDialogOpen(true);
              }}
              sx={{ px: 2, py: 1 }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <AddLinkIcon fontSize="small" sx={{ mr: 1.5, color: 'text.secondary' }} />
                <span>Link</span>
              </Box>
            </MenuItem>
          </Menu>
        </ButtonGroup>
        
        <Box sx={{ flexGrow: 1 }} />
        
        <ButtonGroup 
          variant="text" 
          size="small"
          sx={{ 
            '& .MuiButtonGroup-grouped': {
              borderColor: 'transparent'
            }
          }}
        >
          <Tooltip title="Undo">
            <IconButton
              onClick={() => editor.chain().focus().undo().run()}
              disabled={!editor.can().undo()}
              sx={{ 
                color: 'text.secondary',
                p: 0.5
              }}
            >
              <UndoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Redo">
            <IconButton
              onClick={() => editor.chain().focus().redo().run()}
              disabled={!editor.can().redo()}
              sx={{ 
                color: 'text.secondary',
                p: 0.5
              }}
            >
              <RedoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </ButtonGroup>
      </Box>
      
      {/* Node path display */}
      {nodeInfo && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            mb: 1.5,
            py: 0.5,
            px: 1,
            borderRadius: 1,
            bgcolor: isDarkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(55, 53, 47, 0.08)',
            color: isDarkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(55, 53, 47, 0.65)',
            fontSize: '0.75rem'
          }}
        >
          <MuiTypography variant="caption">
            {nodeInfo.path.join(' / ')}
          </MuiTypography>
        </Box>
      )}
      
      {/* Image Dialog */}
      <Dialog open={imageDialogOpen} onClose={() => setImageDialogOpen(false)}>
        <DialogTitle>Insert Image</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="image-url"
            label="Image URL"
            type="url"
            fullWidth
            variant="outlined"
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImageDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleImageSubmit} variant="contained">Insert</Button>
        </DialogActions>
      </Dialog>
      
      {/* Link Dialog */}
      <Dialog open={linkDialogOpen} onClose={() => setLinkDialogOpen(false)}>
        <DialogTitle>Insert Link</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="link-url"
            label="URL"
            type="url"
            fullWidth
            variant="outlined"
            value={linkUrl}
            onChange={(e) => setLinkUrl(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLinkDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleLinkSubmit} variant="contained">Insert</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
};

const TipTapEditor = ({ content = '', onChange, nodeInfo = null }) => {
  const { isDarkMode } = useCustomTheme();
  
  const editor = useEditor({
    extensions: [
      StarterKit,
      Highlight,
      Typography,
      Image,
      Link.configure({
        openOnClick: false,
      }),
      Placeholder.configure({
        placeholder: 'Write something...',
      }),
      TextbookNodeExtension.configure({
        nodeInfo: nodeInfo
      })
    ],
    content,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });
  
  // Update the nodeInfo in the extension when it changes
  useEffect(() => {
    if (editor && nodeInfo) {
      editor.extensionManager.extensions.find(
        extension => extension.name === 'textbookNode'
      ).storage.nodeInfo = nodeInfo;
    }
  }, [editor, nodeInfo]);

  return (
    <Box sx={{
      position: 'relative',
      '& .ProseMirror': {
        outline: 'none',
        minHeight: '60vh',
        color: isDarkMode ? '#e0e0e0' : '#37352f',
        backgroundColor: isDarkMode ? '#121212' : '#fff',
        fontSize: '16px',
        lineHeight: 1.6,
        '& p:first-of-type': {
          marginTop: 0,
        },
        '& > * + *': {
          marginTop: '0.75em',
        },
        '& ul, & ol': {
          padding: '0 1rem'
        },
        '& blockquote': {
          paddingLeft: '1rem',
          borderLeft: '3px solid',
          borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.2)' : '#ddd',
          color: isDarkMode ? 'rgba(255, 255, 255, 0.6)' : 'rgba(55, 53, 47, 0.6)',
          fontStyle: 'italic'
        },
        '& code': {
          backgroundColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(135, 131, 120, 0.15)',
          color: isDarkMode ? '#ff6b6b' : '#eb5757',
          borderRadius: '3px',
          padding: '0.2em 0.4em'
        },
        '& pre': {
          background: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(135, 131, 120, 0.15)',
          borderRadius: '0.5em',
          color: isDarkMode ? '#e0e0e0' : '#37352f',
          fontFamily: '"JetBrainsMono", monospace',
          padding: '0.75em 1em',
          '& code': {
            backgroundColor: 'transparent',
            color: 'inherit',
            padding: 0
          }
        },
        '& img': {
          maxWidth: '100%',
          height: 'auto',
          borderRadius: '4px'
        },
        '& a': {
          color: isDarkMode ? '#90caf9' : '#2D7FF9',
          textDecoration: 'underline',
        },
        '& h1': {
          fontSize: '1.875em',
          color: isDarkMode ? '#fff' : '#37352f',
          fontWeight: 600,
          lineHeight: 1.3,
          marginTop: '1.4em',
          marginBottom: '0.5em'
        },
        '& h2': {
          fontSize: '1.5em',
          color: isDarkMode ? '#fff' : '#37352f',
          fontWeight: 600,
          lineHeight: 1.3,
          marginTop: '1.4em',
          marginBottom: '0.5em'
        },
        '& h3': {
          fontSize: '1.25em',
          color: isDarkMode ? '#fff' : '#37352f',
          fontWeight: 600,
          lineHeight: 1.3, 
          marginTop: '1em',
          marginBottom: '0.5em'
        },
        '& p.is-editor-empty:first-of-type::before': {
          color: isDarkMode ? 'rgba(255, 255, 255, 0.4)' : '#adb5bd',
          content: 'attr(data-placeholder)',
          float: 'left',
          height: 0,
          pointerEvents: 'none'
        }
      }
    }}>
      <NotionMenuBar editor={editor} nodeInfo={nodeInfo} />
      <EditorContent editor={editor} />
    </Box>
  );
};

export default TipTapEditor;