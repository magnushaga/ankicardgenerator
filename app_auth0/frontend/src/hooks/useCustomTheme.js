import { useTheme } from '@mui/material/styles';

export const useCustomTheme = () => {
  const theme = useTheme();
  return { theme };
}; 