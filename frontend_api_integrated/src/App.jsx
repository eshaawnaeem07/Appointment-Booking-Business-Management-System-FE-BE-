import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import HomePage from "./pages/HomePage";
import BusinessesPage from "./pages/BusinessesPage";
import BusinessDetailPage from "./pages/BusinessDetailPage";
import AppointmentsPage from "./pages/AppointmentsPage";
import AppointmentDetailPage from "./pages/AppointmentDetailPage";
import Dashboard from "./pages/owner/Dashboard";
import ServicesManager from "./pages/owner/ServicesManager";
import BusinessCustomerList from "./components/BusinessCustomerList";
import BusinessCustomerForm from "./components/BusinessCustomerForm";
import BusinessCustomerDetail from "./components/BusinessCustomerDetail";

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      {/* User */}
      <Route path="/home" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
      <Route path="/businesses" element={<ProtectedRoute><BusinessesPage /></ProtectedRoute>} />
      <Route path="/businesses/:id" element={<ProtectedRoute><BusinessDetailPage /></ProtectedRoute>} />
      <Route path="/appointments" element={<ProtectedRoute><AppointmentsPage /></ProtectedRoute>} />
      <Route path="/appointments/:id" element={<ProtectedRoute><AppointmentDetailPage /></ProtectedRoute>} />
      <Route path="/payment/success" element={<ProtectedRoute><PaymentSuccess /></ProtectedRoute>} />
      <Route path="/payment/cancel" element={<ProtectedRoute><PaymentCancel /></ProtectedRoute>} />

      {/* Owner only */}
      <Route path="/dashboard" element={<ProtectedRoute ownerOnly><Dashboard /></ProtectedRoute>} />
      <Route path="/dashboard/services" element={<ProtectedRoute ownerOnly><ServicesManager /></ProtectedRoute>} />
      <Route path="/dashboard/hours" element={<ProtectedRoute ownerOnly><HoursManager /></ProtectedRoute>} />
      <Route path="/dashboard/appointments" element={<ProtectedRoute ownerOnly><OwnerAppointments /></ProtectedRoute>} />
      <Route path="/dashboard/customers" element={<ProtectedRoute ownerOnly><BusinessCustomerList /></ProtectedRoute>} />
      <Route path="/dashboard/customers/new" element={<ProtectedRoute ownerOnly><BusinessCustomerForm /></ProtectedRoute>} />
      <Route path="/dashboard/customers/:customerId" element={<ProtectedRoute ownerOnly><BusinessCustomerDetail /></ProtectedRoute>} />
      <Route path="/dashboard/customers/edit/:customerId" element={<ProtectedRoute ownerOnly><BusinessCustomerForm /></ProtectedRoute>} />

      <Route path="/business-customer-list" element={<ProtectedRoute><BusinessCustomerList /></ProtectedRoute>} />
      <Route path="/business-customer-form" element={<ProtectedRoute><BusinessCustomerForm /></ProtectedRoute>} />
      <Route path="/business-customer-detail/:id" element={<ProtectedRoute><BusinessCustomerDetail /></ProtectedRoute>} />

      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}