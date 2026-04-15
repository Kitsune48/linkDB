import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/layout/AppLayout";
import { PrivateRoute } from "./components/routing/PrivateRoute";
import { useAuth } from "./hooks/useAuth";
import { LoginPage } from "./pages/LoginPage";
import { NewLinkPage } from "./pages/NewLinkPage";
import { ReadLaterPage } from "./pages/ReadLaterPage";
import { SearchLinksPage } from "./pages/SearchLinksPage";

function PublicRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  if (isAuthenticated) {
    return <Navigate to="/links/search" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/links/search" replace />} />
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="/links/search"
          element={
            <PrivateRoute>
              <SearchLinksPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/links/new"
          element={
            <PrivateRoute>
              <NewLinkPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/links/read-later"
          element={
            <PrivateRoute>
              <ReadLaterPage />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to="/links/search" replace />} />
      </Route>
    </Routes>
  );
}

export default App;
