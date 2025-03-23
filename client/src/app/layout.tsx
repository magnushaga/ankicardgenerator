import { AppRouterCacheProvider } from '@mui/material-nextjs/v14-appRouter';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { theme } from '@/lib/theme';
import Navbar from '@/components/layout/Navbar';
import { Box } from '@mui/material';

export const metadata = {
  title: 'AnkiGen - Smart Flashcard Generator',
  description: 'Generate and study Anki cards from textbooks using AI',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AppRouterCacheProvider>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <Navbar />
            <Box
              component="main"
              sx={{
                minHeight: '100vh',
                pt: '64px', // Height of navbar
                background: 'linear-gradient(to bottom, #1a1a1a, #121212)',
              }}
            >
              {children}
            </Box>
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}