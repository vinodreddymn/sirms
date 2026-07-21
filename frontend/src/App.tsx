import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import { Login } from './features/auth/Login';
import { Dashboard } from './features/dashboard/Dashboard';
import { AssetList } from './features/assets/AssetList';
import { AssetDetailsPage } from './features/assets/AssetDetails';
import { AssetMovementsPage } from './features/assets/AssetMovementsPage';
import { IncidentList } from './features/incidents/IncidentList';
import { IncidentDetails } from './features/incidents/IncidentDetails';
import { StockTransactions } from './features/stock/StockTransactions';
import { LookupsList } from './features/master/LookupsList';
import { SpecificationDefinitions } from './features/master/SpecificationDefinitions';
import { PositionTemplates } from './features/master/PositionTemplates';
import { LocationsTree } from './features/infrastructure/LocationsTree';
import { MaintenanceStub } from './features/maintenance/MaintenanceStub';
import { DailyWorkLog } from './features/dailywork/DailyWorkLog';
import { Reports } from './features/reports/Reports';
import { ToastProvider } from './contexts/ToastContext';

// Basic Auth Guard
const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = !!localStorage.getItem('access_token');
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

function App() {
  return (
    <ToastProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route path="/" element={<PrivateRoute><MainLayout /></PrivateRoute>}>
            <Route index element={<Dashboard />} />
            <Route path="master" element={<LookupsList />} />
            <Route path="master/specifications" element={<SpecificationDefinitions />} />
            <Route path="master/position-templates" element={<PositionTemplates />} />
            <Route path="assets" element={<AssetList />} />
            <Route path="asset-movements" element={<AssetMovementsPage />} />
            <Route path="assets/:id" element={<AssetDetailsPage />} />
            <Route path="incidents" element={<IncidentList />} />
            <Route path="incidents/:id" element={<IncidentDetails />} />
            <Route path="maintenance" element={<MaintenanceStub />} />
            <Route path="daily-work-log" element={<DailyWorkLog />} />
            <Route path="reports" element={<Reports />} />
            <Route path="stock" element={<StockTransactions />} />
            <Route path="infrastructure" element={<LocationsTree />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ToastProvider>
  );
}

export default App;
