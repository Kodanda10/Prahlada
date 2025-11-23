import { useLocation, useNavigate } from 'react-router-dom';

export const useRouting = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const goToPage = (path: string) => {
    navigate(path);
  };

  const goBack = () => {
    navigate(-1);
  };

  const refreshPage = () => {
    window.location.reload();
  };

  return {
    currentPath: location.pathname,
    goToPage,
    goBack,
    refreshPage
  };
};